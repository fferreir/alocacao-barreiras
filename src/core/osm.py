"""
Módulo para download e processamento da malha viária do OpenStreetMap via OSMnx.
"""
from typing import Tuple, Optional
import logging
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import LineString

logger = logging.getLogger(__name__)

# Configurações do OSMnx
ox.settings.log_console = False
ox.settings.use_cache = True


def download_road_network(
    zones_gdf: gpd.GeoDataFrame,
    network_type: str = "all",
    buffer_margin_km: float = 4.0,
    custom_filter: Optional[str] = None
) -> Tuple[nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Baixa a malha viária do OpenStreetMap cobrindo a extensão das zonas infectadas
    mais uma margem de segurança (banda de tolerância + ancoragem externa de 3 km).
    
    Args:
        zones_gdf: GeoDataFrame contendo os polígonos das zonas infectadas.
        network_type: Tipo de rede do OSM ('drive', 'all', 'drive_service', etc.).
        buffer_margin_km: Margem adicional ao redor da zona em quilômetros (padrão: 4.0 km = 1 km tolerância + 3 km ancoragem).
        custom_filter: Filtro Overpass customizado (opcional).
        
    Returns:
        Tupla com:
          1. Grafo NetworkX (MultiDiGraph).
          2. GeoDataFrame de arestas (edges_gdf).
          3. GeoDataFrame de nós (nodes_gdf).
    """
    # 1. Obter a união e aplicar margem na geometria projetada (UTM)
    zones_metric = zones_gdf.to_crs(zones_gdf.estimate_utm_crs())
    union_metric = zones_metric.unary_union.buffer(buffer_margin_km * 1000.0)
    
    # 2. Reprojetar o polígono expandido para WGS84 (EPSG:4326)
    bounding_polygon = gpd.GeoSeries([union_metric], crs=zones_metric.crs).to_crs(epsg=4326).iloc[0]
    
    logger.info(f"Baixando malha viária OSM (tipo: '{network_type}') para a região de estudo...")
    
    try:
        if custom_filter:
            G = ox.graph_from_polygon(
                bounding_polygon,
                custom_filter=custom_filter,
                retain_all=True,
                truncate_by_edge=True,
                simplify=True
            )
        else:
            G = ox.graph_from_polygon(
                bounding_polygon,
                network_type=network_type,
                retain_all=True,
                truncate_by_edge=True,
                simplify=True
            )
    except Exception as e:
        logger.warning(f"Falha ao baixar por polígono ({e}). Tentando por Bounding Box...")
        minx, miny, maxx, maxy = bounding_polygon.bounds
        bbox = (float(minx), float(miny), float(maxx), float(maxy))
        G = ox.graph_from_bbox(
            bbox=bbox,
            network_type=network_type,
            custom_filter=custom_filter,
            retain_all=True,
            truncate_by_edge=True,
            simplify=True
        )

    if len(G) == 0:
        raise ValueError("Nenhuma via foi encontrada no OpenStreetMap para a região especificada.")
        
    logger.info(f"Malha viária obtida: {len(G.nodes)} nós e {len(G.edges)} arestas.")
    
    # 3. Converter para GeoDataFrames
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
    
    # 4. Garantir que todas as arestas tenham LineString (mesmo quando simplificadas)
    edges_gdf = ensure_edge_geometries(edges_gdf, nodes_gdf)
    
    return G, edges_gdf, nodes_gdf


def ensure_edge_geometries(edges_gdf: gpd.GeoDataFrame, nodes_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Garante que todas as arestas possuam geometria válida (LineString entre nós u e v).
    """
    edges = edges_gdf.copy()
    if "geometry" not in edges.columns:
        edges["geometry"] = None
        
    null_geom_mask = edges.geometry.isna() | edges.geometry.is_empty
    if null_geom_mask.any():
        logger.debug(f"Criando geometria de linha reta para {null_geom_mask.sum()} arestas sem geometria explícita.")
        for idx in edges[null_geom_mask].index:
            u, v = idx[0], idx[1]
            if u in nodes_gdf.index and v in nodes_gdf.index:
                p_u = nodes_gdf.loc[u].geometry
                p_v = nodes_gdf.loc[v].geometry
                edges.at[idx, "geometry"] = LineString([p_u, p_v])
                
    return edges
