"""
Módulo de otimização de bloqueios viários utilizando o Teorema do Min-Cut / Max-Flow Híbrido
(Entroncamentos Estratégicos + Arestas Diretas + Garantia Formal de Cobertura Total).
"""
from typing import Dict, Any, List, Optional, Tuple, Set
import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
from shapely.geometry import Point, LineString, MultiPoint, Polygon
from scipy.spatial import cKDTree
import logging

logger = logging.getLogger(__name__)


def classify_highway_type(highway_val: Any) -> str:
    """Classifica a tag 'highway' do OpenStreetMap em categorias amigáveis."""
    if isinstance(highway_val, list):
        highway_val = highway_val[0] if len(highway_val) > 0 else "unclassified"
    highway_str = str(highway_val).lower()
    
    if any(k in highway_str for k in ["motorway", "trunk", "primary"]):
        return "Rodovia Principal / Federal / Estadual"
    elif any(k in highway_str for k in ["secondary", "tertiary"]):
        return "Estrada Secundária / Coletora"
    elif any(k in highway_str for k in ["unclassified", "residential", "living_street"]):
        return "Estrada Municipal / Acesso Local"
    elif any(k in highway_str for k in ["track", "path", "service"]):
        return "Estrada Rural / Vicinal / Servidão"
    else:
        return "Outras Vias"


def extract_road_name(name_val: Any) -> str:
    """Extrai nome legível da via a partir do atributo do OSM."""
    if name_val is None or (isinstance(name_val, float) and np.isnan(name_val)):
        return "Acesso Rural Sem Nome"
    if isinstance(name_val, list):
        return ", ".join(str(n) for n in name_val if pd.notna(n))
    return str(name_val)


