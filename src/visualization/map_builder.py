"""
Módulo para construção de mapas interativos Folium com zonas de contenção e barreiras Min-Cut.
"""
from typing import Optional
import folium
from folium.plugins import Fullscreen, MeasureControl, MiniMap
import geopandas as gpd
import json
import logging

logger = logging.getLogger(__name__)


def get_marker_color_by_class(road_class: str) -> str:
    """Retorna cor do marcador com base na importância da via."""
    if "Principal" in road_class or "Federal" in road_class or "Estadual" in road_class:
        return "red"
    elif "Secundária" in road_class or "Coletora" in road_class:
        return "orange"
    elif "Municipal" in road_class or "Local" in road_class:
        return "blue"
    elif "Rural" in road_class or "Vicinal" in road_class:
        return "purple"
    return "darkblue"


def build_interactive_map(
    properties_gdf: gpd.GeoDataFrame,
    zones_gdf: gpd.GeoDataFrame,
    barriers_gdf: gpd.GeoDataFrame,
    edges_gdf: Optional[gpd.GeoDataFrame] = None,
    foco_col: str = "foco",
    save_html_path: Optional[str] = None
) -> folium.Map:
    """
    Constrói um mapa interativo completo com camadas de propriedades, focos,
    zonas de contenção, malha viária e postos de bloqueio alocados por Min-Cut em entroncamentos.
    
    Args:
        properties_gdf: GeoDataFrame de propriedades rurais.
        zones_gdf: GeoDataFrame com as zonas infectadas (buffers coalescidos).
        barriers_gdf: GeoDataFrame com os pontos de bloqueio viário ótimos.
        edges_gdf: GeoDataFrame com a malha viária OSM (opcional).
        foco_col: Nome da coluna que indica foco.
        save_html_path: Caminho para salvar o arquivo HTML gerado.
        
    Returns:
        Objeto folium.Map gerado.
    """
    # 1. Converter todas as camadas para WGS 84 (EPSG:4326)
    props_wgs = properties_gdf.to_crs(epsg=4326)
    zones_wgs = zones_gdf.to_crs(epsg=4326)
    barriers_wgs = barriers_gdf.to_crs(epsg=4326) if not barriers_gdf.empty else barriers_gdf
    edges_wgs = edges_gdf.to_crs(epsg=4326) if edges_gdf is not None and not edges_gdf.empty else None

    # 2. Calcular centro do mapa
    center_lat = props_wgs.geometry.y.mean()
    center_lon = props_wgs.geometry.x.mean()

    # 3. Inicializar Mapa com Camadas Base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB positron",
        control_scale=True
    )
    
    # Camadas base adicionais
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri World Street Map"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satélite (Esri World Imagery)"
    ).add_to(m)

    # 4. Camada de Zonas de Contenção (Buffers Coalescidos)
    fg_zones = folium.FeatureGroup(name="🚨 Zonas de Contenção (Área Infectada)", show=True)
    for _, zrow in zones_wgs.iterrows():
        z_id = zrow.get("zone_id", "Zona")
        z_area = zrow.get("area_km2", 0.0)
        z_perim = zrow.get("perimeter_km", 0.0)
        z_focos = zrow.get("num_focos", 0)
        z_props = zrow.get("num_propriedades_total", 0)
        
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="color: #D32F2F; margin-bottom: 5px;">⚠️ Zona de Contenção {z_id}</h4>
            <hr style="margin: 4px 0;"/>
            <b>Área Total:</b> {z_area} km²<br/>
            <b>Perímetro da Fronteira:</b> {z_perim} km<br/>
            <b>Focos Ativos Contidos:</b> {z_focos}<br/>
            <b>Total de Propriedades na Zona:</b> {z_props}<br/>
        </div>
        """
        
        geo_json = zrow.geometry.__geo_interface__
        folium.GeoJson(
            geo_json,
            style_function=lambda x: {
                "fillColor": "#F44336",
                "color": "#B71C1C",
                "weight": 2.5,
                "fillOpacity": 0.22,
                "dashArray": "5, 5"
            },
            tooltip=f"Zona {z_id} ({z_area} km²)",
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(fg_zones)
    fg_zones.add_to(m)

    # 5. Camada de Malha Viária
    if edges_wgs is not None and not edges_wgs.empty:
        fg_roads = folium.FeatureGroup(name="🛣️ Vias Conectadas (Vetor OSM)", show=True)
        try:
            sample_edges = edges_wgs.copy()
            if len(sample_edges) > 1000:
                zones_poly_union = zones_wgs.unary_union.buffer(0.015)
                sample_edges = sample_edges[sample_edges.intersects(zones_poly_union)]
                
            cols_to_keep = [c for c in ["name", "highway", "geometry"] if c in sample_edges.columns]
            sample_edges = sample_edges[cols_to_keep]
            
            folium.GeoJson(
                sample_edges.__geo_interface__,
                style_function=lambda x: {
                    "color": "#FFC107",  # Amarelo/Laranja de alto contraste
                    "weight": 3.0,       # Linha mais grossa
                    "opacity": 0.95      # Quase totalmente opaco
                }
            ).add_to(fg_roads)
            fg_roads.add_to(m)
        except Exception as e:
            logger.warning(f"Erro ao renderizar malha viária: {e}")

    # 6. Camada de Propriedades Rurais (Sadias e Focos)
    fg_focos = folium.FeatureGroup(name="🔴 Propriedades com Foco Sanitário", show=True)
    fg_sadias = folium.FeatureGroup(name="🟢 Propriedades de Controle (Sem Foco)", show=True)

    for _, prow in props_wgs.iterrows():
        is_foco = int(prow.get(foco_col, 0)) == 1
        prop_id = prow.get("id", prow.get("codigo", f"Prop_{prow.name}"))
        prop_name = prow.get("nome", prow.get("propriedad", f"Propriedade {prop_id}"))
        lat, lon = prow.geometry.y, prow.geometry.x
        
        popup_html = f"""
        <div style="font-family: Arial; min-width: 180px;">
            <b>ID:</b> {prop_id}<br/>
            <b>Propriedade:</b> {prop_name}<br/>
            <b>Status Sanitário:</b> {'<span style="color:red; font-weight:bold;">🚨 FOCO CONFIRMADO</span>' if is_foco else '<span style="color:green;">Sem Foco</span>'}<br/>
            <b>Coordenadas:</b> {lat:.5f}, {lon:.5f}
        </div>
        """
        
        if is_foco:
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color="#B71C1C",
                fill=True,
                fill_color="#FF1744",
                fill_opacity=0.9,
                weight=2.5,
                tooltip=f"🚨 FOCO: {prop_name}",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(fg_focos)
        else:
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color="#2E7D32",
                fill=True,
                fill_color="#4CAF50",
                fill_opacity=0.7,
                weight=1,
                tooltip=f"Propriedade: {prop_name}",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(fg_sadias)

    fg_focos.add_to(m)
    fg_sadias.add_to(m)

    # 7. Camada de Pontos de Bloqueio Sanitário (Min-Cut / Entroncamentos)
    if not barriers_wgs.empty:
        fg_barriers = folium.FeatureGroup(name="🛑 Postos de Bloqueio Ótimos (Min-Cut)", show=True)
        
        for _, brow in barriers_wgs.iterrows():
            b_id = brow.get("barrier_id", "Bloqueio")
            z_id = brow.get("zone_id", "Zona")
            b_type = brow.get("barrier_type", "Posto de Bloqueio")
            r_name = brow.get("road_name", "Via Local")
            r_class = brow.get("road_class", "Via")
            hw_type = brow.get("highway", "N/A")
            n_connected = brow.get("connected_roads", 2)
            b_lat = brow.geometry.y
            b_lon = brow.geometry.x
            color = get_marker_color_by_class(r_class)
            
            is_junction = "Entroncamento" in str(b_type)
            icon_name = "random" if is_junction else "ban"
            
            popup_html = f"""
            <div style="font-family: Arial; min-width: 230px;">
                <h4 style="color: #C62828; margin-bottom: 4px;">🛑 Posto {b_id}</h4>
                <div style="font-size: 11px; color: #555; margin-bottom: 6px;"><b>Tipo:</b> {b_type}</div>
                <hr style="margin: 4px 0;"/>
                <b>Local / Via:</b> {r_name}<br/>
                <b>Classificação:</b> {r_class}<br/>
                <b>Vias Conectadas no Ponto:</b> {n_connected}<br/>
                <b>Coordenadas:</b> {b_lat:.5f}, {b_lon:.5f}<br/>
                <div style="margin-top: 8px; padding: 5px; background: #FFEBEE; border-left: 3px solid #C62828; font-size: 11px;">
                    {'<b>Otimização:</b> 1 posto em entroncamento bloqueia múltiplas saídas/entradas.' if is_junction else '<b>Ação:</b> Barreira de desinfecção e fiscalização sanitária.'}
                </div>
            </div>
            """
            
            folium.Marker(
                location=[b_lat, b_lon],
                icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
                tooltip=f"🛑 {b_id}: {r_name}",
                popup=folium.Popup(popup_html, max_width=290)
            ).add_to(fg_barriers)
            
        fg_barriers.add_to(m)

    # 8. Controles e Plugins Adicionais
    folium.LayerControl(collapsed=False).add_to(m)
    Fullscreen().add_to(m)
    MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(m)

    # 9. Salvar se solicitado
    if save_html_path:
        m.save(save_html_path)
        logger.info(f"Mapa interativo salvo com sucesso em: {save_html_path}")

    return m
