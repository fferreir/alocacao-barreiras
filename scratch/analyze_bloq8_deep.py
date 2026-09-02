import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import Point
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
from src.core.optimizer import allocate_barriers_min_cut

def analyze():
    props_gdf = load_properties("data/propriedades_rurais_exemplo.shp", foco_col="foco")
    zones_gdf, _ = create_infected_zones(props_gdf, buffer_km=4.0, foco_col="foco")
    G, edges_gdf, nodes_gdf = download_road_network(zones_gdf, network_type="all", buffer_margin_km=2.0)
    
    target_lat, target_lon = -22.77249, -47.48761
    metric_crs = zones_gdf.estimate_utm_crs()
    target_geom = Point(target_lon, target_lat)
    target_proj = gpd.GeoSeries([target_geom], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
    edges_proj = edges_gdf.to_crs(metric_crs)
    edges_proj['dist'] = edges_proj.geometry.distance(target_proj)
    nearest_edge = edges_proj.loc[edges_proj['dist'].idxmin()]
    
    u = nearest_edge.name[0]
    v = nearest_edge.name[1]
    
    print(f"Edge: {u} -> {v}")
    
    zone_poly = zones_gdf.iloc[0].geometry
    expanded_poly = props_gdf[props_gdf['foco']==1].geometry.buffer((4.0 + 1.5) * 1000.0).unary_union
    
    node_u = nodes_gdf.loc[u].geometry
    node_v = nodes_gdf.loc[v].geometry
    node_u_proj = gpd.GeoSeries([node_u], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
    node_v_proj = gpd.GeoSeries([node_v], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
    
    def classify(pt):
        if zone_poly.contains(pt): return "INNER"
        if not expanded_poly.contains(pt): return "OUTER"
        return "BAND"
        
    print(f"Node u classification: {classify(node_u_proj)}")
    print(f"Node v classification: {classify(node_v_proj)}")
    
if __name__ == "__main__":
    analyze()
