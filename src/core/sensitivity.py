"""
Módulo de análise de sensibilidade e trade-off entre raio de buffer, tolerância de entroncamento e número de barreiras
(comparando Estratégia Geométrica Convencional vs. Min-Cut Híbrido).
"""
from typing import List, Dict, Any, Tuple, Optional
import time
import geopandas as gpd
import pandas as pd
import numpy as np
import logging
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network, ensure_edge_geometries
from src.core.optimizer import (
    allocate_barriers_min_cut,
    allocate_barriers,
    ox_gdfs_from_graph,
    compute_solution_stats
)

logger = logging.getLogger(__name__)


def run_sensitivity_analysis(
    properties_gdf: gpd.GeoDataFrame,
    buffer_radii_km: List[float],
    tolerance_km: float = 1.0,
    cut_mode: str = "hybrid",
    foco_col: str = "foco",
    network_type: str = "all",
    cached_graph: Optional[Any] = None,
    progress_callback: Optional[Any] = None
) -> Tuple[pd.DataFrame, Dict[float, Dict[str, Any]]]:
    """
    Executa varredura de sensibilidade para múltiplos raios de buffer comparando
    a Estratégia Geométrica Convencional e o Teorema Min-Cut / Max-Flow Híbrido.
    
    Args:
        properties_gdf: GeoDataFrame de propriedades rurais.
        buffer_radii_km: Lista de raios de buffer a testar (em km).
        tolerance_km: Tolerância para busca de entroncamentos em km.
        cut_mode: Modo de corte ('hybrid', 'junctions', 'edges', 'geometric').
        foco_col: Coluna indicadora de foco.
        network_type: Tipo de malha OSM.
        cached_graph: Grafo OSMnx pré-carregado.
        progress_callback: Callback de progresso.
        
    Returns:
        Tupla com resumo tabular e resultados detalhados por raio.
    """
    from shapely.geometry import Point

    sorted_radii = sorted(list(set(buffer_radii_km)))
    max_radius = sorted_radii[-1] + tolerance_km
    
    # 1. Baixar malha viária com margem abrangendo o maior raio + tolerância + 3.0 km de ancoragem externa
    if cached_graph is None or len(cached_graph) == 0:
        logger.info(f"Baixando malha viária cobrindo o raio máximo expandido ({max_radius:.1f} km + 3.0 km de ancoragem)...")
        max_zones, _ = create_infected_zones(properties_gdf, buffer_km=max_radius, foco_col=foco_col)
        G, edges_gdf, _ = download_road_network(max_zones, network_type=network_type, buffer_margin_km=3.0)
    else:
        G = cached_graph
        nodes_gdf, edges_gdf = ox_gdfs_from_graph(G)
        edges_gdf = ensure_edge_geometries(edges_gdf, nodes_gdf)

    metric_crs = properties_gdf.estimate_utm_crs() if not properties_gdf.crs.is_projected else properties_gdf.crs
    node_points_wgs = {n: Point(data["x"], data["y"]) for n, data in G.nodes(data=True)}
    node_series_proj = gpd.GeoSeries(node_points_wgs, crs="EPSG:4326").to_crs(metric_crs) if len(G) > 0 else gpd.GeoSeries([], crs=metric_crs)

    results_table: List[Dict[str, Any]] = []
    detailed_results: Dict[float, Dict[str, Any]] = {}

    mc_mode = cut_mode if cut_mode not in ["geometric", "geom"] else "hybrid"
    total_steps = len(sorted_radii)

    for i, r in enumerate(sorted_radii):
        if progress_callback:
            progress_callback(i + 1, total_steps, r)
            
        logger.info(f"Avaliando Sensibilidade: Buffer = {r:.2f} km (±{tolerance_km:.1f}km) ({i+1}/{total_steps})...")
        
        # Gerar zonas
        zones_gdf, tagged_props = create_infected_zones(properties_gdf, buffer_km=r, foco_col=foco_col)

        # Recortar o grafo para a vizinhança do raio atual (r + tolerance_km + 3.0 km de ancoragem),
        # preservando nós de borda conectados (truncate_by_edge) para equivalência com o cenário piloto
        if not zones_gdf.empty and len(G) > 0:
            zones_proj = zones_gdf.to_crs(metric_crs)
            local_poly = zones_proj.unary_union.buffer((tolerance_km + 3.0) * 1000.0)
            inside_nodes = {n for n, pt in node_series_proj.items() if local_poly.contains(pt)}
            boundary_neighbors = set()
            for u, v in G.edges():
                if u in inside_nodes and v not in inside_nodes:
                    boundary_neighbors.add(v)
                elif v in inside_nodes and u not in inside_nodes:
                    boundary_neighbors.add(u)
            local_nodes_set = inside_nodes | boundary_neighbors
            if len(local_nodes_set) > 0 and len(local_nodes_set) < len(G):
                G_r = G.subgraph(local_nodes_set).copy()
                if isinstance(edges_gdf.index, pd.MultiIndex):
                    u_vals = edges_gdf.index.get_level_values(0)
                    v_vals = edges_gdf.index.get_level_values(1)
                    edges_r = edges_gdf[u_vals.isin(local_nodes_set) & v_vals.isin(local_nodes_set)]
                else:
                    edges_r = edges_gdf
            else:
                G_r = G
                edges_r = edges_gdf
        else:
            G_r = G
            edges_r = edges_gdf
        
        # 1. Estratégia Geométrica Convencional
        t0_g = time.perf_counter()
        barriers_geom = allocate_barriers(edges_gdf=edges_r, zones_gdf=zones_gdf)
        t_geom = time.perf_counter() - t0_g
        stats_geom = compute_solution_stats(barriers_geom, elapsed_time_s=t_geom)

        # 2. Alocar barreiras via Min-Cut Max-Flow Híbrido
        t0_mc = time.perf_counter()
        barriers_mincut = allocate_barriers_min_cut(
            G=G_r,
            properties_gdf=properties_gdf,
            zones_gdf=zones_gdf,
            buffer_km=r,
            tolerance_km=tolerance_km,
            cut_mode=mc_mode,
            foco_col=foco_col
        )
        t_mc = time.perf_counter() - t0_mc
        stats_mc = compute_solution_stats(barriers_mincut, elapsed_time_s=t_mc)
        
        # Métricas agregadas
        total_area = zones_gdf["area_km2"].sum() if not zones_gdf.empty else 0.0
        n_geom = stats_geom["total_postos"]
        n_mincut = stats_mc["total_postos"]
        num_junctions = stats_mc["postos_entroncamentos"]
        pct_junctions = stats_mc["pct_entroncamentos"]
        reducao_pct = ((n_mincut - n_geom) / n_geom) * 100.0 if n_geom > 0 else 0.0

        c_geom = stats_geom["custo_logistico"]
        c_mincut = stats_mc["custo_logistico"]
        reducao_custo_pct = ((c_mincut - c_geom) / c_geom) * 100.0 if c_geom > 0 else 0.0

        num_clusters = len(zones_gdf)
        num_props_affected = (tagged_props["in_infected_zone"] == True).sum()
        num_focos = (properties_gdf[foco_col] == 1).sum()

        record = {
            "buffer_km": r,
            "num_barreiras_geometrico": int(n_geom),
            "num_barreiras_mincut": int(n_mincut),
            "num_barreiras": int(n_geom if cut_mode in ["geometric", "geom"] else n_mincut),
            "reducao_pct": round(reducao_pct, 1),
            "barreiras_em_entroncamentos": int(num_junctions),
            "pct_entroncamentos": round(pct_junctions, 1),
            "custo_geometrico": round(c_geom, 1),
            "custo_mincut": round(c_mincut, 1),
            "reducao_custo_pct": round(reducao_custo_pct, 1),
            "tempo_geometrico_s": round(t_geom, 2),
            "tempo_mincut_s": round(t_mc, 2),
            "area_total_km2": round(total_area, 2),
            "num_zonas_coalescidas": int(num_clusters),
            "propriedades_afetadas": int(num_props_affected),
            "total_focos": int(num_focos)
        }
        
        results_table.append(record)
        comparison_r = {
            "buffer_km": r,
            "tolerance_km": tolerance_km,
            "geometric": stats_geom,
            "mincut": stats_mc,
            "reducao_postos_pct": round(reducao_pct, 1),
            "reducao_custo_pct": round(reducao_custo_pct, 1)
        }
        detailed_results[r] = {
            "G": G_r,
            "edges_gdf": edges_r,
            "zones_gdf": zones_gdf,
            "tagged_props": tagged_props,
            "barriers_gdf": barriers_geom if cut_mode in ["geometric", "geom"] else barriers_mincut,
            "barriers_geom_gdf": barriers_geom,
            "barriers_mincut_gdf": barriers_mincut,
            "comparison": comparison_r,
            "metrics": record
        }

    df_summary = pd.DataFrame(results_table)
    return df_summary, detailed_results
