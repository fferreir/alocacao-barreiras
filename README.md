# 🛡️ Alocação Ótima de Barreiras Sanitárias Rurais

Aplicação em Python para determinação geoespacial ótima do número mínimo de bloqueios e barreiras sanitárias em malha viária (**OpenStreetMap**) para contenção epidemiológica de zonas rurais infectadas (buffers com coalescência espacial), permitindo escolher e comparar entre a **Estratégia Geométrica Convencional** e o **Teorema do Min-Cut / Max-Flow Híbrido** em entroncamentos estratégicos.

---

## 📌 Funcionalidades Principais

1. **Entrada de Camada de Propriedades**:
   - Suporte a Shapefile (`.shp`), GeoPackage (`.gpkg`) e GeoJSON (`.geojson`).
   - Leitura de coluna indicadora `foco` (1 para foco confirmado, 0 para propriedade sob controle/sadia).
   - Conversão automática para projeção métrica adequada (UTM / SIRGAS 2000).

2. **Zonas de Contenção com Coalescência Espacial**:
   - Criação de buffers parametrizados em quilômetros em torno das propriedades foco.
   - Fusão automática (*unary_union / dissolve*) de buffers sobrepostos em clusters únicos e polígonos isolados para focos distantes.
   - Contabilização da área ($km^2$), perímetro ($km$) e propriedades englobadas.

3. **Integração com OpenStreetMap (OSMnx)**:
   - Download automático da malha viária real para a região de estudo com margem de segurança.
   - Suporte a diferentes tipos de rede (`drive`, `all`, `drive_service`, `all_private`).

4. **Alocação Ótima de Bloqueios Viários (Min-Cut Híbrido vs. Geométrica Convencional)**:
   - **Min-Cut Híbrido (`--method min-cut`)**: Aplica *Vertex Splitting* em entroncamentos estratégicos na banda de busca ($\pm$ tolerância em km) combinado com corte de vias diretas, minimizando o número total de postos físicos e o custo logístico ponderado ($\sum$ capacidades).
   - **Geométrica Convencional (`--method geometric`)**: Aloca postos diretamente nas interseções geométricas entre as vias e o perímetro do buffer.
   - Garante formalmente **100% de Hermeticidade Topológica (*Reachability*)** e **Conectividade Residual Nula (Fluxo Zero)** entre os focos e o exterior.
   - Ponderação hierárquica de custo logístico por classe de via:
     - Rodovias Principais (`motorway`, `trunk`, `primary`): capacidade $c = 10,0$
     - Estradas Secundárias / Coletoras (`secondary`, `tertiary`): capacidade $c = 5,0$
     - Estradas Municipais e Acessos Rurais / Vicinais: capacidade $c = 1,0$
     - Entroncamentos Estratégicos (Min-Cut): capacidade $c = 1,0$

5. **Análise de Sensibilidade e Indicadores de Desempenho**:
   - **Tabela Comparativa de Desempenho Computacional e Logístico**: Compara automaticamente *Geométrica Convencional* vs. *Min-Cut Híbrido* em termos de total de postos físicos, postos em entroncamentos estratégicos, custo logístico ponderado ($\sum$ capacidades), tempo de processamento computacional, conectividade residual e hermeticidade topológica.
   - **Análise de Sensibilidade por Raio de Contenção**: Avalia múltiplos raios ($r$, ex: `3,0 km`, `5,0 km`, `7,0 km`, `10,0 km`) comparando o número de postos e a redução percentual entre a Estratégia Geométrica e o Min-Cut Híbrido.

