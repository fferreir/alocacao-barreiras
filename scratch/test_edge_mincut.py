import geopandas as gpd
import osmnx as ox
import networkx as nx
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.optimizer import allocate_barriers_min_cut
from shapely.geometry import Point

def test_edge_mincut():
    # Cria grafos de teste, propriedades, zonas
    G = nx.MultiDiGraph()
    G.graph['crs'] = 'EPSG:4326'
    # Foco
    G.add_node(1, x=-50.0, y=-20.0)
    # Band
    G.add_node(2, x=-50.01, y=-20.01)
    G.add_node(3, x=-50.02, y=-20.02)
    # Outer
    G.add_node(4, x=-50.05, y=-20.05)
    
    G.add_edge(1, 2, highway='primary')
    G.add_edge(2, 4, highway='primary')
    G.add_edge(2, 3, highway='track')
    G.add_edge(3, 4, highway='track')
    
    props = gpd.GeoDataFrame({
        'id': [1],
        'foco': [1],
        'geometry': [Point(-50.0, -20.0)]
    }, crs='EPSG:4326')
    
    zones = gpd.GeoDataFrame({
        'zone_id': ['Z1'],
        'geometry': [Point(-50.0, -20.0).buffer(0.01)] # 1km roughly
    }, crs='EPSG:4326')
    
    print("Testing original allocate_barriers_min_cut...")
    b = allocate_barriers_min_cut(G, props, zones, buffer_km=1.0, tolerance_km=1.0)
    print(b)
    
if __name__ == "__main__":
    test_edge_mincut()
