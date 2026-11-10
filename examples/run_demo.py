"""
Demonstração comparativa: Corte Geométrico de Fronteira vs. Teorema Min-Cut / Max-Flow em Entroncamentos.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.generate_sample_data import generate_sample_properties
from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
from src.core.optimizer import allocate_barriers_min_cut, allocate_barriers, compare_allocation_strategies
from src.core.sensitivity import run_sensitivity_analysis
from src.visualization.map_builder import build_interactive_map
from src.visualization.plots import plot_sensitivity_curves, plot_barrier_classes
from src.export.exporter import export_analysis_results

def run_demo():
    print("=" * 75)
    print("DEMONSTRAÇÃO: ALOCAÇÃO ÓTIMA VIA TEOREMA MIN-CUT / MAX-FLOW (ENTRONCAMENTOS)")
    print("=" * 75)

    data_dir = "data"
    shp_path = generate_sample_properties(data_dir)
    output_dir = "output_mincut_demo"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Carregar dados
    print("\n[1/5] Carregando propriedades rurais...")
    props_gdf = load_properties(shp_path, foco_col="foco")
    num_focos = (props_gdf["foco"] == 1).sum()
    print(f" -> Total de propriedades: {len(props_gdf)} | Focos ativos: {num_focos}")

    # 2. Gerar Zonas de Contenção Base (3.0 km)
    buffer_km = 3.0
    tolerance_km = 1.0
    print(f"\n[2/5] Gerando zonas de contenção e coalescência espacial (Buffer base = {buffer_km:.1f} km)...")
    zones_gdf, tagged_props = create_infected_zones(props_gdf, buffer_km=buffer_km, foco_col="foco")
    print(f" -> Zonas geradas: {len(zones_gdf)} cluster(s) de contenção.")

    # 3. Baixar Malha Viária
    print("\n[3/5] Baixando malha viária do OpenStreetMap com margem de tolerância e ancoragem...")
    G, edges_gdf, _ = download_road_network(zones_gdf, network_type="all", buffer_margin_km=tolerance_km + 3.0)
    print(f" -> Grafo viário: {len(G.nodes)} nós e {len(G.edges)} vias.")

    # 4. Comparação: Corte de Fronteira Geométrico vs. Min-Cut Híbrido
    print("\n[4/5] Executando Otimização e Comparação de Algoritmos...")
    comp_res = compare_allocation_strategies(
        G=G,
        edges_gdf=edges_gdf,
        properties_gdf=props_gdf,
        zones_gdf=zones_gdf,
        buffer_km=buffer_km,
        tolerance_km=tolerance_km,
        cut_mode="hybrid",
        foco_col="foco"
    )
    barriers_geom = comp_res["barriers_geom"]
    barriers_mincut = comp_res["barriers_mincut"]
    comparison_stats = comp_res["comparison"]
    g_st = comparison_stats["geometric"]
    m_st = comparison_stats["mincut"]

    print(f" ⚠️  Geométrica Convencional: {g_st['total_postos']} postos | Custo: {g_st['custo_logistico']:.1f} | Tempo: {g_st['tempo_processamento_s']:.2f} s")
    print(
        f" 🎯 Min-Cut Híbrido (Proposto): {m_st['total_postos']} postos ({comparison_stats['reducao_postos_pct']:+.1f}%) | "
        f"Entroncamentos: {m_st['postos_entroncamentos']} ({m_st['pct_entroncamentos']:.1f}%) | "
        f"Custo: {m_st['custo_logistico']:.1f} ({comparison_stats['reducao_custo_pct']:+.1f}%) | "
        f"Tempo: {m_st['tempo_processamento_s']:.2f} s"
    )

    # 5. Exportação (Shapefiles, GeoJSON, CSV e Relatório Executivo) e Mapa Interativo
    print("\n[5/5] Gerando mapa interativo, Shapefiles e Relatório Executivo...")
    map_path = os.path.join(output_dir, "mapa_bloqueios_mincut.html")
    build_interactive_map(
        properties_gdf=tagged_props,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_mincut,
        edges_gdf=edges_gdf,
        foco_col="foco",
        save_html_path=map_path,
        method="min-cut"
    )

    plot_barrier_classes(
        barriers_mincut,
        save_path=os.path.join(output_dir, "distribuicao_classes_vias.png"),
        method="min-cut"
    )

    exported = export_analysis_results(
        output_dir=output_dir,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_mincut,
        properties_gdf=tagged_props,
        buffer_km=buffer_km,
        edges_gdf=edges_gdf,
        comparison_stats=comparison_stats,
        barriers_geom_gdf=barriers_geom,
        barriers_mincut_gdf=barriers_mincut,
        method="min-cut",
        tolerance_km=tolerance_km
    )

    print("\n" + "=" * 75)
    print("DEMONSTRAÇÃO MIN-CUT CONCLUÍDA COM SUCESSO!")
    print(f"Arquivos salvos em: {output_dir}/")
    print(f" - Mapa Interativo HTML: {map_path}")
    print(f" - Shapefile dos Postos: {exported.get('barriers_shp')}")
    print(f" - Shapefile das Vias:   {exported.get('edges_shp')}")
    print(f" - Relatório Executivo:  {exported['report_md']}")
    print("=" * 75)

if __name__ == "__main__":
    run_demo()
