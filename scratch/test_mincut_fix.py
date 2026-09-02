"""
Script de teste da formulação corrigida de Min-Cut com cobertura integral da zona infectada.
"""
import geopandas as gpd
from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
import networkx as nx
from shapely.geometry import Point, LineString
import logging

props = load_properties('data/propriedades_rurais_exemplo.shp')
zones, tagged = create_infected_zones(props, buffer_km=4.0)
G, edges, nodes = download_road_network(zones, buffer_margin_km=2.5)

metric_crs = props.estimate_utm_crs()
props_proj = props.to_crs(metric_crs)
zones_proj = zones.to_crs(metric_crs)

node_points_wgs = {n: Point(d['x'], d['y']) for n, d in G.nodes(data=True)}
node_series_proj = gpd.GeoSeries(node_points_wgs, crs='EPSG:4326').to_crs(metric_crs)

# Testar na ZONA_01 (Foco 4)
z1_row = zones_proj[zones_proj.zone_id == 'ZONA_01'].iloc[0]
zone_poly = z1_row.geometry
foco4_geom = props_proj[props_proj.foco == 1].iloc[3].geometry

# Banda de busca:
# Inner: Nós estritamente dentro da zona de buffer (4.0km)
# Outer: Nós fora do buffer expandido (5.5km)
# Band: Nós entre o buffer e o buffer expandido
expanded_poly = foco4_geom.buffer(5500.0)

inner_nodes = set()
outer_nodes = set()
band_nodes = set()

for node_id, geom in node_series_proj.items():
    if not expanded_poly.buffer(3000.0).contains(geom):
        continue
    if zone_poly.contains(geom):
        inner_nodes.add(node_id)
    elif not expanded_poly.contains(geom):
        outer_nodes.add(node_id)
    else:
        band_nodes.add(node_id)

print(f"ZONA_01 Nós: {len(inner_nodes)} internos (dentro do buffer), {len(band_nodes)} na banda de busca, {len(outer_nodes)} externos.")

flow_G = nx.DiGraph()
SUPER_SOURCE = "__SOURCE__"
SUPER_SINK = "__SINK__"
INF_CAP = 1000000.0

flow_G.add_node(SUPER_SOURCE)
flow_G.add_node(SUPER_SINK)

# Conectar TODOS os nós dentro do buffer ao Super-Source
for u in inner_nodes:
    flow_G.add_edge(SUPER_SOURCE, f"{u}_in", capacity=INF_CAP)
    flow_G.add_edge(f"{u}_in", f"{u}_out", capacity=INF_CAP)
    flow_G.add_edge(f"{u}_out", f"{u}_in", capacity=INF_CAP)

for v in outer_nodes:
    flow_G.add_edge(f"{v}_in", f"{v}_out", capacity=INF_CAP)
    flow_G.add_edge(f"{v}_out", SUPER_SINK, capacity=INF_CAP)
    flow_G.add_edge(f"{v}_out", f"{v}_in", capacity=INF_CAP)

for w in band_nodes:
    deg = G.degree(w)
    # Incentivar entroncamentos (grau >= 3) com capacidade 1.0, nós intermediários 1.2
    node_cap = 1.0 if deg >= 3 else 1.2
    flow_G.add_edge(f"{w}_in", f"{w}_out", capacity=node_cap)
    flow_G.add_edge(f"{w}_out", f"{w}_in", capacity=node_cap)

relevant_nodes = inner_nodes | band_nodes | outer_nodes
edge_map = {}

for u, v, k, data in G.edges(keys=True, data=True):
    if u not in relevant_nodes or v not in relevant_nodes:
        continue
    u_in, u_out = f"{u}_in", f"{u}_out"
    v_in, v_out = f"{v}_in", f"{v}_out"
    
    # Se cruza da zona interna para fora ou passa pela banda
    is_cuttable = (u in band_nodes or v in band_nodes or (u in inner_nodes and v in outer_nodes) or (u in outer_nodes and v in inner_nodes))
    edge_cap = 1.0 if is_cuttable else INF_CAP
    
    flow_G.add_edge(u_out, v_in, capacity=edge_cap)
    edge_map[(u_out, v_in)] = (u, v, k, data)
    flow_G.add_edge(v_out, u_in, capacity=edge_cap)
    edge_map[(v_out, u_in)] = (v, u, k, data)

cut_value, (reachable, non_reachable) = nx.minimum_cut(flow_G, SUPER_SOURCE, SUPER_SINK)
print(f"Corte Mínimo Exato Calculado: {cut_value:.1f}")

cut_nodes = set()
cut_edges = []

for w in band_nodes:
    if f"{w}_in" in reachable and f"{w}_out" in non_reachable:
        cut_nodes.add(w)

for (u_out, v_in), edge_info in edge_map.items():
    if u_out in reachable and v_in in non_reachable:
        u_node, v_node = edge_info[0], edge_info[1]
        if u_node not in cut_nodes and v_node not in cut_nodes:
            cut_edges.append(edge_info)

print(f"Postos em Entroncamentos: {len(cut_nodes)}, Postos em Arestas Diretas: {len(cut_edges)}")

# Testar se sobrou qualquer fuga
G_test = nx.Graph()
blocked_edges = set((e[0], e[1]) for e in cut_edges) | set((e[1], e[0]) for e in cut_edges)
for u, v in G.edges():
    if u in cut_nodes or v in cut_nodes: continue
    if (u, v) in blocked_edges: continue
    G_test.add_edge(u, v)

leaked = False
for comp in nx.connected_components(G_test):
    if (comp & inner_nodes) and (comp & outer_nodes):
        leaked = True
        break

if not leaked:
    print("✔ PERFEITO! NENHUM VAZAMENTO: 100% DAS ROTAS FORAM BLOQUEADAS!")
else:
    print("Vazamento detectado.")
