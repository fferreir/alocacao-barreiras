# 🛡️ Alocação Ótima de Barreiras Sanitárias Rurais

Aplicação em Python para determinação geoespacial ótima do número mínimo de bloqueios e barreiras sanitárias em malha viária (**OpenStreetMap**) para contenção epidemiológica de zonas rurais infectadas (buffers com coalescência espacial).

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
   - Suporte a diferentes tipos de rede (`drive`, `all`, `drive_service`).

4. **Alocação Ótima de Bloqueios Viários**:
   - Identificação matemática exata das vias que cruzam o perímetro da zona de contenção.
   - Garante que **qualquer veículo que entre ou saia da zona de contenção passe obrigatoriamente por um posto de fiscalização/desinfecção**.
   - Classificação das vias (Rodovias Principais, Vias Coletoras, Estradas Municipais, Acessos Rurais e Vicinais).
   - Deduplicação inteligente de travessias duplicadas ou vias de mão dupla.

5. **Flexibilização e Análise de Sensibilidade do Buffer**:
   - Varredura paramétrica de raios de buffer para apoiar a tomada de decisão logística e orçamentária.
   - Curvas de Trade-off (Curva de Pareto: Raio do Buffer vs. Quantidade de Bloqueios vs. Área Contida).

6. **Visualização e Exportação**:
   - **Mapa Interativo Web (Folium / Leaflet)** com camadas comutáveis, popups informativos e satélite.
   - **Gráficos em Alta Resolução**: Curvas de sensibilidade e distribuição por classe de via.
   - **Exportação SIG**: GeoJSON, CSV, Shapefile e Relatório Executivo em Markdown.

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

#### Executar Cenário Operacional Simples (Buffer de 3.5 km):
```bash
python3 -m src.cli --input data/propriedades_rurais_exemplo.shp --buffer-km 3.5 --output-dir resultados
```

#### Executar com Análise de Sensibilidade de 1 km a 10 km:
```bash
python3 -m src.cli --input data/propriedades_rurais_exemplo.shp --buffer-km 4.0 --sensitivity --buffer-min 1.0 --buffer-max 10.0 --buffer-step 1.0 --output-dir resultados
```

### 2. Demonstração Rápida Ponta a Ponta

```bash
python3 examples/run_demo.py
```

### 3. Como Biblioteca Python

```python
from src.core.loader import load_properties
from src.core.buffer import create_infected_zones
from src.core.osm import download_road_network
from src.core.optimizer import allocate_barriers
from src.visualization.map_builder import build_interactive_map

# 1. Carregar propriedades
props_gdf = load_properties("caminho/para/propriedades.shp", foco_col="foco")

# 2. Criar zonas infectadas (buffer de 5 km com coalescência)
zones_gdf, tagged_props = create_infected_zones(props_gdf, buffer_km=5.0, foco_col="foco")

# 3. Baixar vias do OpenStreetMap
_, edges_gdf, _ = download_road_network(zones_gdf, network_type="drive")

# 4. Determinar bloqueios ótimos
barriers_gdf = allocate_barriers(edges_gdf, zones_gdf)

# 5. Gerar mapa interativo
build_interactive_map(
    properties_gdf=tagged_props,
    zones_gdf=zones_gdf,
    barriers_gdf=barriers_gdf,
    save_html_path="mapa_bloqueios.html"
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
│   └── run_demo.py                   # Script de demonstração rápida
├── src/
│   ├── core/
│   │   ├── loader.py                 # Validação e reprojeção de dados espaciais
│   │   ├── buffer.py                 # Criação e coalescência de zonas infectadas
│   │   ├── osm.py                    # Download e processamento da rede viária OSM
│   │   ├── optimizer.py              # Cálculo ótimo de pontos de bloqueio
│   │   └── sensitivity.py            # Análise de sensibilidade (Raio vs Bloqueios)
│   ├── visualization/
│   │   ├── map_builder.py            # Geração de mapa interativo Folium
│   │   └── plots.py                  # Gráficos de trade-off e classes de vias
│   ├── export/
│   │   └── exporter.py               # Exportação SIG (GeoJSON, CSV, Relatórios)
│   └── cli.py                        # Interface de linha de comando
├── tests/
│   ├── generate_sample_data.py       # Gerador de base sintética de fazendas
│   └── test_all.py                   # Suíte de testes automatizados
└── requirements.txt                  # Dependências do projeto
```

---

## 📜 Licença
Distribuído sob a licença Apache 2.0. Consulte `LICENSE` para mais detalhes.
