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
from src.core.optimizer import allocate_barriers_min_cut, allocate_barriers
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

    # 2. Gerar Zonas de Contenção Base (4.0 km)
    print("\n[2/5] Gerando zonas de contenção e coalescência espacial (Buffer base = 4.0 km)...")
    zones_gdf, tagged_props = create_infected_zones(props_gdf, buffer_km=4.0, foco_col="foco")
    print(f" -> Zonas geradas: {len(zones_gdf)} cluster(s) de contenção.")

    # 3. Baixar Malha Viária
    print("\n[3/5] Baixando malha viária do OpenStreetMap com margem de tolerância...")
    G, edges_gdf, _ = download_road_network(zones_gdf, network_type="all", buffer_margin_km=2.0)
    print(f" -> Grafo viário: {len(G.nodes)} nós e {len(G.edges)} vias.")

    # 4. Comparação: Corte de Fronteira Ingênuo vs. Min-Cut / Max-Flow
    print("\n[4/5] Executando Otimização e Comparação de Algoritmos...")
    
    # 4.1. Corte de Fronteira Clássico
    barriers_geom = allocate_barriers(edges_gdf, zones_gdf)
    print(f" ⚠️  Abordagem Geométrica de Fronteira: {len(barriers_geom)} barreiras (muito oneroso)")

    # 4.2. Teorema Min-Cut / Max-Flow em Entroncamentos (tolerância ±1.5 km)
    barriers_mincut = allocate_barriers_min_cut(
        G=G,
        properties_gdf=props_gdf,
        zones_gdf=zones_gdf,
        buffer_km=4.0,
        tolerance_km=1.5,
        cut_mode="junctions",
        foco_col="foco"
    )
    n_junctions = (barriers_mincut["barrier_type"].str.contains("Entroncamento")).sum()
    reduction_pct = ((len(barriers_geom) - len(barriers_mincut)) / len(barriers_geom)) * 100.0 if len(barriers_geom) > 0 else 0
    
    print(f" 🎯 Teorema Min-Cut / Max-Flow (Entroncamentos): {len(barriers_mincut)} barreiras ({n_junctions} em entroncamentos)")
    print(f" 🚀 Redução de esforço e custos operacionais: {reduction_pct:.1f}% de economia de postos de fiscalização!")

    print("\nPrimeiros Postos de Bloqueio Min-Cut Alocados:")
    for _, b in barriers_mincut.head(10).iterrows():
        print(f"  🛑 {b['barrier_id']} [{b['zone_id']}]: {b['road_name']} ({b['road_class']}) - Lat: {b['latitude']:.5f}, Lon: {b['longitude']:.5f}")

    # 5. Exportação e Mapa Interativo
    print("\n[5/5] Gerando mapa interativo e exportando dados...")
    map_path = os.path.join(output_dir, "mapa_bloqueios_mincut.html")
    build_interactive_map(
        properties_gdf=tagged_props,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_mincut,
        edges_gdf=edges_gdf,
        foco_col="foco",
        save_html_path=map_path
    )

    plot_barrier_classes(
        barriers_mincut,
        save_path=os.path.join(output_dir, "distribuicao_classes_vias.png")
    )

    exported = export_analysis_results(
        output_dir=output_dir,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_mincut,
        properties_gdf=tagged_props,
        buffer_km=4.0,
        edges_gdf=edges_gdf
    )

    print("\n" + "=" * 75)
    print("DEMONSTRAÇÃO MIN-CUT CONCLUÍDA COM SUCESSO!")
    print(f"Arquivos salvos em: {output_dir}/")
    print(f" - Mapa Interativo HTML: {map_path}")
    print(f" - Relatório Executivo: {exported['report_md']}")
    print("=" * 75)

if __name__ == "__main__":
    run_demo()
