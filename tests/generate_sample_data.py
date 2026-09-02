"""
Script para geração de base de dados sintética realista de propriedades rurais
em uma região do Brasil com malha viária real no OpenStreetMap.
"""
import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

def generate_sample_properties(output_dir: str = "data") -> str:
    """
    Gera um Shapefile e GeoJSON de propriedades rurais na região de Piracicaba/SP (Brasil),
    contendo propriedades com foco (1) e sem foco (0), configuradas para demonstrar
    tanto a coalescência de buffers próximos quanto buffers isolados.
    """
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(42)

    # Coordenada central (Região rural de Piracicaba / Santa Bárbara d'Oeste / SP)
    # Centro: Lat -22.72, Lon -47.65
    base_lat = -22.72
    base_lon = -47.65

    # Cluster 1: Grupo de 3 focos próximos (devem coalescer com buffer >= 3km)
    cluster1_points = [
        (-22.710, -47.640, 1, "Fazenda Santa Cruz (Foco 1)"),
        (-22.725, -47.625, 1, "Sítio Boa Vista (Foco 2)"),
        (-22.700, -47.630, 1, "Estância Esperança (Foco 3)"),
    ]

    # Cluster 2: Foco isolado a ~12 km de distância (deve formar zona separada)
    cluster2_points = [
        (-22.790, -47.530, 1, "Fazenda Bela Alvorada (Foco 4 - Isolado)"),
    ]

    # Propriedades de controle / sadias (foco == 0)
    control_points = []
    nomes_propriedades = [
        "Sítio dos Ipês", "Fazenda Primavera", "Recanto das Águas", "Fazenda São José",
        "Sítio Monte Alegre", "Rancho Fundo", "Estância Paraíso", "Fazenda Morro Alto",
        "Chácara Bela Vista", "Sítio São Pedro", "Fazenda Canavial", "Rancho da Colina",
        "Sítio Palmeiras", "Fazenda Três Barras", "Sítio do Cedro", "Fazenda Rio Claro",
        "Chácara das Flores", "Sítio Recanto Verde", "Fazenda Santo Antônio", "Sítio Aliança"
    ]

    for i, nome in enumerate(nomes_propriedades):
        lat_offset = np.random.uniform(-0.10, 0.10)
        lon_offset = np.random.uniform(-0.12, 0.12)
        control_points.append((base_lat + lat_offset, base_lon + lon_offset, 0, nome))

    all_data = cluster1_points + cluster2_points + control_points

    records = []
    for idx, (lat, lon, foco, nome) in enumerate(all_data):
        records.append({
            "id": idx + 1,
            "codigo": f"CAR_SP_{idx+1:04d}",
            "nome": nome,
            "area_ha": round(np.random.uniform(50, 800), 1),
            "atividade": np.random.choice(["Cana-de-açúcar", "Pecuária de Corte", "Citros", "Grãos", "Pecuária de Leite"]),
            "foco": int(foco),
            "geometry": Point(lon, lat)
        })

    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")

    # Salvar em Shapefile e GeoJSON
    shp_path = os.path.join(output_dir, "propriedades_rurais_exemplo.shp")
    geojson_path = os.path.join(output_dir, "propriedades_rurais_exemplo.geojson")

    gdf.to_file(shp_path, driver="ESRI Shapefile", encoding="utf-8")
    gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"Base de dados sintética criada com sucesso:")
    print(f" - Shapefile: {shp_path}")
    print(f" - GeoJSON: {geojson_path}")
    print(f" - Total de Propriedades: {len(gdf)} (Focos: {(gdf['foco'] == 1).sum()})")

    return shp_path

if __name__ == "__main__":
    generate_sample_properties()