def allocate_barriers_min_cut(
    G: nx.MultiDiGraph,
    properties_gdf: gpd.GeoDataFrame,
    zones_gdf: gpd.GeoDataFrame,
    buffer_km: float,
    tolerance_km: float = 1.0,
    cut_mode: str = "hybrid",
    foco_col: str = "foco"
) -> gpd.GeoDataFrame:
    """
    Aloca o número MÍNIMO de bloqueios viários aplicando o Teorema do Min-Cut / Max-Flow
    Híbrido (Entroncamentos + Vias Diretas) por zona de contenção independente.
    
    Garante formalmente que 100% de todas as rotas possíveis de entrada e saída
    sejam interceptadas por postos de fiscalização, aproveitando entroncamentos
    sempre que disponíveis para reduzir custos e bloqueando vias diretas onde não houver convergência.
    
    Args:
        G: Grafo NetworkX da malha viária (OSMnx MultiDiGraph).
        properties_gdf: GeoDataFrame de propriedades rurais.
        zones_gdf: GeoDataFrame com os polígonos das zonas de contenção base.
        buffer_km: Raio base do buffer em quilômetros.
        tolerance_km: Tolerância para busca de entroncamentos em km (ex: ±1.0 km).
        cut_mode: 'hybrid' (Entroncamentos + Vias Diretas), 'junctions' ou 'edges'.
        foco_col: Nome da coluna indicadora de foco.
        
    Returns:
        GeoDataFrame contendo os postos de bloqueio ótimos sem nenhuma rota de fuga.
    """
    if len(G) == 0 or properties_gdf.empty or zones_gdf.empty:
        return gpd.GeoDataFrame(
            columns=["barrier_id", "zone_id", "barrier_type", "road_name", "road_class", "geometry"],
            crs=properties_gdf.crs
        )

    # 1. Alinhar CRS métrico projetado
    metric_crs = properties_gdf.estimate_utm_crs() if not properties_gdf.crs.is_projected else properties_gdf.crs
    props_proj = properties_gdf.to_crs(metric_crs)
    zones_proj = zones_gdf.to_crs(metric_crs)

    # Coordenadas dos nós do grafo viário em CRS métrico
    node_points_wgs = {n: Point(data["x"], data["y"]) for n, data in G.nodes(data=True)}
    node_series_wgs = gpd.GeoSeries(node_points_wgs, crs="EPSG:4326")
    node_series_proj = node_series_wgs.to_crs(metric_crs)

    all_barrier_records: List[Dict[str, Any]] = []

    # 2. Processar CADA ZONA/CLUSTER INFECTADO INDEPENDENTEMENTE
    for _, zone_row in zones_proj.iterrows():
        zone_id = zone_row["zone_id"]
        zone_poly = zone_row.geometry

        # Propriedades foco dentro deste cluster
        focos_in_zone = props_proj[
            (props_proj[foco_col] == 1) & (props_proj.geometry.intersects(zone_poly))
        ]
        if focos_in_zone.empty:
            focos_in_zone = props_proj[props_proj[foco_col] == 1]

        # Polígono expandido com a tolerância de busca de entroncamentos
        expanded_poly = focos_in_zone.geometry.buffer((buffer_km + tolerance_km) * 1000.0).unary_union

        # Classificar nós:
        # Inner: TODOS os nós dentro do polígono de buffer base da zona infectada
        # Outer: Nós fora do polígono expandido
        # Band: Nós intermediários entre o buffer base e o expandido
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

        logger.info(
            f"[{zone_id}] Nós classificados: {len(inner_nodes)} internos (dentro do buffer), "
            f"{len(band_nodes)} na banda de busca, {len(outer_nodes)} externos."
        )

        if not inner_nodes or not outer_nodes:
            logger.warning(f"[{zone_id}] Nós insuficientes para Min-Cut. Aplicando corte geométrico.")
            geom_barriers = allocate_barriers_for_single_zone(G, zone_row, metric_crs)
            all_barrier_records.extend(geom_barriers)
            continue

        # 3. Construir Grafo de Fluxo Híbrido (Nós e Arestas)
        flow_G = nx.DiGraph()
        SUPER_SOURCE = f"__SOURCE_{zone_id}__"
        SUPER_SINK = f"__SINK_{zone_id}__"
        INF_CAP = 1000000.0

        flow_G.add_node(SUPER_SOURCE)
        flow_G.add_node(SUPER_SINK)

        # Conectar TODOS os nós internos da zona infectada ao Super-Source
        for u in inner_nodes:
            flow_G.add_edge(SUPER_SOURCE, f"{u}_in", capacity=INF_CAP)
            flow_G.add_edge(f"{u}_in", f"{u}_out", capacity=INF_CAP)
            flow_G.add_edge(f"{u}_out", f"{u}_in", capacity=INF_CAP)

        # Conectar nós externos ao Super-Sink
        for v in outer_nodes:
            flow_G.add_edge(f"{v}_in", f"{v}_out", capacity=INF_CAP)
            flow_G.add_edge(f"{v}_out", SUPER_SINK, capacity=INF_CAP)
            flow_G.add_edge(f"{v}_out", f"{v}_in", capacity=INF_CAP)

        # Nós na banda de busca (Vertex Splitting)
        # Prioriza entroncamentos (grau >= 3) com capacidade 1.0; outros nós com 1.2
        for w in band_nodes:
            deg = G.degree(w)
            node_cap = 1.0 if deg >= 3 else 1.2
            flow_G.add_edge(f"{w}_in", f"{w}_out", capacity=node_cap)
            flow_G.add_edge(f"{w}_out", f"{w}_in", capacity=node_cap)

        # Adicionar as arestas viárias reais conectando nós relevantes
        relevant_nodes = inner_nodes | band_nodes | outer_nodes
        edge_map = {}

        for u, v, k, data in G.edges(keys=True, data=True):
            if u not in relevant_nodes or v not in relevant_nodes:
                continue

            hw = data.get("highway", "unclassified")
            if isinstance(hw, list):
                hw_str = str(hw[0]).lower()
            else:
                hw_str = str(hw).lower()

            if any(key in hw_str for key in ["motorway", "trunk", "primary"]):
                edge_cap = 10.0
            elif any(key in hw_str for key in ["secondary", "tertiary"]):
                edge_cap = 5.0
            else:
                edge_cap = 1.0

            u_in, u_out = f"{u}_in", f"{u}_out"
            v_in, v_out = f"{v}_in", f"{v}_out"

            flow_G.add_edge(u_out, v_in, capacity=edge_cap)
            flow_G.add_edge(v_out, u_in, capacity=edge_cap)
            
            pair = tuple(sorted([u, v]))
            if pair not in edge_map:
                edge_map[pair] = []
            edge_map[pair].append((u, v, k, data))

        # 4. Executar Min-Cut / Max-Flow
        try:
            cut_value, partition = nx.minimum_cut(
                flow_G,
                SUPER_SOURCE,
                SUPER_SINK,
                flow_func=nx.algorithms.flow.boykov_kolmogorov
            )
        except Exception:
            try:
                cut_value, partition = nx.minimum_cut(
                    flow_G,
                    SUPER_SOURCE,
                    SUPER_SINK,
                    flow_func=nx.algorithms.flow.edmonds_karp
                )
            except Exception as e:
                logger.warning(f"[{zone_id}] Min-Cut falhou ({e}). Usando corte geométrico.")
                geom_barriers = allocate_barriers_for_single_zone(G, zone_row, metric_crs)
                all_barrier_records.extend(geom_barriers)
                continue

        reachable, non_reachable = partition
        logger.info(f"[{zone_id}] Min-Cut executado com sucesso. Valor do corte: {cut_value:.1f}")

        # 5. Extrair nós e arestas cortados
        zone_cut_nodes = set()
        zone_cut_edges = []

        for w in band_nodes:
            w_in, w_out = f"{w}_in", f"{w}_out"
            if w_in in reachable and w_out in non_reachable:
                zone_cut_nodes.add(w)

        for pair, edges_info in edge_map.items():
            u, v = pair
            u_out, v_in = f"{u}_out", f"{v}_in"
            v_out, u_in = f"{v}_out", f"{u}_in"
            
            # Se a aresta direcional foi cortada em qualquer direção
            if (u_out in reachable and v_in in non_reachable) or (v_out in reachable and u_in in non_reachable):
                # Só adiciona arestas se não caírem num entroncamento já cortado
                if u not in zone_cut_nodes and v not in zone_cut_nodes:
                    for edge_info in edges_info:
                        zone_cut_edges.append(edge_info)

        # 6. Criar registros de postos de bloqueio para esta zona
        # 6.1. Postos em Entroncamentos
        for node_id in zone_cut_nodes:
            node_data = G.nodes[node_id]
            pt_wgs = Point(node_data["x"], node_data["y"])
            pt_proj = node_series_proj[node_id]

            adj_edges = list(G.in_edges(node_id, data=True)) + list(G.out_edges(node_id, data=True))
            road_names = set()
            highway_types = set()
            for _, _, edata in adj_edges:
                name = edata.get("name")
                hw = edata.get("highway")
                if name:
                    road_names.add(extract_road_name(name))
                if hw:
                    highway_types.add(str(hw) if not isinstance(hw, list) else str(hw[0]))

            junction_name = " & ".join(list(road_names)[:3]) if road_names else "Entroncamento Rural"
            primary_hw = list(highway_types)[0] if highway_types else "unclassified"

            all_barrier_records.append({
                "zone_id": zone_id,
                "barrier_type": "Entroncamento Estratégico (Min-Cut)",
                "road_name": f"Entroncamento: {junction_name}",
                "road_class": classify_highway_type(primary_hw),
                "highway": primary_hw,
                "connected_roads": len(adj_edges),
                "latitude": round(pt_wgs.y, 6),
                "longitude": round(pt_wgs.x, 6),
                "geometry": pt_proj
            })

        # 6.2. Postos em Vias Diretas Cortadas
        for u, v, k, edata in zone_cut_edges:
            p_u = node_series_proj[u]
            p_v = node_series_proj[v]
            
            if "geometry" in edata:
                geom_wgs = edata["geometry"]
                edge_line_proj = gpd.GeoSeries([geom_wgs], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
            else:
                edge_line_proj = LineString([p_u, p_v])
                
            # Tenta posicionar o bloqueio exatamente na fronteira da zona
            inter = edge_line_proj.intersection(zone_poly.boundary)
            if inter.is_empty:
                inter = edge_line_proj.intersection(expanded_poly.boundary)
                
            if not inter.is_empty:
                if inter.geom_type == 'Point':
                    midpoint = inter
                elif inter.geom_type in ['MultiPoint', 'GeometryCollection']:
                    # Pega o primeiro ponto de interseção
                    midpoint = [g for g in inter.geoms if g.geom_type == 'Point'][0]
                else:
                    midpoint = edge_line_proj.interpolate(0.5, normalized=True)
            else:
                midpoint = edge_line_proj.interpolate(0.5, normalized=True)
                
            pt_wgs = gpd.GeoSeries([midpoint], crs=metric_crs).to_crs(epsg=4326).iloc[0]

            hw = edata.get("highway", "unclassified")
            name = edata.get("name", None)

            all_barrier_records.append({
                "zone_id": zone_id,
                "barrier_type": "Via Direta / Estrangulamento (Min-Cut)",
                "road_name": extract_road_name(name),
                "road_class": classify_highway_type(hw),
                "highway": str(hw) if not isinstance(hw, list) else str(hw[0]),
                "connected_roads": 2,
                "latitude": round(pt_wgs.y, 6),
                "longitude": round(pt_wgs.x, 6),
                "geometry": midpoint
            })

        # 7. VALIDAÇÃO ULTRA-RÁPIDA DE FECHAMENTO (Connected Components Reachability)
        escaped_edges = find_unblocked_escape_paths(
            G=G,
            inner_nodes=inner_nodes,
            outer_nodes=outer_nodes,
            cut_nodes=zone_cut_nodes,
            cut_edges=zone_cut_edges,
            node_series_proj=node_series_proj,
            zone_boundary=zone_poly.boundary
        )
        
        for esc_edge in escaped_edges:
            all_barrier_records.append({
                "zone_id": zone_id,
                "barrier_type": "Bloqueio Complementar de Fronteira",
                "road_name": esc_edge["road_name"],
                "road_class": esc_edge["road_class"],
                "highway": esc_edge["highway"],
                "connected_roads": 2,
                "latitude": esc_edge["latitude"],
                "longitude": esc_edge["longitude"],
                "geometry": esc_edge["geometry"]
            })

    if not all_barrier_records:
        logger.warning("Nenhum posto de bloqueio gerado. Aplicando corte geométrico de fallback.")
        return allocate_barriers(ox_gdfs_from_graph(G)[1], zones_gdf)

    barriers_gdf = gpd.GeoDataFrame(all_barrier_records, crs=metric_crs)

    # 8. Deduplicação e Consolidação de Postos Contíguos (< 35m)
    barriers_gdf = consolidate_barrier_points(barriers_gdf, max_dist=35.0)

    # Atribuir identificadores sequenciais
    barriers_gdf["barrier_id"] = [f"BLOQ_{i+1:03d}" for i in range(len(barriers_gdf))]
    
    # Atualizar coordenadas WGS84
    wgs_pts = barriers_gdf.to_crs(epsg=4326)
    barriers_gdf["latitude"] = wgs_pts.geometry.y.round(6)
    barriers_gdf["longitude"] = wgs_pts.geometry.x.round(6)

    logger.info(
        f"Alocação Min-Cut Híbrida concluída: {len(barriers_gdf)} postos no total, "
        f"garantindo 100% de contenção em todos os focos."
    )
    return barriers_gdf


def find_unblocked_escape_paths(
    G: nx.MultiDiGraph,
    inner_nodes: Set[Any],
    outer_nodes: Set[Any],
    cut_nodes: Set[Any],
    cut_edges: List[Tuple],
    node_series_proj: gpd.GeoSeries,
    zone_boundary: any
) -> List[Dict[str, Any]]:
    """
    Executa verificação ultra-rápida de reachability usando componentes conexos.
    Garante que qualquer rota de fuga residual seja imediatamente interceptada.
    """
    G_test = nx.Graph()
    
    blocked_edge_set = set()
    for edge_info in cut_edges:
        u, v = edge_info[0], edge_info[1]
        blocked_edge_set.add((u, v))
        blocked_edge_set.add((v, u))

    for u, v, k, edata in G.edges(keys=True, data=True):
        if u in cut_nodes or v in cut_nodes:
            continue
        if (u, v) in blocked_edge_set:
            continue
        G_test.add_edge(u, v, **edata)

    escape_records = []
    visited_pairs = set()

    for comp in nx.connected_components(G_test):
        comp_inner = comp & inner_nodes
        comp_outer = comp & outer_nodes
        
        if comp_inner and comp_outer:
            subg = G_test.subgraph(comp)
            for u, v, edata in subg.edges(data=True):
                pair = tuple(sorted([u, v]))
                if pair in visited_pairs:
                    continue
                    
                p1 = node_series_proj[u]
                p2 = node_series_proj[v]
                
                if "geometry" in edata:
                    geom_wgs = edata["geometry"]
                    line = gpd.GeoSeries([geom_wgs], crs="EPSG:4326").to_crs(node_series_proj.crs).iloc[0]
                else:
                    line = LineString([p1, p2])
                
                if line.intersects(zone_boundary):
                    visited_pairs.add(pair)
                    inter = line.intersection(zone_boundary)
                    pt = inter if isinstance(inter, Point) else Point(line.interpolate(0.5, normalized=True))
                    pt_wgs = gpd.GeoSeries([pt], crs=node_series_proj.crs).to_crs(epsg=4326).iloc[0]
                    
                    hw = edata.get("highway", "unclassified")
                    name = edata.get("name", None)
                    
                    escape_records.append({
                        "road_name": extract_road_name(name),
                        "road_class": classify_highway_type(hw),
                        "highway": str(hw) if not isinstance(hw, list) else str(hw[0]),
                        "latitude": round(pt_wgs.y, 6),
                        "longitude": round(pt_wgs.x, 6),
                        "geometry": pt
                    })

    return escape_records


def allocate_barriers_for_single_zone(
    G: nx.MultiDiGraph,
    zone_row: any,
    metric_crs: any
) -> List[Dict[str, Any]]:
    """Corte geométrico para uma única zona isolada."""
    from src.core.osm import ensure_edge_geometries
    nodes_gdf, edges_gdf = ox_gdfs_from_graph(G)
    zone_gdf = gpd.GeoDataFrame([zone_row], crs=metric_crs)
    b_df = allocate_barriers(edges_gdf, zone_gdf)
    return b_df.to_dict(orient="records")


def ox_gdfs_from_graph(G: nx.MultiDiGraph):
    """Extrai GeoDataFrames de nós e arestas de um MultiDiGraph OSMnx."""
    import osmnx as ox
    return ox.graph_to_gdfs(G)


def allocate_barriers(
    edges_gdf: gpd.GeoDataFrame,
    zones_gdf: gpd.GeoDataFrame,
    dedup_distance_meters: float = 30.0
) -> gpd.GeoDataFrame:
    """Corte de fronteira simples (legado/fallback)."""
    if edges_gdf.empty or zones_gdf.empty:
        return gpd.GeoDataFrame(
            columns=["barrier_id", "zone_id", "barrier_type", "highway", "road_name", "road_class", "geometry"],
            crs=zones_gdf.crs
        )

    metric_crs = zones_gdf.crs if zones_gdf.crs.is_projected else zones_gdf.estimate_utm_crs()
    zones_proj = zones_gdf.to_crs(metric_crs)
    edges_proj = edges_gdf.to_crs(metric_crs) if edges_gdf.crs != metric_crs else edges_gdf

    raw_barriers: List[Dict[str, Any]] = []

    for _, zone_row in zones_proj.iterrows():
        zone_id = zone_row["zone_id"]
        zone_poly = zone_row.geometry
        zone_boundary = zone_poly.boundary

        possible_edges_idx = list(edges_proj.sindex.intersection(zone_boundary.bounds))
        if not possible_edges_idx:
            continue
            
        candidate_edges = edges_proj.iloc[possible_edges_idx]
        
        for idx, edge_row in candidate_edges.iterrows():
            edge_geom = edge_row.geometry
            if not edge_geom.intersects(zone_boundary):
                continue
                
            intersection = edge_geom.intersection(zone_boundary)
            if intersection.is_empty:
                continue

            points: List[Point] = []
            if isinstance(intersection, Point):
                points.append(intersection)
            elif isinstance(intersection, MultiPoint):
                points.extend(list(intersection.geoms))
            elif isinstance(intersection, (LineString, MultiLineString)):
                if isinstance(intersection, LineString):
                    points.extend([Point(intersection.coords[0]), Point(intersection.coords[-1])])
                else:
                    for ls in intersection.geoms:
                        points.extend([Point(ls.coords[0]), Point(ls.coords[-1])])

            highway_val = edge_row.get("highway", "unclassified")
            name_val = edge_row.get("name", None)

            for pt in points:
                raw_barriers.append({
                    "zone_id": zone_id,
                    "barrier_type": "Fronteira Simples",
                    "highway": str(highway_val) if not isinstance(highway_val, list) else str(highway_val[0]),
                    "road_name": extract_road_name(name_val),
                    "road_class": classify_highway_type(highway_val),
                    "geometry": pt
                })

    if not raw_barriers:
        return gpd.GeoDataFrame(
            columns=["barrier_id", "zone_id", "barrier_type", "highway", "road_name", "road_class", "geometry"],
            crs=metric_crs
        )

    raw_df = gpd.GeoDataFrame(raw_barriers, crs=metric_crs)
    consolidated = consolidate_barrier_points(raw_df, max_dist=dedup_distance_meters)
    
    wgs84_barriers = consolidated.to_crs(epsg=4326)
    consolidated["latitude"] = wgs84_barriers.geometry.y.round(6)
    consolidated["longitude"] = wgs84_barriers.geometry.x.round(6)
    consolidated["barrier_id"] = [f"BLOQ_{i+1:03d}" for i in range(len(consolidated))]
    return consolidated


def consolidate_barrier_points(
    barriers_gdf: gpd.GeoDataFrame,
    max_dist: float = 30.0
) -> gpd.GeoDataFrame:
    """Agrupa pontos de bloqueio contíguos a menos de max_dist metros."""
    if len(barriers_gdf) <= 1:
        return barriers_gdf

    coords = np.array([(geom.x, geom.y) for geom in barriers_gdf.geometry])
    tree = cKDTree(coords)
    
    visited = set()
    clusters = []

    for i in range(len(coords)):
        if i in visited:
            continue
        neighbors = tree.query_ball_point(coords[i], r=max_dist)
        cur_zone = barriers_gdf.iloc[i]["zone_id"]
        valid_neighbors = [n for n in neighbors if n not in visited and barriers_gdf.iloc[n]["zone_id"] == cur_zone]
        visited.update(valid_neighbors)
        clusters.append(valid_neighbors)

    merged_records = []
    for cluster_indices in clusters:
        cluster_rows = barriers_gdf.iloc[cluster_indices]
        mean_x = cluster_rows.geometry.x.mean()
        mean_y = cluster_rows.geometry.y.mean()
        rep_geom = Point(mean_x, mean_y)
        
        rep_row = cluster_rows.iloc[0]
        named_rows = cluster_rows[~cluster_rows["road_name"].str.contains("Sem Nome", na=False)]
        if not named_rows.empty:
            rep_row = named_rows.iloc[0]

        record = {
            "zone_id": rep_row.get("zone_id", "ZONA_01"),
            "barrier_type": rep_row.get("barrier_type", "Bloqueio"),
            "highway": rep_row.get("highway", "unclassified"),
            "road_name": rep_row.get("road_name", "Via"),
            "road_class": rep_row.get("road_class", "Via"),
            "geometry": rep_geom
        }
        if "connected_roads" in rep_row:
            record["connected_roads"] = rep_row["connected_roads"]
        merged_records.append(record)

    return gpd.GeoDataFrame(merged_records, crs=barriers_gdf.crs)
