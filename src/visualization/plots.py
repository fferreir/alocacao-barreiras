"""
Módulo para geração de gráficos de trade-off e sensibilidade de alocação de barreiras.
"""
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import logging

logger = logging.getLogger(__name__)


def plot_sensitivity_curves(
    sensitivity_df: pd.DataFrame,
    save_path: Optional[str] = None,
    recommended_radius: Optional[float] = None
) -> plt.Figure:
    """
    Gera gráfico com curvas de trade-off:
    Eixo Primário (Esquerda): Número de Bloqueios Viários Necessários.
    Eixo Secundário (Direita): Área Total da Zona de Contenção (km²).
    
    Args:
        sensitivity_df: DataFrame gerado por run_sensitivity_analysis.
        save_path: Caminho para salvar a imagem (.png ou .pdf).
        recommended_radius: Raio destacado como cenário recomendado.
        
    Returns:
        Figura do Matplotlib.
    """
    # Configurar estilo visual moderno
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
    
    color_barriers = "#D32F2F"  # Vermelho para barreiras
    color_area = "#1976D2"      # Azul para área

    # Coluna de barreiras (compatibilidade)
    barriers_col = "num_barreiras_mincut" if "num_barreiras_mincut" in sensitivity_df.columns else "num_barreiras"

    lines = []
    if "num_barreiras_geometrico" in sensitivity_df.columns:
        line_geom = ax1.plot(
            sensitivity_df["buffer_km"],
            sensitivity_df["num_barreiras_geometrico"],
            color="#757575",
            marker="^",
            linestyle="-.",
            linewidth=2.0,
            markersize=6,
            label="Estratégia Geométrica Convencional"
        )
        lines.extend(line_geom)

    # Curva 1: Número de Bloqueios Min-Cut
    line1 = ax1.plot(
        sensitivity_df["buffer_km"],
        sensitivity_df[barriers_col],
        color=color_barriers,
        marker="o",
        linewidth=2.5,
        markersize=7,
        label="Min-Cut Híbrido (Proposto)"
    )
    lines.extend(line1)
    ax1.set_xlabel("Raio do Buffer em Torno dos Focos (km)", fontsize=12, fontweight="bold", labelpad=10)
    ax1.set_ylabel("Quantidade de Bloqueios / Postos", color=color_barriers, fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_barriers)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Curva 2: Área de Contenção
    ax2 = ax1.twinx()
    line2 = ax2.plot(
        sensitivity_df["buffer_km"],
        sensitivity_df["area_total_km2"],
        color=color_area,
        marker="s",
        linestyle="--",
        linewidth=2.0,
        markersize=6,
        label="Área Total Contida (km²)"
    )
    lines.extend(line2)
    ax2.set_ylabel("Área Total da Zona Infectada (km²)", color=color_area, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color_area)
    ax2.grid(False)  # evitar sobreposição de grids

    # Destaque de ponto recomendado se fornecido
    if recommended_radius is not None:
        rec_row = sensitivity_df[sensitivity_df["buffer_km"] == recommended_radius]
        if not rec_row.empty:
            ax1.axvline(x=recommended_radius, color="#388E3C", linestyle=":", linewidth=2, label=f"Recomendado ({recommended_radius} km)")
            ax1.scatter(
                [recommended_radius],
                rec_row[barriers_col],
                color="#388E3C",
                s=120,
                zorder=5
            )

    # Legenda unificada
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

    plt.title("Análise de Sensibilidade: Raio do Buffer vs. Barreiras Sanitárias", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        logger.info(f"Gráfico de sensibilidade salvo em: {save_path}")

    return fig


def plot_barrier_classes(
    barriers_gdf: gpd.GeoDataFrame,
    save_path: Optional[str] = None
) -> Optional[plt.Figure]:
    """
    Gera gráfico de barras com a distribuição de bloqueios por classe de via.
    """
    if barriers_gdf.empty or "road_class" not in barriers_gdf.columns:
        return None
        
    counts = barriers_gdf["road_class"].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    colors = ["#C62828", "#E65100", "#F57C00", "#388E3C", "#757575"]
    
    counts.plot(kind="barh", ax=ax, color=colors[:len(counts)], edgecolor="black", alpha=0.85)
    ax.set_title("Distribuição de Bloqueios por Classe de Via", fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Quantidade de Postos", fontsize=11, fontweight="bold")
    ax.set_ylabel("Classe da Via", fontsize=11, fontweight="bold")
    
    # Rótulos nas barras
    for i, v in enumerate(counts):
        ax.text(v + 0.1, i, f" {v}", va="center", fontweight="bold", fontsize=10)
        
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        logger.info(f"Gráfico de classes de vias salvo em: {save_path}")
        
    return fig
