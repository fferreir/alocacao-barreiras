"""
Módulo para exportação de dados vetoriais, tabulares e relatórios executivos.
"""
from typing import Optional, Dict, Any
import os
import geopandas as gpd
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def export_analysis_results(
    output_dir: str,
    zones_gdf: gpd.GeoDataFrame,
    barriers_gdf: gpd.GeoDataFrame,
    properties_gdf: gpd.GeoDataFrame,
    sensitivity_df: Optional[pd.DataFrame] = None,
    buffer_km: Optional[float] = None,
    edges_gdf: Optional[gpd.GeoDataFrame] = None
) -> Dict[str, str]:
    """
    Exporta os resultados completos em múltiplos formatos padrão de SIG (GeoJSON, GeoPackage, CSV, Markdown).
    
    Args:
        output_dir: Diretório de destino.
        zones_gdf: GeoDataFrame de zonas de contenção.
        barriers_gdf: GeoDataFrame de barreiras sanitárias.
        properties_gdf: GeoDataFrame de propriedades rurais analisadas.
        sensitivity_df: DataFrame com dados de sensibilidade (opcional).
        buffer_km: Raio de buffer utilizado na análise principal.
        
    Returns:
        Dicionário com os caminhos dos arquivos exportados.
    """
    os.makedirs(output_dir, exist_ok=True)
    exported_files = {}

    # 1. Exportar GeoJSON (WGS84 EPSG:4326)
    zones_wgs = zones_gdf.to_crs(epsg=4326) if not zones_gdf.empty else zones_gdf
    barriers_wgs = barriers_gdf.to_crs(epsg=4326) if not barriers_gdf.empty else barriers_gdf
    props_wgs = properties_gdf.to_crs(epsg=4326) if not properties_gdf.empty else properties_gdf

    # Zonas de Contenção
    zones_geojson = os.path.join(output_dir, "zonas_contencao.geojson")
    zones_wgs.to_file(zones_geojson, driver="GeoJSON")
    exported_files["zones_geojson"] = zones_geojson

    # Bloqueios Sanitários
    if not barriers_wgs.empty:
        barriers_geojson = os.path.join(output_dir, "bloqueios_sanitarios.geojson")
        barriers_wgs.to_file(barriers_geojson, driver="GeoJSON")
        exported_files["barriers_geojson"] = barriers_geojson

        # CSV de Barreiras
        barriers_csv = os.path.join(output_dir, "bloqueios_sanitarios.csv")
        barriers_df = pd.DataFrame(barriers_wgs.drop(columns=["geometry"]))
        barriers_df.to_csv(barriers_csv, index=False, encoding="utf-8-sig")
        exported_files["barriers_csv"] = barriers_csv

    # Propriedades com marcação de zona
    props_csv = os.path.join(output_dir, "propriedades_analisadas.csv")
    props_df = pd.DataFrame(props_wgs.drop(columns=["geometry"]))
    props_df.to_csv(props_csv, index=False, encoding="utf-8-sig")
    exported_files["properties_csv"] = props_csv

    # Malha Viária (Vetor)
    if edges_gdf is not None and not edges_gdf.empty:
        edges_wgs = edges_gdf.to_crs(epsg=4326)
        edges_geojson = os.path.join(output_dir, "malha_viaria.geojson")
        edges_wgs.to_file(edges_geojson, driver="GeoJSON")
        exported_files["edges_geojson"] = edges_geojson

    # 2. Tabela de Sensibilidade
    if sensitivity_df is not None and not sensitivity_df.empty:
        sens_csv = os.path.join(output_dir, "analise_sensibilidade_buffers.csv")
        sensitivity_df.to_csv(sens_csv, index=False, encoding="utf-8-sig")
        exported_files["sensitivity_csv"] = sens_csv

    # 3. Gerar Relatório Executivo em Markdown
    report_path = os.path.join(output_dir, "relatorio_executivo.md")
    generate_markdown_report(
        report_path=report_path,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        properties_gdf=properties_gdf,
        sensitivity_df=sensitivity_df,
        buffer_km=buffer_km
    )
    exported_files["report_md"] = report_path

    logger.info(f"Exportação finalizada. Arquivos salvos em: {output_dir}")
    return exported_files


