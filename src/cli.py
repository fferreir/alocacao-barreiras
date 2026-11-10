"""
Interface de Linha de Comando (CLI) para Alocação Ótima de Barreiras Sanitárias com Teorema Min-Cut / Max-Flow.
"""
import argparse
import sys
import os
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
from src.core.optimizer import allocate_barriers_min_cut, allocate_barriers, compare_allocation_strategies
from src.core.sensitivity import run_sensitivity_analysis
from src.visualization.map_builder import build_interactive_map
from src.visualization.plots import plot_sensitivity_curves, plot_barrier_classes
from src.export.exporter import export_analysis_results

console = Console()
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(
        description="Alocação Ótima de Barreiras Sanitárias com Teorema do Min-Cut / Max-Flow e Solução Geométrica."
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Caminho do arquivo espacial de propriedades (Shapefile, GeoPackage, GeoJSON)."
    )
    parser.add_argument(
        "--foco-col", "-f",
        default="foco",
        help="Nome da coluna indicadora de foco (padrão: 'foco')."
    )
    parser.add_argument(
        "--buffer-km", "-b",
        type=float,
        default=3.0,
        help="Raio base do buffer em km (padrão: 3.0 km)."
    )
    parser.add_argument(
        "--tolerance-km", "-t",
        type=float,
        default=1.0,
        help="Tolerância da banda espacial em km para busca de entroncamentos ótimos (padrão: 1.0 km)."
    )
    parser.add_argument(
        "--method", "-m",
        default="min-cut",
        choices=["min-cut", "mincut", "geometric", "geom"],
        help="Estratégia de alocação para saída principal: 'min-cut' (Min-Cut Híbrido) ou 'geometric' (Geométrica Convencional). Padrão: 'min-cut'."
    )
    parser.add_argument(
        "--cut-mode", "-c",
        default="hybrid",
        choices=["hybrid", "junctions", "edges", "geometric"],
        help="Modo do algoritmo: 'hybrid' (padrão), 'junctions', 'edges' ou 'geometric'."
    )
    parser.add_argument(
        "--sensitivity", "-s",
        action="store_true",
        help="Executar análise de sensibilidade e trade-off variando o raio do buffer."
    )
    parser.add_argument(
        "--radii",
        type=float,
        nargs="+",
        default=None,
        help="Lista explícita de raios (km) para análise de sensibilidade (ex: --radii 3.0 5.0 7.0 10.0)."
    )
    parser.add_argument(
        "--buffer-min",
        type=float,
        default=3.0,
        help="Raio mínimo para sensibilidade em km (padrão: 3.0 km)."
    )
    parser.add_argument(
        "--buffer-max",
        type=float,
        default=10.0,
        help="Raio máximo para sensibilidade em km (padrão: 10.0 km)."
    )
    parser.add_argument(
        "--buffer-step",
        type=float,
        default=2.0,
        help="Passo do raio para sensibilidade em km (padrão: 2.0 km)."
    )
    parser.add_argument(
        "--network-type",
        type=str,
        default="all",
        choices=["drive", "all", "drive_service", "all_private"],
        help="Tipo de malha viária a ser extraída (default: all)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Diretório de saída (padrão: 'output')."
    )
    
    args = parser.parse_args()

    # Normalizar método escolhido
    method = "geometric" if (args.method in ["geometric", "geom"] or args.cut_mode == "geometric") else "min-cut"
    cut_mode = "geometric" if method == "geometric" else args.cut_mode

    console.print(Panel.fit(
        "[bold cyan]🛡️ SISTEMA DE ALOCAÇÃO ÓTIMA DE BARREIRAS SANITÁRIAS RURAIS[/bold cyan]\n"
        "[white]Comparativo Geométrica Convencional vs. Teorema Min-Cut / Max-Flow Híbrido[/white]",
        border_style="cyan"
    ))

    # 1. Carregar dados
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task1 = progress.add_task("[yellow]Carregando e validando propriedades...", total=None)
        try:
            properties_gdf = load_properties(args.input, foco_col=args.foco_col)
            progress.update(task1, description=f"[green]Propriedades carregadas: {len(properties_gdf)} registros.")
        except Exception as e:
            console.print(f"[bold red]Erro ao carregar dados:[/bold red] {e}")
            sys.exit(1)

    total_focos = (properties_gdf[args.foco_col] == 1).sum()
    console.print(
        f"📍 Total de propriedades: [bold]{len(properties_gdf)}[/bold] | "
        f"Focos ativos: [bold red]{total_focos}[/bold red] | "
        f"Saída selecionada: [bold cyan]{'Geométrica Convencional' if method == 'geometric' else 'Min-Cut Híbrido'}[/bold cyan]"
    )

    if total_focos == 0:
        console.print("[bold red]Nenhum foco encontrado. Encerrando.[/bold red]")
        sys.exit(0)

    os.makedirs(args.output_dir, exist_ok=True)

    # 2. Análise de Sensibilidade (se solicitada)
    sensitivity_df = None
    sensitivity_details = {}
    if args.sensitivity:
        if args.radii:
            radii = sorted(list(set(round(float(x), 2) for x in args.radii)))
        else:
            radii = []
            r = args.buffer_min
            while r <= args.buffer_max + 1e-5:
                radii.append(round(r, 2))
                r += args.buffer_step

        console.print(
            f"\n[bold yellow]🔬 Executando Análise de Sensibilidade Comparativa ({len(radii)} cenários: {radii} km com tolerância ±{args.tolerance_km:.1f}km)...[/bold yellow]"
        )
        
        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Calculando trade-offs...", total=len(radii))
            
            def on_progress(current, total, current_r):
                progress.update(task, completed=current, description=f"[cyan]Avaliando Geométrica vs. Min-Cut para buffer: {current_r:.1f} km...")
                
            sensitivity_df, sensitivity_details = run_sensitivity_analysis(
                properties_gdf,
                buffer_radii_km=radii,
                tolerance_km=args.tolerance_km,
                cut_mode=cut_mode,
                foco_col=args.foco_col,
                network_type=args.network_type,
                progress_callback=on_progress
            )

        # Exibir Tabela 3 de Sensibilidade
        table = Table(
            title="🔬 Tabela 3: Análise de Sensibilidade (Variação do Número de Postos por Raio r)",
            header_style="bold magenta"
        )
        table.add_column("Raio (r)", justify="center")
        table.add_column("Estratégia Geométrica", justify="center")
        table.add_column("Min-Cut Híbrido", justify="center", style="bold green")
        table.add_column("Redução (Geom. → Min-Cut)", justify="center", style="bold cyan")
        table.add_column("Em Entroncamentos", justify="center")
        table.add_column("Custo (Geom. → Min-Cut)", justify="center")
        table.add_column("Área Total (km²)", justify="center")
        
        for _, row in sensitivity_df.iterrows():
            n_g = int(row.get("num_barreiras_geometrico", row["num_barreiras"]))
            n_mc = int(row.get("num_barreiras_mincut", row["num_barreiras"]))
            red_p = float(row.get("reducao_pct", 0.0))
            n_j = int(row.get("barreiras_em_entroncamentos", 0))
            pct_j = float(row.get("pct_entroncamentos", 0.0))
            c_g = float(row.get("custo_geometrico", 0.0))
            c_mc = float(row.get("custo_mincut", 0.0))
            table.add_row(
                f"{row['buffer_km']:.1f} km",
                f"{n_g} postos",
                f"{n_mc} postos",
                f"{red_p:+.1f}%",
                f"{n_j} ({pct_j:.1f}%)",
                f"{c_g:.1f} → {c_mc:.1f}",
                f"{row['area_total_km2']:.2f}"
            )
        console.print(table)

        sens_plot_name = "curva_sensibilidade_geometrico.png" if method == "geometric" else "curva_sensibilidade_mincut.png"
        plot_path = os.path.join(args.output_dir, sens_plot_name)
        plot_sensitivity_curves(sensitivity_df, save_path=plot_path, recommended_radius=args.buffer_km, method=method)
        console.print(f"📊 Gráfico de sensibilidade salvo em: [bold green]{plot_path}[/bold green]")

    # 3. Execução do Cenário Selecionado e Comparação (Tabela 2)
    console.print(f"\n[bold green]🚀 Processando Cenário Piloto: Buffer = {args.buffer_km:.1f} km (Tolerância ±{args.tolerance_km:.1f} km)...[/bold green]")
    
    target_r = round(float(args.buffer_km), 2)
    if target_r in sensitivity_details:
        cached_sc = sensitivity_details[target_r]
        G = cached_sc["G"]
        edges_gdf = cached_sc["edges_gdf"]
        zones_gdf = cached_sc["zones_gdf"]
        tagged_props = cached_sc["tagged_props"]
        barriers_geom = cached_sc["barriers_geom_gdf"]
        barriers_mincut = cached_sc["barriers_mincut_gdf"]
        comparison_stats = cached_sc["comparison"]
        barriers_gdf = barriers_geom if method == "geometric" else barriers_mincut
        console.print(
            f"[green]✔ Zonas criadas: {len(zones_gdf)} cluster(s) de contenção.[/green]\n"
            f"[green]✔ Malha viária carregada: {len(G.nodes)} nós e {len(G.edges)} vias.[/green]\n"
            f"[green]✔ Otimização concluída: Geométrica = {len(barriers_geom)} postos | "
            f"Min-Cut = {len(barriers_mincut)} postos ({comparison_stats['reducao_postos_pct']:+.1f}%).[/green]"
        )
    else:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            t_buf = progress.add_task("[yellow]Gerando zonas de contenção e coalescência espacial...", total=None)
            zones_gdf, tagged_props = create_infected_zones(properties_gdf, buffer_km=args.buffer_km, foco_col=args.foco_col)
            progress.update(t_buf, description=f"[green]Zonas criadas: {len(zones_gdf)} cluster(s) de contenção.")

            t_osm = progress.add_task("[yellow]Baixando malha viária OpenStreetMap...", total=None)
            G, edges_gdf, _ = download_road_network(zones_gdf, network_type=args.network_type, buffer_margin_km=args.tolerance_km + 3.0)
            progress.update(t_osm, description=f"[green]Malha viária carregada: {len(G.nodes)} nós e {len(G.edges)} vias.")

            t_opt = progress.add_task("[yellow]Avaliando solução Geométrica Convencional e Min-Cut Híbrido...", total=None)
            comp_res = compare_allocation_strategies(
                G=G,
                edges_gdf=edges_gdf,
                properties_gdf=properties_gdf,
                zones_gdf=zones_gdf,
                buffer_km=args.buffer_km,
                tolerance_km=args.tolerance_km,
                cut_mode=cut_mode,
                foco_col=args.foco_col
            )
            barriers_geom = comp_res["barriers_geom"]
            barriers_mincut = comp_res["barriers_mincut"]
            comparison_stats = comp_res["comparison"]
            barriers_gdf = barriers_geom if method == "geometric" else barriers_mincut
            progress.update(
                t_opt,
                description=(
                    f"[green]Otimização concluída: Geométrica = {len(barriers_geom)} postos | "
                    f"Min-Cut = {len(barriers_mincut)} postos ({comparison_stats['reducao_postos_pct']:+.1f}%)."
                )
            )

    # 3.1. Exibir Tabela 2: Indicadores de Desempenho Computacional e Logístico
    g_st = comparison_stats["geometric"]
    m_st = comparison_stats["mincut"]
    t2 = Table(
        title=f"📊 Tabela 2: Indicadores de Desempenho Computacional e Logístico (r = {args.buffer_km:.1f} km)",
        header_style="bold cyan"
    )
    t2.add_column("Métrica de Avaliação", justify="left", style="bold")
    t2.add_column("Geométrica Convencional", justify="center")
    t2.add_column("Min-Cut Híbrido (Proposto)", justify="center", style="bold green")
    t2.add_row(
        "Total de Postos Físicos Exigidos",
        str(g_st["total_postos"]),
        f"{m_st['total_postos']} ({comparison_stats['reducao_postos_pct']:+.1f}%)"
    )
    t2.add_row(
        "Postos em Entroncamentos Estratégicos",
        str(g_st["postos_entroncamentos"]),
        f"{m_st['postos_entroncamentos']} ({m_st['pct_entroncamentos']:.1f}%)"
    )
    t2.add_row(
        "Custo Logístico Ponderado (∑ capacidades)",
        f"{g_st['custo_logistico']:.1f}",
        f"{m_st['custo_logistico']:.1f} ({comparison_stats['reducao_custo_pct']:+.1f}%)"
    )
    t2.add_row(
        "Tempo de Processamento Computacional",
        f"≈ {g_st['tempo_processamento_s']:.2f} s",
        f"≈ {m_st['tempo_processamento_s']:.2f} s"
    )
    t2.add_row(
        "Conectividade Residual Origem-Destino",
        g_st["conectividade_residual"],
        m_st["conectividade_residual"]
    )
    t2.add_row(
        "Hermeticidade Topológica (Reachability)",
        f"{int(g_st['hermeticidade_topologica_pct'])}%",
        f"{int(m_st['hermeticidade_topologica_pct'])}%"
    )
    console.print(t2)

    # 4. Tabela de Bloqueios Alocados (Solução Selecionada)
    if not barriers_gdf.empty:
        b_table = Table(
            title=f"🛑 Postos de Bloqueio Alocados ({'Geométrica' if method == 'geometric' else 'Min-Cut Híbrido'} | Buffer = {args.buffer_km:.1f} km)",
            header_style="bold red"
        )
        b_table.add_column("ID", justify="center", style="bold")
        b_table.add_column("Zona", justify="center")
        b_table.add_column("Tipo de Posto", justify="left")
        b_table.add_column("Local / Entroncamento", justify="left")
        b_table.add_column("Classificação", justify="left")
        b_table.add_column("Capacidade", justify="center")
        b_table.add_column("Latitude", justify="center")
        b_table.add_column("Longitude", justify="center")

        for _, brow in barriers_gdf.iterrows():
            b_table.add_row(
                brow["barrier_id"],
                brow["zone_id"],
                brow.get("barrier_type", "Bloqueio"),
                brow["road_name"],
                brow["road_class"],
                f"{float(brow.get('capacity', 1.0)):.1f}",
                f"{brow['latitude']:.5f}",
                f"{brow['longitude']:.5f}"
            )
        console.print(b_table)

    # 5. Gerar Mapa Interativo e Gráficos
    map_filename = "mapa_bloqueios_geometrico.html" if method == "geometric" else "mapa_bloqueios_mincut.html"
    map_html_path = os.path.join(args.output_dir, map_filename)
    build_interactive_map(
        properties_gdf=tagged_props,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        edges_gdf=edges_gdf,
        foco_col=args.foco_col,
        save_html_path=map_html_path,
        method=method
    )
    console.print(f"🗺️  Mapa interativo salvo em: [bold green]{map_html_path}[/bold green]")

    classes_plot_path = os.path.join(args.output_dir, "distribuicao_classes_vias.png")
    plot_barrier_classes(barriers_gdf, save_path=classes_plot_path, method=method)

    # 6. Exportar Arquivos (Shapefiles, GeoJSON, CSV e Relatório Executivo)
    exported = export_analysis_results(
        output_dir=args.output_dir,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        properties_gdf=tagged_props,
        sensitivity_df=sensitivity_df,
        buffer_km=args.buffer_km,
        edges_gdf=edges_gdf,
        comparison_stats=comparison_stats,
        barriers_geom_gdf=barriers_geom,
        barriers_mincut_gdf=barriers_mincut,
        method=method,
        tolerance_km=args.tolerance_km
    )

    console.print(Panel.fit(
        f"[bold green]✔ Alocação e Exportação Finalizadas com Sucesso![/bold green]\n"
        f"📁 Diretório: [bold]{args.output_dir}[/bold]\n"
        f"📄 Relatório Executivo: [bold]{exported.get('report_md')}[/bold]\n"
        f"🗺️  Shapefile dos Postos: [bold]{exported.get('barriers_shp')}[/bold]\n"
        f"🛣️  Shapefile das Vias: [bold]{exported.get('edges_shp')}[/bold]\n"
        f"🌐 Mapa Interativo: [bold]{map_html_path}[/bold]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
