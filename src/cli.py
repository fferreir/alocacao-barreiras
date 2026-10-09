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
from src.core.optimizer import allocate_barriers_min_cut
from src.core.sensitivity import run_sensitivity_analysis
from src.visualization.map_builder import build_interactive_map
from src.visualization.plots import plot_sensitivity_curves, plot_barrier_classes
from src.export.exporter import export_analysis_results

console = Console()
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(
        description="Alocação Ótima de Barreiras Sanitárias com Teorema do Min-Cut / Max-Flow e Entroncamentos."
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
        default=4.0,
        help="Raio base do buffer em km (padrão: 4.0 km)."
    )
    parser.add_argument(
        "--tolerance-km", "-t",
        type=float,
        default=1.0,
        help="Tolerância da banda espacial em km para busca de entroncamentos ótimos (padrão: 1.0 km)."
    )
    parser.add_argument(
        "--cut-mode", "-c",
        default="junctions",
        choices=["junctions", "edges", "hybrid"],
        help="Modo do Teorema Min-Cut: 'junctions' (nós de entroncamento), 'edges' (arestas) ou 'hybrid' (padrão: 'junctions')."
    )
    parser.add_argument(
        "--sensitivity", "-s",
        action="store_true",
        help="Executar análise de sensibilidade e trade-off variando o raio do buffer."
    )
    parser.add_argument(
        "--buffer-min",
        type=float,
        default=2.0,
        help="Raio mínimo para sensibilidade em km (padrão: 2.0 km)."
    )
    parser.add_argument(
        "--buffer-max",
        type=float,
        default=6.0,
        help="Raio máximo para sensibilidade em km (padrão: 6.0 km)."
    )
    parser.add_argument(
        "--buffer-step",
        type=float,
        default=1.0,
        help="Passo do raio para sensibilidade em km (padrão: 1.0 km)."
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

    console.print(Panel.fit(
        "[bold cyan]🛡️ SISTEMA DE ALOCAÇÃO ÓTIMA DE BARREIRAS SANITÁRIAS RURAIS[/bold cyan]\n"
        "[white]Otimização de Gargalos & Entroncamentos via Teorema Min-Cut / Max-Flow[/white]",
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
    console.print(f"📍 Total de propriedades: [bold]{len(properties_gdf)}[/bold] | Focos ativos: [bold red]{total_focos}[/bold red]")

    if total_focos == 0:
        console.print("[bold red]Nenhum foco encontrado. Encerrando.[/bold red]")
        sys.exit(0)

    os.makedirs(args.output_dir, exist_ok=True)

    # 2. Análise de Sensibilidade (se solicitada)
    sensitivity_df = None
    if args.sensitivity:
        radii = []
        r = args.buffer_min
        while r <= args.buffer_max + 1e-5:
            radii.append(round(r, 2))
            r += args.buffer_step

        console.print(f"\n[bold yellow]🔬 Executando Análise de Sensibilidade Min-Cut ({len(radii)} cenários de {args.buffer_min}km a {args.buffer_max}km com tolerância ±{args.tolerance_km:.1f}km)...[/bold yellow]")
        
        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Calculando trade-offs...", total=len(radii))
            
            def on_progress(current, total, current_r):
                progress.update(task, completed=current, description=f"[cyan]Min-Cut para buffer: {current_r:.1f} km...")
                
            sensitivity_df, _ = run_sensitivity_analysis(
                properties_gdf,
                buffer_radii_km=radii,
                tolerance_km=args.tolerance_km,
                cut_mode=args.cut_mode,
                foco_col=args.foco_col,
                network_type=args.network_type,
                progress_callback=on_progress
            )

        # Exibir Tabela de Sensibilidade
        table = Table(title="🔬 Sensibilidade Min-Cut: Raio vs. Bloqueios em Entroncamentos", header_style="bold magenta")
        table.add_column("Raio (km)", justify="center")
        table.add_column("Nº Barreiras Ótimas", justify="center", style="bold red")
        table.add_column("Em Entroncamentos", justify="center", style="bold green")
        table.add_column("Área Total (km²)", justify="center")
        table.add_column("Zonas Coalescidas", justify="center")
        table.add_column("Propriedades Afetadas", justify="center")
        
        for _, row in sensitivity_df.iterrows():
            table.add_row(
                f"{row['buffer_km']:.1f}",
                str(int(row["num_barreiras_mincut"])),
                str(int(row["barreiras_em_entroncamentos"])),
                f"{row['area_total_km2']:.2f}",
                str(int(row["num_zonas_coalescidas"])),
                str(int(row["propriedades_afetadas"]))
            )
        console.print(table)

        plot_path = os.path.join(args.output_dir, "curva_sensibilidade_mincut.png")
        plot_sensitivity_curves(sensitivity_df, save_path=plot_path, recommended_radius=args.buffer_km)
        console.print(f"📊 Gráfico de sensibilidade salvo em: [bold green]{plot_path}[/bold green]")

    # 3. Execução do Cenário Selecionado
    console.print(f"\n[bold green]🚀 Processando Cenário Min-Cut: Buffer = {args.buffer_km:.1f} km (Tolerância ±{args.tolerance_km:.1f} km)...[/bold green]")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        t_buf = progress.add_task("[yellow]Gerando zonas de contenção e coalescência espacial...", total=None)
        zones_gdf, tagged_props = create_infected_zones(properties_gdf, buffer_km=args.buffer_km, foco_col=args.foco_col)
        progress.update(t_buf, description=f"[green]Zonas criadas: {len(zones_gdf)} cluster(s) de contenção.")

        t_osm = progress.add_task("[yellow]Baixando malha viária OpenStreetMap...", total=None)
        G, edges_gdf, _ = download_road_network(zones_gdf, network_type=args.network_type, buffer_margin_km=args.tolerance_km + 1.0)
        progress.update(t_osm, description=f"[green]Malha viária carregada: {len(G.nodes)} nós e {len(G.edges)} vias.")

        t_opt = progress.add_task("[yellow]Calculando Corte Mínimo (Min-Cut / Max-Flow)...", total=None)
        barriers_gdf = allocate_barriers_min_cut(
            G=G,
            properties_gdf=properties_gdf,
            zones_gdf=zones_gdf,
            buffer_km=args.buffer_km,
            tolerance_km=args.tolerance_km,
            cut_mode=args.cut_mode,
            foco_col=args.foco_col
        )
        progress.update(t_opt, description=f"[green]Min-Cut concluído: {len(barriers_gdf)} posto(s) estratégico(s) de bloqueio.")

    # 4. Tabela de Bloqueios Alocados
    if not barriers_gdf.empty:
        b_table = Table(title=f"🛑 Postos de Bloqueio Min-Cut Alocados (Buffer = {args.buffer_km:.1f} km)", header_style="bold red")
        b_table.add_column("ID", justify="center", style="bold")
        b_table.add_column("Zona", justify="center")
        b_table.add_column("Tipo de Posto", justify="left")
        b_table.add_column("Local / Entroncamento", justify="left")
        b_table.add_column("Classificação", justify="left")
        b_table.add_column("Latitude", justify="center")
        b_table.add_column("Longitude", justify="center")

        for _, brow in barriers_gdf.iterrows():
            b_table.add_row(
                brow["barrier_id"],
                brow["zone_id"],
                brow.get("barrier_type", "Bloqueio"),
                brow["road_name"],
                brow["road_class"],
                f"{brow['latitude']:.5f}",
                f"{brow['longitude']:.5f}"
            )
        console.print(b_table)

    # 5. Gerar Mapa Interativo e Gráficos
    map_html_path = os.path.join(args.output_dir, "mapa_bloqueios_mincut.html")
    build_interactive_map(
        properties_gdf=tagged_props,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        edges_gdf=edges_gdf,
        foco_col=args.foco_col,
        save_html_path=map_html_path
    )
    console.print(f"🗺️  Mapa interativo salvo em: [bold green]{map_html_path}[/bold green]")

    classes_plot_path = os.path.join(args.output_dir, "distribuicao_classes_vias.png")
    plot_barrier_classes(barriers_gdf, save_path=classes_plot_path)

    # 6. Exportar Arquivos
    exported = export_analysis_results(
        output_dir=args.output_dir,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        properties_gdf=tagged_props,
        sensitivity_df=sensitivity_df,
        buffer_km=args.buffer_km,
        edges_gdf=edges_gdf
    )

    console.print(Panel.fit(
        f"[bold green]✔ Alocação por Min-Cut / Max-Flow Finalizada![/bold green]\n"
        f"📁 Diretório: [bold]{args.output_dir}[/bold]\n"
        f"📄 Relatório: [bold]{exported.get('report_md')}[/bold]\n"
        f"🌐 Abra [bold]{map_html_path}[/bold] para inspecionar os entroncamentos bloqueados no mapa.",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
