"""
Módulo para criação de zonas infectadas (buffers com coalescência espacial).
"""
from typing import Tuple
import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
import logging
from src.core.loader import ensure_projected_crs

logger = logging.getLogger(__name__)


def create_infected_zones(
    gdf: gpd.GeoDataFrame,
    buffer_km: float,
    foco_col: str = "foco"
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Cria polígonos de zonas infectadas a partir de buffers em torno dos focos.
    Buffers que se sobrepõem coalescem automaticamente em um único polígono.
    
    Args:
        gdf: GeoDataFrame de propriedades rurais.
        buffer_km: Raio do buffer em quilômetros.
        foco_col: Nome da coluna que indica foco.
        
    Returns:
        Tupla com:
          1. GeoDataFrame das Zonas Infectadas (projetado no CRS métrico).
          2. GeoDataFrame das Propriedades com a coluna `zone_id` associada.
    """
    if buffer_km <= 0:
        raise ValueError("O raio do buffer em quilômetros deve ser maior que zero.")
        
    # 1. Filtrar focos
    focos_gdf = gdf[gdf[foco_col] == 1].copy()
    if focos_gdf.empty:
        raise ValueError("Nenhum ponto com 'foco == 1' foi encontrado para gerar buffers.")
        
    # 2. Garantir CRS métrico
    gdf_proj, metric_crs = ensure_projected_crs(gdf)
    focos_proj = gdf_proj[gdf_proj[foco_col] == 1].copy()
    
    # 3. Gerar buffers individuais (distância em metros)
    buffer_meters = buffer_km * 1000.0
    buffers = focos_proj.geometry.buffer(buffer_meters)
    
    # 4. Coalescer buffers sobrepostos através de unary_union
    merged_union = unary_union(buffers)
    
    # 5. Criar GeoDataFrame de zonas individuais (explodir MultiPolygons)
    if isinstance(merged_union, Polygon):
        geoms = [merged_union]
    elif isinstance(merged_union, MultiPolygon):
        geoms = list(merged_union.geoms)
    else:
        # Geometria vazia ou coleção
        geoms = [geom for geom in merged_union.geoms if isinstance(geom, (Polygon, MultiPolygon))]
        
    zones_gdf = gpd.GeoDataFrame(
        {
            "zone_id": [f"ZONA_{i+1:02d}" for i in range(len(geoms))],
            "buffer_km": buffer_km,
            "geometry": geoms
        },
        crs=metric_crs
    )
    
    # 6. Calcular métricas espaciais (Área e Perímetro)
    zones_gdf["area_km2"] = (zones_gdf.geometry.area / 1_000_000.0).round(3)
    zones_gdf["perimeter_km"] = (zones_gdf.geometry.length / 1000.0).round(3)
    
    # 7. Associar propriedades às zonas infectadas (Spatial Join)
    tagged_props_proj = tag_properties_with_zones(gdf_proj, zones_gdf)
    
    # 8. Contar estatísticas por zona
    num_focos_list = []
    num_props_list = []
    
    for _, zone_row in zones_gdf.iterrows():
        zone_geom = zone_row.geometry
        # Propriedades dentro desta zona específica
        props_in_zone = gdf_proj[gdf_proj.geometry.intersects(zone_geom)]
        num_props_list.append(len(props_in_zone))
        num_focos_list.append((props_in_zone[foco_col] == 1).sum())
        
    zones_gdf["num_focos"] = num_focos_list
    zones_gdf["num_propriedades_total"] = num_props_list
    
    # Reprojetar o GeoDataFrame de propriedades resultante para o CRS original
    tagged_props = tagged_props_proj.to_crs(gdf.crs)
    
    logger.info(
        f"Zonas infectadas geradas: {len(zones_gdf)} zona(s) consolidada(s) para {len(focos_gdf)} foco(s) "
        f"com buffer de {buffer_km:.1f} km."
    )
    
    return zones_gdf, tagged_props


def tag_properties_with_zones(
    properties_gdf: gpd.GeoDataFrame,
    zones_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Associa cada propriedade à zona infectada em que está inserida.
    
    Args:
        properties_gdf: GeoDataFrame de propriedades (mesmo CRS de zones_gdf).
        zones_gdf: GeoDataFrame de zonas infectadas.
        
    Returns:
        GeoDataFrame de propriedades com as colunas 'in_infected_zone' e 'zone_id'.
    """
    props = properties_gdf.copy()
    if "zone_id" in props.columns:
        props.drop(columns=["zone_id"], inplace=True)
    if "in_infected_zone" in props.columns:
        props.drop(columns=["in_infected_zone"], inplace=True)
        
    # Spatial join 'within'
    joined = gpd.sjoin(
        props,
        zones_gdf[["zone_id", "geometry"]],
        how="left",
        predicate="within"
    )
    
    # Remover duplicatas se propriedade cair na borda exata
    joined = joined[~joined.index.duplicated(keep="first")]
    
    props["zone_id"] = joined["zone_id"]
    props["in_infected_zone"] = props["zone_id"].notna()
    
    return props
