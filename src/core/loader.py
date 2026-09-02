"""
Módulo de carregamento e validação de dados geoespaciais de propriedades rurais.
"""
from typing import Optional, Tuple
import geopandas as gpd
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)


def load_properties(filepath: str, foco_col: str = "foco") -> gpd.GeoDataFrame:
    """
    Carrega arquivo geoespacial (Shapefile, GeoPackage, GeoJSON, etc.) contendo propriedades rurais.
    
    Args:
        filepath: Caminho do arquivo espacial.
        foco_col: Nome da coluna que indica presença de foco (1 para foco, 0 para não foco).
        
    Returns:
        GeoDataFrame validado.
    """
    try:
        gdf = gpd.read_file(filepath)
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo espacial '{filepath}': {e}")
        
    if gdf.empty:
        raise ValueError(f"O arquivo '{filepath}' não contém geometrias.")

    gdf = validate_properties(gdf, foco_col=foco_col)
    return gdf


def validate_properties(gdf: gpd.GeoDataFrame, foco_col: str = "foco") -> gpd.GeoDataFrame:
    """
    Valida e normaliza o GeoDataFrame de propriedades rurais.
    
    Args:
        gdf: GeoDataFrame de propriedades.
        foco_col: Nome da coluna indicadora de foco.
        
    Returns:
        GeoDataFrame validado e tipado.
    """
    gdf = gdf.copy()
    
    # 1. Validar coluna foco (case-insensitive fallback)
    matched_col = None
    for col in gdf.columns:
        if col.lower() == foco_col.lower():
            matched_col = col
            break
            
    if matched_col is None:
        raise ValueError(
            f"Coluna indicadora '{foco_col}' não encontrada no arquivo. "
            f"Colunas disponíveis: {list(gdf.columns)}"
        )
        
    if matched_col != foco_col:
        gdf.rename(columns={matched_col: foco_col}, inplace=True)
        
    # 2. Normalizar valores da coluna foco para 0 e 1
    gdf[foco_col] = gdf[foco_col].fillna(0).astype(int)
    invalid_vals = set(gdf[foco_col].unique()) - {0, 1}
    if invalid_vals:
        # Se contiver outros valores (ex: 2, 3), trata tudo > 0 como 1
        logger.warning(
            f"Valores inesperados na coluna '{foco_col}': {invalid_vals}. "
            f"Valores maiores que 0 serão convertidos para 1."
        )
        gdf[foco_col] = (gdf[foco_col] > 0).astype(int)
        
    total_focos = (gdf[foco_col] == 1).sum()
    if total_focos == 0:
        logger.warning("Nenhum foco (foco == 1) encontrado na base de dados carregada.")
        
    # 3. Validar CRS
    if gdf.crs is None:
        logger.warning("CRS não definido no arquivo. Assumindo EPSG:4326 (WGS 84).")
        gdf.set_crs(epsg=4326, inplace=True)
        
    # 4. Validar e filtrar geometrias nulas ou vazias
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()].copy()
    
    # Se geometrias forem polígonos (ex: limites de fazendas), podemos extrair centróides representativos
    if not all(isinstance(geom, Point) for geom in gdf.geometry):
        logger.info("Convertendo geometrias não pontuais em centróides representativos para análise de foco.")
        # Mantém coluna de geometria original se necessário e usa centróide para o ponto do foco
        gdf["geometry"] = gdf.geometry.centroid

    return gdf


def ensure_projected_crs(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, any]:
    """
    Garante que o GeoDataFrame esteja em um CRS métrico (projetado) para cálculos exatos de buffer.
    Usa estimate_utm_crs() do GeoPandas para encontrar automaticamente a zona UTM ideal.
    
    Args:
        gdf: GeoDataFrame com CRS definido.
        
    Returns:
        Tupla contendo (GeoDataFrame projetado, CRS métrico original/estimado).
    """
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
        
    if gdf.crs.is_projected:
        return gdf, gdf.crs
        
    # Estima CRS métrico local baseado no centróide dos pontos
    metric_crs = gdf.estimate_utm_crs()
    gdf_projected = gdf.to_crs(metric_crs)
    return gdf_projected, metric_crs
