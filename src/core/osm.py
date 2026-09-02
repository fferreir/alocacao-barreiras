"""
Módulo para download e processamento da malha viária do OpenStreetMap via OSMnx.
"""
from typing import Tuple, Optional
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import LineString, box
import logging

logger = logging.getLogger(__name__)

# Configurações do OSMnx
ox.settings.log_console = False
ox.settings.use_cache = True


def download_road_network(
    zones_gdf: gpd.GeoDataFrame,
    network_type: str = "all",
    buffer_margin_km: float = 2.0,
    custom_filter: Optional[str] = None
) -> Tuple[nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Baixa a malha viária do OpenStreetMap cobrindo a extensão das zonas infectadas
    mais uma margem de segurança.
    
    Args:
        zones_gdf: GeoDataFrame contendo os polígonos das zonas infectadas.
        network_type: Tipo de rede do OSM ('drive', 'all', 'drive_service', etc.).
        buffer_margin_km: Margem adicional ao redor da zona em quilômetros.
        custom_filter: Filtro Overpass customizado (opcional).
        
    Returns:
        Tupla com:
          1. Grafo NetworkX (MultiDiGraph).
          2. GeoDataFrame de arestas (edges_gdf).
          3. GeoDataFrame de nós (nodes_gdf).
    """
    # 1. Garantir que temos a geometria em WGS84 (EPSG:4326)
    zones_wgs84 = zones_gdf.to_crs(epsg=4326)
    
    # 2. Obter a união e aplicar margem na geometria projetada
    zones_metric = zones_gdf.to_crs(zones_gdf.estimate_utm_crs())
    union_metric = zones_metric.unary_union.buffer(buffer_margin_km * 1000.0)
    
    # Reprojetar o polígono expandido para EPSG:4326
    bounding_polygon = gpd.GeoSeries([union_metric], crs=zones_metric.crs).to_crs(epsg=4326).iloc[0]
    
    logger.info(f"Baixando malha viária OSM (tipo: '{network_type}') para a região de estudo...")
    
    try:
        if custom_filter:
            G = ox.graph_from_polygon(
                bounding_polygon,
                custom_filter=custom_filter,
                retain_all=True,
                simplify=True
            )
        else:
            G = ox.graph_from_polygon(
                bounding_polygon,
                network_type=network_type,
                retain_all=True,
                simplify=True
            )
    except Exception as e:
        logger.warning(f"Falha ao baixar por polígono ({e}). Tentando por Bounding Box...")
        bounds = bounding_polygon.bounds  # minx, miny, maxx, maxy (lon_min, lat_min, lon_max, lat_max)
        # OSMnx graph_from_bbox aceita bbox=(north, south, east, west) ou (lat_max, lat_min, lon_max, lon_min)
        lat_max, lat_min = bounds[3], bounds[1]
        lon_max, lon_min = bounds[2], bounds[0]
        try:
            # Compatibilidade com versões do OSMnx (bbox=(north, south, east, west) ou bbox=tuple)
            G = ox.graph_from_bbox(
                bbox=(lat_max, lat_min, lon_max, lon_min),
                network_type=network_type,
                retain_all=True,
                simplify=True
            )
        except TypeError:
            G = ox.graph_from_bbox(
                north=lat_max,
                south=lat_min,
                east=lon_max,
                west=lon_min,
                network_type=network_type,
                retain_all=True,
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
