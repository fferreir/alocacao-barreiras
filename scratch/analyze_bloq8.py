import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point, LineString
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network

def analyze():
    print("Loading data...")
    props_gdf = load_properties("data/propriedades_rurais_exemplo.shp", foco_col="foco")
    zones_gdf, _ = create_infected_zones(props_gdf, buffer_km=4.0, foco_col="foco")
    G, edges_gdf, nodes_gdf = download_road_network(zones_gdf, network_type="all", buffer_margin_km=2.0)
    
    target_lat, target_lon = -22.77249, -47.48761
    
    # We want to find the edge closest to this point
    target_geom = Point(target_lon, target_lat)
    
    # Reproject to metric for distance calc
    metric_crs = zones_gdf.estimate_utm_crs()
    target_proj = gpd.GeoSeries([target_geom], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
    edges_proj = edges_gdf.to_crs(metric_crs)
    
    edges_proj['dist'] = edges_proj.geometry.distance(target_proj)
    nearest_edge = edges_proj.loc[edges_proj['dist'].idxmin()]
    
    u = nearest_edge.name[0]
    v = nearest_edge.name[1]
    
    G_undir = ox.utils_graph.get_undirected(G)
    
    deg_u = G_undir.degree(u)
    deg_v = G_undir.degree(v)
    
    print(f"\nNearest edge: {u} -> {v}")
    print(f"Degree of u ({u}): {deg_u}")
    print(f"Degree of v ({v}): {deg_v}")
    
    if deg_u == 1 or deg_v == 1:
        print("This edge leads to a DEAD END!")
    else:
        print("This edge is part of a continuing path.")

if __name__ == "__main__":
    analyze()
