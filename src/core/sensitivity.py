"""
Módulo de análise de sensibilidade e trade-off entre raio de buffer, tolerância de entroncamento e número de barreiras.
"""
from typing import List, Dict, Any, Tuple, Optional
import geopandas as gpd
import pandas as pd
import numpy as np
import logging
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
from src.core.optimizer import allocate_barriers_min_cut, allocate_barriers

logger = logging.getLogger(__name__)


def run_sensitivity_analysis(
    properties_gdf: gpd.GeoDataFrame,
    buffer_radii_km: List[float],
    tolerance_km: float = 1.0,
    cut_mode: str = "junctions",
    foco_col: str = "foco",
    network_type: str = "all",
    cached_graph: Optional[Any] = None,
    progress_callback: Optional[Any] = None
) -> Tuple[pd.DataFrame, Dict[float, Dict[str, Any]]]:
    """
    Executa varredura de sensibilidade para múltiplos raios de buffer utilizando
    o algoritmo de Min-Cut Max-Flow em entroncamentos.
    
    Args:
        properties_gdf: GeoDataFrame de propriedades rurais.
        buffer_radii_km: Lista de raios de buffer a testar (em km).
        tolerance_km: Tolerância para busca de entroncamentos em km.
        cut_mode: Modo de corte ('junctions', 'edges', 'hybrid').
        foco_col: Coluna indicadora de foco.
        network_type: Tipo de malha OSM.
        cached_graph: Grafo OSMnx pré-carregado.
        progress_callback: Callback de progresso.
        
    Returns:
        Tupla com resumo tabular e resultados detalhados por raio.
    """
    sorted_radii = sorted(list(set(buffer_radii_km)))
    max_radius = sorted_radii[-1] + tolerance_km
    
    # 1. Baixar malha viária com margem abrangendo o maior raio + tolerância
    if cached_graph is None or len(cached_graph) == 0:
        logger.info(f"Baixando malha viária cobrindo o raio máximo expandido ({max_radius:.1f} km)...")
        max_zones, _ = create_infected_zones(properties_gdf, buffer_km=max_radius, foco_col=foco_col)
        G, edges_gdf, _ = download_road_network(max_zones, network_type=network_type, buffer_margin_km=2.0)
    else:
        G = cached_graph

    results_table: List[Dict[str, Any]] = []
    detailed_results: Dict[float, Dict[str, Any]] = {}

    total_steps = len(sorted_radii)
    for i, r in enumerate(sorted_radii):
        if progress_callback:
            progress_callback(i + 1, total_steps, r)
            
        logger.info(f"Avaliando Min-Cut: Buffer = {r:.2f} km (±{tolerance_km:.1f}km) ({i+1}/{total_steps})...")
        
        # Gerar zonas
        zones_gdf, tagged_props = create_infected_zones(properties_gdf, buffer_km=r, foco_col=foco_col)
        
        # Alocar barreiras via Min-Cut Max-Flow
        barriers_gdf = allocate_barriers_min_cut(
            G=G,
            properties_gdf=properties_gdf,
            zones_gdf=zones_gdf,
            buffer_km=r,
            tolerance_km=tolerance_km,
            cut_mode=cut_mode,
            foco_col=foco_col
        )
        
        # Métricas agregadas
        total_area = zones_gdf["area_km2"].sum() if not zones_gdf.empty else 0.0
        total_barriers = len(barriers_gdf)
        num_junctions = (barriers_gdf["barrier_type"].str.contains("Entroncamento")).sum() if not barriers_gdf.empty else 0
        num_clusters = len(zones_gdf)
        num_props_affected = (tagged_props["in_infected_zone"] == True).sum()
        num_focos = (properties_gdf[foco_col] == 1).sum()

        record = {
            "buffer_km": r,
            "num_barreiras_mincut": total_barriers,
            "barreiras_em_entroncamentos": int(num_junctions),
            "area_total_km2": round(total_area, 2),
            "num_zonas_coalescidas": num_clusters,
            "propriedades_afetadas": int(num_props_affected),
            "total_focos": int(num_focos)
        }
        
        results_table.append(record)
        detailed_results[r] = {
            "zones_gdf": zones_gdf,
            "tagged_props": tagged_props,
            "barriers_gdf": barriers_gdf,
            "metrics": record
        }

    df_summary = pd.DataFrame(results_table)
    return df_summary, detailed_results
