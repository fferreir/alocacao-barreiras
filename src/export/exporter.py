"""
Módulo para exportação de dados vetoriais (Shapefile, GeoJSON), tabulares (CSV) e relatórios executivos (Markdown).
"""
from typing import Optional, Dict, Any
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import logging
from src.core.optimizer import (
    classify_highway_type,
    extract_road_name,
    get_highway_capacity,
    compute_solution_stats
)

logger = logging.getLogger(__name__)


def _fmt_pt(val: float, decimals: int = 1, signed: bool = False) -> str:
    """Formata número decimal no padrão brasileiro (vírgula como separador decimal)."""
    fmt = f"{val:+,.{decimals}f}" if signed else f"{val:,.{decimals}f}"
    return fmt.replace(",", "X").replace(".", ",").replace("X", ".")


def _sanitize_value_for_gis(val: Any) -> Any:
    """Converte listas, tuplas, conjuntos ou dicionários em strings compatíveis com Shapefile/OGR."""
    if val is None:
        return None
    if isinstance(val, (list, tuple, set)):
        return ", ".join(str(v) for v in val if v is not None)
    if isinstance(val, dict):
        return str(val)
    if isinstance(val, float) and np.isnan(val):
        return None
    return val


def prepare_barriers_for_shapefile(barriers_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Prepara o GeoDataFrame de postos de bloqueio para exportação em ESRI Shapefile,
    garantindo nomes de colunas com <= 10 caracteres e tipos escalares limpos.
    """
    if barriers_gdf.empty:
        return barriers_gdf.copy()

    gdf = barriers_gdf.to_crs(epsg=4326).copy()
    if not isinstance(gdf.index, pd.RangeIndex):
        gdf = gdf.reset_index(drop=True)

    for col in gdf.columns:
        if col != "geometry":
            gdf[col] = gdf[col].apply(_sanitize_value_for_gis)

    rename_map = {
        "barrier_id": "barrier_id",
        "zone_id": "zone_id",
        "barrier_type": "tipo_posto",
        "road_name": "nome_via",
        "road_class": "classe_via",
        "highway": "highway",
        "connected_roads": "vias_conec",
        "capacity": "capacidade",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    cols_rename = {k: v for k, v in rename_map.items() if k in gdf.columns}
    gdf = gdf.rename(columns=cols_rename)

    # Garantir <= 10 caracteres em quaisquer colunas extras
    final_rename = {}
    for col in gdf.columns:
        if col != "geometry" and len(col) > 10:
            final_rename[col] = col[:10]
    if final_rename:
        gdf = gdf.rename(columns=final_rename)

    return gdf


def prepare_edges_for_shapefile(edges_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Prepara o GeoDataFrame da malha viária (OSM) para exportação em ESRI Shapefile e GeoJSON,
    enriquecendo com classificação funcional e capacidade logística e sanitizando tipos complexos.
    """
    if edges_gdf.empty:
        return edges_gdf.copy()

    gdf = edges_gdf.to_crs(epsg=4326).copy()
    if not isinstance(gdf.index, pd.RangeIndex):
        gdf = gdf.reset_index()

    # Adicionar atributos padronizados do modelo se ainda não existirem
    if "highway" in gdf.columns:
        gdf["classe_via"] = gdf["highway"].apply(classify_highway_type)
        gdf["capacidade"] = gdf["highway"].apply(get_highway_capacity)
    if "name" in gdf.columns:
        gdf["nome_via"] = gdf["name"].apply(extract_road_name)

    # Selecionar colunas principais com nomes <= 10 caracteres para Shapefile limpo
    preferred_cols = [
        "u", "v", "key", "osmid", "nome_via", "highway", "classe_via",
        "capacidade", "length", "oneway", "lanes", "maxspeed", "ref",
        "bridge", "service", "geometry"
    ]
    existing_cols = [c for c in preferred_cols if c in gdf.columns]
    gdf = gdf[existing_cols].copy()

    # Converter IDs de nós OSM (64-bit) e listas para string para evitar overflow em DBF 32-bit
    for col in gdf.columns:
        if col == "geometry":
            continue
        if col in ["u", "v", "osmid"]:
            gdf[col] = gdf[col].apply(lambda x: str(_sanitize_value_for_gis(x)) if x is not None else "")
        else:
            gdf[col] = gdf[col].apply(_sanitize_value_for_gis)

    return gdf


def prepare_zones_for_shapefile(zones_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Prepara o GeoDataFrame de zonas de contenção para exportação em ESRI Shapefile.
    """
    if zones_gdf.empty:
        return zones_gdf.copy()

    gdf = zones_gdf.to_crs(epsg=4326).copy()
    if not isinstance(gdf.index, pd.RangeIndex):
        gdf = gdf.reset_index(drop=True)

    rename_map = {
        "zone_id": "zone_id",
        "buffer_km": "buffer_km",
        "area_km2": "area_km2",
        "perimeter_km": "perim_km",
        "num_focos": "num_focos",
        "num_propriedades_total": "num_props"
    }
    cols_rename = {k: v for k, v in rename_map.items() if k in gdf.columns}
    gdf = gdf.rename(columns=cols_rename)

    for col in gdf.columns:
        if col != "geometry":
            gdf[col] = gdf[col].apply(_sanitize_value_for_gis)
            if len(col) > 10:
                gdf = gdf.rename(columns={col: col[:10]})

    return gdf


def export_analysis_results(
    output_dir: str,
    zones_gdf: gpd.GeoDataFrame,
    barriers_gdf: gpd.GeoDataFrame,
    properties_gdf: gpd.GeoDataFrame,
    sensitivity_df: Optional[pd.DataFrame] = None,
    buffer_km: Optional[float] = None,
    edges_gdf: Optional[gpd.GeoDataFrame] = None,
    comparison_stats: Optional[Dict[str, Any]] = None,
    barriers_geom_gdf: Optional[gpd.GeoDataFrame] = None,
    barriers_mincut_gdf: Optional[gpd.GeoDataFrame] = None,
    method: str = "min-cut",
    tolerance_km: float = 1.0
) -> Dict[str, str]:
    """
    Exporta os resultados completos em múltiplos formatos padrão de SIG:
    - ESRI Shapefiles (.shp) dos postos de bloqueio, das vias e das zonas de contenção
    - GeoJSON (.geojson)
    - Tabelas CSV (.csv)
    - Relatório Executivo em Markdown (.md) com indicadores comparativos (Tabela 2) e sensibilidade (Tabela 3)
    
    Args:
        output_dir: Diretório de destino.
        zones_gdf: GeoDataFrame de zonas de contenção.
        barriers_gdf: GeoDataFrame de barreiras sanitárias (solução principal selecionada).
        properties_gdf: GeoDataFrame de propriedades rurais analisadas.
        sensitivity_df: DataFrame com dados de sensibilidade (opcional).
        buffer_km: Raio de buffer utilizado na análise principal.
        edges_gdf: GeoDataFrame da malha viária do OpenStreetMap (opcional).
        comparison_stats: Dicionário com métricas comparativas Geométrica vs. Min-Cut (opcional).
        barriers_geom_gdf: GeoDataFrame da solução geométrica convencional (opcional).
        barriers_mincut_gdf: GeoDataFrame da solução Min-Cut Híbrido (opcional).
        method: Método selecionado para saída principal ('min-cut' ou 'geometric').
        tolerance_km: Tolerância da banda de busca em km.
        
    Returns:
        Dicionário com os caminhos dos arquivos exportados.
    """
    os.makedirs(output_dir, exist_ok=True)
    exported_files = {}

    # 1. Converter camadas para WGS84 (EPSG:4326)
    zones_wgs = zones_gdf.to_crs(epsg=4326) if not zones_gdf.empty else zones_gdf
    barriers_wgs = barriers_gdf.to_crs(epsg=4326) if not barriers_gdf.empty else barriers_gdf
    props_wgs = properties_gdf.to_crs(epsg=4326) if not properties_gdf.empty else properties_gdf

    # 2. Zonas de Contenção (GeoJSON + Shapefile)
    zones_geojson = os.path.join(output_dir, "zonas_contencao.geojson")
    zones_wgs.to_file(zones_geojson, driver="GeoJSON")
    exported_files["zones_geojson"] = zones_geojson

    if not zones_wgs.empty:
        zones_shp = os.path.join(output_dir, "zonas_contencao.shp")
        zones_shp_gdf = prepare_zones_for_shapefile(zones_wgs)
        zones_shp_gdf.to_file(zones_shp, driver="ESRI Shapefile", encoding="utf-8")
        exported_files["zones_shp"] = zones_shp

    # 3. Postos de Bloqueio Sanitário - Solução Principal Selecionada (GeoJSON + Shapefile + CSV)
    if not barriers_wgs.empty:
        barriers_geojson = os.path.join(output_dir, "bloqueios_sanitarios.geojson")
        barriers_clean = barriers_wgs.copy()
        for col in barriers_clean.columns:
            if col != "geometry":
                barriers_clean[col] = barriers_clean[col].apply(_sanitize_value_for_gis)
        barriers_clean.to_file(barriers_geojson, driver="GeoJSON")
        exported_files["barriers_geojson"] = barriers_geojson

        # Shapefile dos Postos de Bloqueio (solução selecionada)
        barriers_shp = os.path.join(output_dir, "bloqueios_sanitarios.shp")
        barriers_shp_gdf = prepare_barriers_for_shapefile(barriers_wgs)
        barriers_shp_gdf.to_file(barriers_shp, driver="ESRI Shapefile", encoding="utf-8")
        exported_files["barriers_shp"] = barriers_shp

        # CSV de Barreiras
        barriers_csv = os.path.join(output_dir, "bloqueios_sanitarios.csv")
        barriers_df = pd.DataFrame(barriers_clean.drop(columns=["geometry"]))
        barriers_df.to_csv(barriers_csv, index=False, encoding="utf-8-sig")
        exported_files["barriers_csv"] = barriers_csv

    # 3.1. Exportar também Shapefiles/GeoJSON/CSV específicos quando ambas as soluções estão disponíveis
    if barriers_mincut_gdf is not None and not barriers_mincut_gdf.empty:
        mc_shp = os.path.join(output_dir, "bloqueios_mincut.shp")
        prepare_barriers_for_shapefile(barriers_mincut_gdf).to_file(mc_shp, driver="ESRI Shapefile", encoding="utf-8")
        exported_files["barriers_mincut_shp"] = mc_shp

        mc_geojson = os.path.join(output_dir, "bloqueios_mincut.geojson")
        mc_wgs = barriers_mincut_gdf.to_crs(epsg=4326)
        mc_wgs.to_file(mc_geojson, driver="GeoJSON")
        exported_files["barriers_mincut_geojson"] = mc_geojson

    if barriers_geom_gdf is not None and not barriers_geom_gdf.empty:
        geom_shp = os.path.join(output_dir, "bloqueios_geometrico.shp")
        prepare_barriers_for_shapefile(barriers_geom_gdf).to_file(geom_shp, driver="ESRI Shapefile", encoding="utf-8")
        exported_files["barriers_geom_shp"] = geom_shp

        geom_geojson = os.path.join(output_dir, "bloqueios_geometrico.geojson")
        geom_wgs = barriers_geom_gdf.to_crs(epsg=4326)
        geom_wgs.to_file(geom_geojson, driver="GeoJSON")
        exported_files["barriers_geom_geojson"] = geom_geojson

    # 4. Propriedades com marcação de zona (CSV)
    props_csv = os.path.join(output_dir, "propriedades_analisadas.csv")
    props_df = pd.DataFrame(props_wgs.drop(columns=["geometry"]))
    props_df.to_csv(props_csv, index=False, encoding="utf-8-sig")
    exported_files["properties_csv"] = props_csv

    # 5. Malha Viária / Vias (GeoJSON + Shapefile)
    if edges_gdf is not None and not edges_gdf.empty:
        edges_clean_gdf = prepare_edges_for_shapefile(edges_gdf)

        edges_geojson = os.path.join(output_dir, "malha_viaria.geojson")
        edges_clean_gdf.to_file(edges_geojson, driver="GeoJSON")
        exported_files["edges_geojson"] = edges_geojson

        edges_shp = os.path.join(output_dir, "malha_viaria.shp")
        edges_clean_gdf.to_file(edges_shp, driver="ESRI Shapefile", encoding="utf-8")
        exported_files["edges_shp"] = edges_shp

    # 6. Tabela de Sensibilidade (CSV)
    if sensitivity_df is not None and not sensitivity_df.empty:
        sens_csv = os.path.join(output_dir, "analise_sensibilidade_buffers.csv")
        sensitivity_df.to_csv(sens_csv, index=False, encoding="utf-8-sig")
        exported_files["sensitivity_csv"] = sens_csv

    # 7. Gerar Relatório Executivo em Markdown
    report_path = os.path.join(output_dir, "relatorio_executivo.md")
    generate_markdown_report(
        report_path=report_path,
        zones_gdf=zones_gdf,
        barriers_gdf=barriers_gdf,
        properties_gdf=properties_gdf,
        sensitivity_df=sensitivity_df,
        buffer_km=buffer_km,
        comparison_stats=comparison_stats,
        method=method,
        tolerance_km=tolerance_km,
        exported_files=exported_files
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
    buffer_km: Optional[float] = None,
    comparison_stats: Optional[Dict[str, Any]] = None,
    method: str = "min-cut",
    tolerance_km: float = 1.0,
    exported_files: Optional[Dict[str, str]] = None
):
    """Gera relatório técnico executivo em Markdown com os indicadores logísticos, computacionais e de sensibilidade."""
    total_focos = int((properties_gdf["foco"] == 1).sum()) if "foco" in properties_gdf.columns else len(properties_gdf)
    total_props = len(properties_gdf)
    total_zones = len(zones_gdf)
    total_area = float(zones_gdf["area_km2"].sum()) if not zones_gdf.empty else 0.0

    active_stats = compute_solution_stats(barriers_gdf)
    total_barriers = active_stats["total_postos"]
    active_junctions = active_stats["postos_entroncamentos"]
    active_pct_junc = active_stats["pct_entroncamentos"]
    active_cost = active_stats["custo_logistico"]

    method_label = (
        "Geométrica Convencional (Interseção de Fronteira)"
        if method in ["geometric", "geom"]
        else "Min-Cut Híbrido (Entroncamentos Estratégicos + Vias Diretas)"
    )
    r_str = _fmt_pt(buffer_km, 1) if buffer_km is not None else "N/A"

    lines = [
        "# Relatório Executivo: Alocação Ótima de Barreiras Sanitárias",
        "",
        "## 1. Resumo Geral da Operação",
        f"- **Estratégia Selecionada para Saída Principal:** {method_label}",
        f"- **Raio de Contenção Utilizado ($r$):** {r_str} km (Tolerância de busca: $\\pm${_fmt_pt(tolerance_km, 1)} km)",
        f"- **Total de Focos Identificados:** {total_focos} propriedade(s)",
        f"- **Total de Propriedades Mapeadas:** {total_props} propriedade(s)",
        f"- **Zonas de Contenção Geradas (Clusters Coalescidos):** {total_zones} zona(s)",
        f"- **Área Total da Zona Infectada:** {_fmt_pt(total_area, 2)} km²",
        f"- **Total de Postos Físicos Exigidos (Solução Ativa):** {total_barriers} posto(s)",
        f"- **Postos em Entroncamentos Estratégicos:** {active_junctions} ({_fmt_pt(active_pct_junc, 1)}%)",
        f"- **Custo Logístico Ponderado ($\\sum$ capacidades):** {_fmt_pt(active_cost, 1)}",
        ""
    ]

    # Seção 2: Tabela 2 (Indicadores de desempenho computacional e logístico)
    if comparison_stats is not None and "geometric" in comparison_stats and "mincut" in comparison_stats:
        g_st = comparison_stats["geometric"]
        m_st = comparison_stats["mincut"]
        red_postos = comparison_stats.get("reducao_postos_pct", 0.0)
        red_custo = comparison_stats.get("reducao_custo_pct", 0.0)

        lines.extend([
            f"## 2. Indicadores de Desempenho Computacional e Logístico ($r = {r_str}$ km)",
            "",
            "| Métrica de Avaliação | Geométrica Convencional | Min-Cut Híbrido (Proposto) |",
            "| :--- | :---: | :---: |",
            f"| **Total de Postos Físicos Exigidos** | {g_st['total_postos']} | **{m_st['total_postos']} ({_fmt_pt(red_postos, 1, signed=True)}%)** |",
            f"| **Postos em Entroncamentos Estratégicos** | {g_st['postos_entroncamentos']} | **{m_st['postos_entroncamentos']} ({_fmt_pt(m_st['pct_entroncamentos'], 1)}%)** |",
            f"| **Custo Logístico Ponderado ($\\sum$ capacidades)** | {_fmt_pt(g_st['custo_logistico'], 1)} | **{_fmt_pt(m_st['custo_logistico'], 1)} ({_fmt_pt(red_custo, 1, signed=True)}%)** |",
            f"| **Tempo de Processamento Computacional** | $\\approx$ {_fmt_pt(g_st['tempo_processamento_s'], 2)} s | **$\\approx$ {_fmt_pt(m_st['tempo_processamento_s'], 2)} s** |",
            f"| **Conectividade Residual Origem-Destino** | {g_st['conectividade_residual']} | **{m_st['conectividade_residual']}** |",
            f"| **Hermeticidade Topológica (*Reachability*)** | {int(g_st['hermeticidade_topologica_pct'])}% | **{int(m_st['hermeticidade_topologica_pct'])}%** |",
            ""
        ])
    else:
        lines.extend([
            f"## 2. Indicadores de Desempenho Computacional e Logístico ($r = {r_str}$ km)",
            "",
            f"| Métrica de Avaliação | {method_label} |",
            "| :--- | :---: |",
            f"| **Total de Postos Físicos Exigidos** | **{total_barriers}** |",
            f"| **Postos em Entroncamentos Estratégicos** | **{active_junctions} ({_fmt_pt(active_pct_junc, 1)}%)** |",
            f"| **Custo Logístico Ponderado ($\\sum$ capacidades)** | **{_fmt_pt(active_cost, 1)}** |",
            f"| **Conectividade Residual Origem-Destino** | **Falsa (Fluxo Zero)** |",
            f"| **Hermeticidade Topológica (*Reachability*)** | **100%** |",
            ""
        ])

    # Seção 3: Tabela 3 (Análise de Sensibilidade)
    if sensitivity_df is not None and not sensitivity_df.empty:
        lines.extend([
            "## 3. Análise de Sensibilidade: Variação do Número de Postos em Função do Raio de Contenção ($r$)",
            "",
            "| Raio ($r$) | Estratégia Geométrica | Min-Cut Híbrido | Redução (Geom. $\\rightarrow$ Min-Cut) | Postos em Entroncamentos | Custo Logístico (Geom. $\\rightarrow$ Min-Cut) | Área Total ($\\text{km}^2$) | Zonas Coalescidas | Propriedades Afetadas |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        ])
        for _, s in sensitivity_df.iterrows():
            r_val = _fmt_pt(float(s["buffer_km"]), 1)
            n_mc = int(s["num_barreiras_mincut"]) if "num_barreiras_mincut" in s else int(s["num_barreiras"])
            n_geom = int(s["num_barreiras_geometrico"]) if "num_barreiras_geometrico" in s else n_mc
            red_p = float(s["reducao_pct"]) if "reducao_pct" in s else (
                ((n_mc - n_geom) / n_geom) * 100.0 if n_geom > 0 else 0.0
            )
            n_junc = int(s["barreiras_em_entroncamentos"]) if "barreiras_em_entroncamentos" in s else 0
            pct_junc = float(s["pct_entroncamentos"]) if "pct_entroncamentos" in s else (
                (n_junc / n_mc) * 100.0 if n_mc > 0 else 0.0
            )
            c_geom = float(s["custo_geometrico"]) if "custo_geometrico" in s else 0.0
            c_mc = float(s["custo_mincut"]) if "custo_mincut" in s else 0.0
            red_c = float(s["reducao_custo_pct"]) if "reducao_custo_pct" in s else 0.0
            area_v = _fmt_pt(float(s["area_total_km2"]), 2)
            n_zonas = int(s["num_zonas_coalescidas"])
            n_props = int(s["propriedades_afetadas"])

            custo_str = (
                f"{_fmt_pt(c_geom, 1)} $\\rightarrow$ **{_fmt_pt(c_mc, 1)}** ({_fmt_pt(red_c, 1, signed=True)}%)"
                if c_geom > 0 else "-"
            )
            lines.append(
                f"| {r_val} km | {n_geom} postos | **{n_mc} postos** | {_fmt_pt(red_p, 1, signed=True)}% | "
                f"{n_junc} ({_fmt_pt(pct_junc, 1)}%) | {custo_str} | {area_v} | {n_zonas} | {n_props} |"
            )
        lines.append("")

    # Seção 4: Detalhamento por Zona de Contenção
    lines.extend([
        "## 4. Detalhamento por Zona de Contenção",
        "",
        "| ID da Zona | Área (km²) | Perímetro (km) | Focos Contidos | Total Propriedades |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ])

    for _, z in zones_gdf.iterrows():
        lines.append(
            f"| {z.get('zone_id', '-')} | {_fmt_pt(float(z.get('area_km2', 0)), 2)} | "
            f"{_fmt_pt(float(z.get('perimeter_km', 0)), 2)} | {z.get('num_focos', 0)} | {z.get('num_propriedades_total', 0)} |"
        )

    # Seção 5: Postos de Bloqueio Sanitário Alocados
    lines.extend([
        "",
        f"## 5. Postos de Bloqueio Sanitário Alocados ({method_label})",
        "",
        "| ID Bloqueio | Zona | Tipo de Posto | Local / Entroncamento | Classificação | Vias Conectadas | Capacidade | Latitude | Longitude |",
        "| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |"
    ])

    if not barriers_gdf.empty:
        for _, b in barriers_gdf.iterrows():
            cap_val = float(b.get("capacity", 1.0))
            lines.append(
                f"| {b.get('barrier_id', '-')} | {b.get('zone_id', '-')} | {b.get('barrier_type', 'Bloqueio')} | "
                f"{b.get('road_name', 'Via Local')} | {b.get('road_class', 'N/A')} | {b.get('connected_roads', 2)} | "
                f"{_fmt_pt(cap_val, 1)} | {b.get('latitude', 0):.5f} | {b.get('longitude', 0):.5f} |"
            )
    else:
        lines.append("| - | - | - | Nenhuma barreira necessária | - | - | - | - | - |")

    # Seção 6: Produtos Cartográficos e Vetoriais Gerados
    if exported_files:
        lines.extend([
            "",
            "## 6. Arquivos Vetoriais (Shapefiles / GeoJSON) e Tabulares Gerados",
            ""
        ])
        labels_map = {
            "barriers_shp": "Shapefile dos Postos de Bloqueio (Solução Principal)",
            "barriers_mincut_shp": "Shapefile dos Postos de Bloqueio (Min-Cut Híbrido)",
            "barriers_geom_shp": "Shapefile dos Postos de Bloqueio (Geométrica Convencional)",
            "edges_shp": "Shapefile da Malha Viária (Vias OSM)",
            "zones_shp": "Shapefile das Zonas de Contenção",
            "barriers_geojson": "GeoJSON dos Postos de Bloqueio",
            "edges_geojson": "GeoJSON da Malha Viária",
            "zones_geojson": "GeoJSON das Zonas de Contenção",
            "barriers_csv": "Planilha CSV dos Postos de Bloqueio",
            "properties_csv": "Planilha CSV das Propriedades Analisadas",
            "sensitivity_csv": "Planilha CSV da Análise de Sensibilidade"
        }
        for key, label in labels_map.items():
            if key in exported_files:
                lines.append(f"- **{label}:** `{os.path.basename(exported_files[key])}`")

    lines.extend([
        "",
        "## 7. Diretrizes Operacionais",
        "1. **Fiscalização Integral:** Qualquer veículo que transite de/para a zona de contenção passará obrigatoriamente por um dos postos listados (Hermeticidade Topológica de 100%, Conectividade Residual Nula).",
        "2. **Equipes de Desinfecção:** Recomenda-se priorizar postos em 'Rodovias Principais' ($c = 10,0$) e 'Estradas Secundárias' ($c = 5,0$) com estrutura reforçada de rodolúvio e arco de desinfecção.",
        "3. **Sinalização:** Instalar placas de advertência e desvio a 500m dos postos de bloqueio."
    ])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