def generate_markdown_report(
    report_path: str,
    zones_gdf: gpd.GeoDataFrame,
    barriers_gdf: gpd.GeoDataFrame,
    properties_gdf: gpd.GeoDataFrame,
    sensitivity_df: Optional[pd.DataFrame] = None,
    buffer_km: Optional[float] = None
):
    """Gera relatório técnico executivo em Markdown com os dados da operação."""
    total_focos = (properties_gdf["foco"] == 1).sum() if "foco" in properties_gdf.columns else len(properties_gdf)
    total_props = len(properties_gdf)
    total_zones = len(zones_gdf)
    total_area = zones_gdf["area_km2"].sum() if not zones_gdf.empty else 0.0
    total_barriers = len(barriers_gdf)

    lines = [
        "# Relatório Executivo: Alocação Ótima de Barreiras Sanitárias",
        "",
        "## 1. Resumo Geral da Operação",
        f"- **Raio de Buffer Utilizado:** {buffer_km if buffer_km is not None else 'N/A'} km",
        f"- **Total de Focos Identificados:** {total_focos} propriedade(s)",
        f"- **Total de Propriedades Mapeadas:** {total_props} propriedade(s)",
        f"- **Zonas de Contenção Geradas (Clusters Coalescidos):** {total_zones} zona(s)",
        f"- **Área Total da Zona Infectada:** {total_area:.2f} km²",
        f"- **Total de Postos de Bloqueio Viário Alocados:** {total_barriers} posto(s)",
        "",
        "## 2. Detalhamento por Zona de Contenção",
        "",
        "| ID da Zona | Área (km²) | Perímetro (km) | Focos Contidos | Total Propriedades |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for _, z in zones_gdf.iterrows():
        lines.append(
            f"| {z.get('zone_id', '-')} | {z.get('area_km2', 0):.2f} | "
            f"{z.get('perimeter_km', 0):.2f} | {z.get('num_focos', 0)} | {z.get('num_propriedades_total', 0)} |"
        )

    lines.extend([
        "",
        "## 3. Postos de Bloqueio Sanitário Alocados (Min-Cut / Entroncamentos)",
        "",
        "| ID Bloqueio | Zona | Tipo de Posto | Local / Entroncamento | Classificação | Vias Conectadas | Latitude | Longitude |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    if not barriers_gdf.empty:
        for _, b in barriers_gdf.iterrows():
            lines.append(
                f"| {b.get('barrier_id', '-')} | {b.get('zone_id', '-')} | {b.get('barrier_type', 'Bloqueio')} | "
                f"{b.get('road_name', 'Via Local')} | {b.get('road_class', 'N/A')} | {b.get('connected_roads', 2)} | "
                f"{b.get('latitude', 0):.5f} | {b.get('longitude', 0):.5f} |"
            )
    else:
        lines.append("| - | - | - | Nenhuma barreira necessária | - | - | - | - |")

    if sensitivity_df is not None and not sensitivity_df.empty:
        lines.extend([
            "",
            "## 4. Análise de Sensibilidade (Trade-off Raio vs. Bloqueios)",
            "",
            "| Raio Buffer (km) | Nº Bloqueios | Área Total (km²) | Nº Zonas Coalescidas | Propriedades Afetadas |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ])
        for _, s in sensitivity_df.iterrows():
            lines.append(
                f"| {s['buffer_km']:.2f} | {int(s['num_barreiras'])} | {s['area_total_km2']:.2f} | "
                f"{int(s['num_zonas_coalescidas'])} | {int(s['propriedades_afetadas'])} |"
            )

    lines.extend([
        "",
        "## 5. Diretrizes Operacionais",
        "1. **Fiscalização Integral:** Qualquer veículo que transite de/para a zona de contenção passará obrigatoriamente por um dos postos listados.",
        "2. **Equipes de Desinfecção:** Recomenda-se priorizar postos em 'Rodovias Principais' e 'Estradas Secundárias' com rodolúvio e arco de desinfecção.",
        "3. **Sinalização:** Instalar placas de advertência e desvio a 500m dos postos de bloqueio."
    ])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