6. **Visualização e Exportação SIG Completa**:
   - **Shapefiles (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`)**:
     - `bloqueios_sanitarios.shp`: Postos de bloqueio da solução selecionada (`min-cut` ou `geometric`).
     - `bloqueios_mincut.shp` e `bloqueios_geometrico.shp`: Camadas vetoriais individuais de ambas as estratégias para comparação em SIG (QGIS/ArcGIS).
     - `malha_viaria.shp`: Rede viária do OpenStreetMap enriquecida com classificação (`classe_via`) e peso logístico (`capacidade`).
     - `zonas_contencao.shp`: Polígonos coalescidos das zonas de contenção.
   - **GeoJSON e CSV**: `bloqueios_sanitarios.geojson`, `malha_viaria.geojson`, `zonas_contencao.geojson`, `bloqueios_sanitarios.csv`, `propriedades_analisadas.csv` e `analise_sensibilidade_buffers.csv`.
   - **Relatório Executivo em Markdown (`relatorio_executivo.md`)**: Documento completo contendo as estatísticas comparativas (Tabelas 2 e 3), detalhamento por zona, lista de postos com coordenadas/capacidades e arquivos gerados.
   - **Mapa Interativo Web (Folium / Leaflet)**: Gera `mapa_bloqueios_mincut.html` (quando `--method min-cut`) ou `mapa_bloqueios_geometrico.html` (quando `--method geometric`), com camadas e legendas ajustadas à estratégia selecionada.
   - **Gráficos em Alta Resolução (PNG)**: `distribuicao_classes_vias.png` e `curva_sensibilidade_mincut.png` / `curva_sensibilidade_geometrico.png`.

---

## 🚀 Instalação

```bash
git clone https://github.com/fferreir/alocacao-barreiras.git
cd alocacao-barreiras
pip install -r requirements.txt
```

---

## 💻 Como Usar

### 1. Linha de Comando (CLI)

#### Executar Cenário Piloto com Solução Min-Cut Híbrida (Padrão, $r = 3,0\text{ km}$):
```bash
python3 -m src.cli --input data/propriedades_rurais_exemplo.shp --buffer-km 3.0 --tolerance-km 1.0 --method min-cut --output-dir resultados
```

#### Exportar a Solução Geométrica Convencional como Saída Principal:
```bash
python3 -m src.cli --input data/propriedades_rurais_exemplo.shp --buffer-km 3.0 --method geometric --output-dir resultados_geometrico
```

#### Executar com Análise de Sensibilidade para Raios Específicos (3, 5, 7 e 10 km):
```bash
python3 -m src.cli --input data/propriedades_rurais_exemplo.shp --buffer-km 3.0 --sensitivity --radii 3.0 5.0 7.0 10.0 --output-dir resultados
```

#### Executar Sensibilidade por Intervalo (`--buffer-min`, `--buffer-max`, `--buffer-step`):
```bash
python3 -m src.cli --input data/propriedades_rurais_exemplo.shp --buffer-km 3.0 --sensitivity --buffer-min 2.0 --buffer-max 8.0 --buffer-step 2.0 --output-dir resultados
```

#### Parâmetros Disponíveis na CLI:
| Parâmetro | Atalho | Descrição | Padrão |
| :--- | :---: | :--- | :---: |
| `--input` | `-i` | Arquivo espacial de propriedades (`.shp`, `.gpkg`, `.geojson`) | *(Obrigatório)* |
| `--foco-col` | `-f` | Nome da coluna indicadora de foco (`1` = foco, `0` = sadia) | `foco` |
| `--buffer-km` | `-b` | Raio de contenção base ($r$) em quilômetros | `3.0` |
| `--tolerance-km` | `-t` | Banda de tolerância (km) para busca de entroncamentos no Min-Cut | `1.0` |
| `--method` | `-m` | Solução ativa de saída: `min-cut` (proposto) ou `geometric` (convencional) | `min-cut` |
| `--cut-mode` | `-c` | Modo de corte: `hybrid`, `junctions`, `edges` ou `geometric` | `hybrid` |
| `--sensitivity` | `-s` | Ativa a análise de sensibilidade (gera Tabela 3 e curva de trade-off) | `False` |
| `--radii` | - | Lista explícita de raios (km) para sensibilidade (ex: `--radii 3 5 7 10`) | `None` |
| `--buffer-min` | - | Raio mínimo (km) para varredura de sensibilidade | `3.0` |
| `--buffer-max` | - | Raio máximo (km) para varredura de sensibilidade | `10.0` |
| `--buffer-step` | - | Passo (km) para varredura de sensibilidade | `2.0` |
| `--network-type` | - | Filtro de malha OSM (`all`, `drive`, `drive_service`, `all_private`) | `all` |
| `--output-dir` | `-o` | Diretório de saída para Shapefiles, GeoJSON, CSV, HTML e relatório | `output` |

---

### 2. Demonstração Rápida Ponta a Ponta

```bash
python3 examples/run_demo.py
```

---

### 3. Como Biblioteca Python

```python
from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
from src.core.optimizer import compare_allocation_strategies
from src.export.exporter import export_analysis_results
from src.visualization.map_builder import build_interactive_map

# 1. Carregar propriedades
props_gdf = load_properties("data/propriedades_rurais_exemplo.shp", foco_col="foco")

# 2. Criar zonas infectadas (buffer de 3.0 km com coalescência)
zones_gdf, tagged_props = create_infected_zones(props_gdf, buffer_km=3.0, foco_col="foco")

# 3. Baixar vias do OpenStreetMap
G, edges_gdf, _ = download_road_network(zones_gdf, network_type="all", buffer_margin_km=2.0)

# 4. Executar e comparar as soluções Geométrica Convencional e Min-Cut Híbrido
res = compare_allocation_strategies(
    G=G,
    edges_gdf=edges_gdf,
    properties_gdf=props_gdf,
    zones_gdf=zones_gdf,
    buffer_km=3.0,
    tolerance_km=1.0,
    cut_mode="hybrid"
)
barriers_mincut = res["barriers_mincut"]
barriers_geom = res["barriers_geom"]
comparison_stats = res["comparison"]

# 5. Exportar Shapefiles (postos, vias e zonas), GeoJSON, CSV e Relatório Executivo
exported = export_analysis_results(
    output_dir="resultados",
    zones_gdf=zones_gdf,
    barriers_gdf=barriers_mincut,       # ou barriers_geom para saída geométrica
    properties_gdf=tagged_props,
    buffer_km=3.0,
    edges_gdf=edges_gdf,
    comparison_stats=comparison_stats,
    barriers_geom_gdf=barriers_geom,
    barriers_mincut_gdf=barriers_mincut,
    method="min-cut",
    tolerance_km=1.0
)

# 6. Gerar mapa interativo (method='min-cut' ou 'geometric')
build_interactive_map(
    properties_gdf=tagged_props,
    zones_gdf=zones_gdf,
    barriers_gdf=barriers_mincut,
    edges_gdf=edges_gdf,
    save_html_path="resultados/mapa_bloqueios_mincut.html",
    method="min-cut"
)
```

---

## 🧪 Testes Automatizados

Para executar os testes unitários e de integração:

```bash
python3 -m pytest tests/test_all.py -v
```

---

## 📁 Estrutura do Repositório

```
alocacao-barreiras/
├── data/                             # Amostras de dados de teste (Shapefile/GeoJSON)
├── examples/
│   └── run_demo.py                   # Script de demonstração comparativa ponta a ponta
├── src/
│   ├── core/
│   │   ├── loader.py                 # Validação e reprojeção de dados espaciais
│   │   ├── buffer.py                 # Criação e coalescência de zonas infectadas
│   │   ├── osm.py                    # Download e processamento da rede viária OSM
│   │   ├── optimizer.py              # Alocação Geométrica, Min-Cut Híbrido e métricas comparativas
│   │   └── sensitivity.py            # Análise de sensibilidade (Geométrica vs. Min-Cut)
│   ├── visualization/
│   │   ├── map_builder.py            # Geração de mapa interativo Folium
│   │   └── plots.py                  # Gráficos comparativos de trade-off e classes de vias
│   ├── export/
│   │   └── exporter.py               # Exportação SIG (Shapefiles, GeoJSON, CSV e Relatório Executivo)
│   └── cli.py                        # Interface de linha de comando
├── tests/
│   ├── generate_sample_data.py       # Gerador de base sintética de fazendas
│   └── test_all.py                   # Suíte de testes automatizados
└── requirements.txt                  # Dependências do projeto
```

---

## 📜 Licença
Distribuído sob a licença Apache 2.0. Consulte `LICENSE` para mais detalhes.
