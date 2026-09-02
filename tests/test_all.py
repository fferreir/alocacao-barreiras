"""
Suíte de testes automatizados para a aplicação de alocação de barreiras sanitárias via Min-Cut.
"""
import pytest
import os
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString, Polygon
import pandas as pd

from src.core.loader import load_properties, validate_properties, ensure_projected_crs
from src.core.buffer import create_infected_zones, tag_properties_with_zones
from src.core.optimizer import allocate_barriers, allocate_barriers_min_cut, consolidate_barrier_points
from src.core.sensitivity import run_sensitivity_analysis
from src.export.exporter import export_analysis_results
from tests.generate_sample_data import generate_sample_properties


def test_loader_and_validation():
    shp_path = generate_sample_properties("data_test")
    gdf = load_properties(shp_path, foco_col="foco")
    
    assert not gdf.empty
    assert "foco" in gdf.columns
    assert (gdf["foco"] == 1).sum() == 4
    assert gdf.crs is not None

    with pytest.raises(ValueError):
        load_properties(shp_path, foco_col="coluna_inexistente")


def test_buffer_coalescence():
    p1 = Point(-47.00, -22.00)
    p2 = Point(-47.005, -22.005)
    p3 = Point(-47.20, -22.20)
    p4 = Point(-47.01, -22.01)

    df = gpd.GeoDataFrame({
        "id": [1, 2, 3, 4],
        "foco": [1, 1, 1, 0],
        "geometry": [p1, p2, p3, p4]
    }, crs="EPSG:4326")

    zones_gdf, tagged_props = create_infected_zones(df, buffer_km=3.0, foco_col="foco")

    assert len(zones_gdf) == 2
    assert "area_km2" in zones_gdf.columns
    assert "perimeter_km" in zones_gdf.columns
    assert tagged_props["in_infected_zone"].sum() >= 3


def test_min_cut_bottleneck_graph():
    """
    Testa se o Teorema Min-Cut / Max-Flow encontra o gargalo único em vez de cortar
    múltiplas vias nas extremidades.
    
    Estrutura do Grafo:
      Foco (Nó 0)
        ├─> Nó 1 (interno) ──┐
        ├─> Nó 2 (interno) ──┼──> Nó 3 (Entroncamento/Gargalo) ──> Nó 4 (Externo) ──┬─> Nó 5 (Externo)
        └─> Nó 6 (interno) ──┘                                                      └─> Nó 7 (Externo)
    
    O Min-Cut com Vertex Splitting deve cortar exatamente o Nó 3 (1 bloqueio no entroncamento)
    em vez de múltiplos bloqueios.
    """
    G = nx.MultiDiGraph()
    # Adicionar nós com coordenadas espaciais (WGS84)
    coords = {
        0: (-47.000, -22.000), # Foco central
        1: (-47.005, -22.005), # Interno
        2: (-47.002, -22.008), # Interno
        6: (-47.008, -22.002), # Interno
        3: (-47.025, -22.025), # Entroncamento / Gargalo (~3.5 km)
        4: (-47.050, -22.050), # Externo (~7 km)
        5: (-47.060, -22.060), # Externo
        7: (-47.065, -22.055), # Externo
    }
    for n, (x, y) in coords.items():
        G.add_node(n, x=x, y=y)

    # Arestas
    edges = [
        (0, 1), (0, 2), (0, 6),
        (1, 3), (2, 3), (6, 3), # Todas convergem no Nó 3
        (3, 4),                 # Gargalo único que sai para o exterior
        (4, 5), (4, 7)          # Ramificações externas
    ]
    for u, v in edges:
        G.add_edge(u, v, highway="primary", name="Rodovia Teste")
        G.add_edge(v, u, highway="primary", name="Rodovia Teste")

    # Propriedades
    props_gdf = gpd.GeoDataFrame({
        "id": [1],
        "foco": [1],
        "geometry": [Point(-47.000, -22.000)]
    }, crs="EPSG:4326")

    zones_gdf, _ = create_infected_zones(props_gdf, buffer_km=4.0, foco_col="foco")

    barriers_gdf = allocate_barriers_min_cut(
        G=G,
        properties_gdf=props_gdf,
        zones_gdf=zones_gdf,
        buffer_km=4.0,
        tolerance_km=2.0,
        cut_mode="junctions",
        foco_col="foco"
    )

    # O corte mínimo deve resultar em apenas 1 posto no entroncamento/gargalo
    assert len(barriers_gdf) == 1


def test_exporter(tmp_path):
    shp_path = generate_sample_properties("data_test")
    gdf = load_properties(shp_path, foco_col="foco")
    zones_gdf, tagged_props = create_infected_zones(gdf, buffer_km=2.0, foco_col="foco")
    
    barriers_gdf = gpd.GeoDataFrame({
        "barrier_id": ["BLOQ_001"],
        "zone_id": ["ZONA_01"],
        "barrier_type": ["Entroncamento / Bifurcação"],
        "road_name": ["Entroncamento BR-101 e SP-304"],
        "road_class": ["Rodovia Principal"],
        "connected_roads": [3],
        "latitude": [-22.70],
        "longitude": [-47.60],
        "geometry": [Point(-47.60, -22.70)]
    }, crs="EPSG:4326")

    output_dir = str(tmp_path / "output_test")
    exported = export_analysis_results(
        output_dir=output_dir,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        properties_gdf=tagged_props,
        buffer_km=2.0
    )

    assert os.path.exists(exported["zones_geojson"])
    assert os.path.exists(exported["barriers_geojson"])
    assert os.path.exists(exported["barriers_csv"])
    assert os.path.exists(exported["report_md"])


if __name__ == "__main__":
    pytest.main(["-v", __file__])
