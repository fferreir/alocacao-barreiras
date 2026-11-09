# Relatório Executivo: Alocação Ótima de Barreiras Sanitárias

## 1. Resumo Geral da Operação
- **Estratégia Selecionada para Saída Principal:** Geométrica Convencional (Interseção de Fronteira)
- **Raio de Contenção Utilizado ($r$):** 3,0 km (Tolerância de busca: $\pm$1,5 km)
- **Total de Focos Identificados:** 4 propriedade(s)
- **Total de Propriedades Mapeadas:** 24 propriedade(s)
- **Zonas de Contenção Geradas (Clusters Coalescidos):** 2 zona(s)
- **Área Total da Zona Infectada:** 77,40 km²
- **Total de Postos Físicos Exigidos (Solução Ativa):** 215 posto(s)
- **Postos em Entroncamentos Estratégicos:** 0 (0,0%)
- **Custo Logístico Ponderado ($\sum$ capacidades):** 414,0

## 2. Indicadores de Desempenho Computacional e Logístico ($r = 3,0$ km)

| Métrica de Avaliação | Geométrica Convencional | Min-Cut Híbrido (Proposto) |
| :--- | :---: | :---: |
| **Total de Postos Físicos Exigidos** | 215 | **72 (-66,5%)** |
| **Postos em Entroncamentos Estratégicos** | 0 | **66 (91,7%)** |
| **Custo Logístico Ponderado ($\sum$ capacidades)** | 414,0 | **81,0 (-80,4%)** |
| **Tempo de Processamento Computacional** | $\approx$ 2,76 s | **$\approx$ 5,55 s** |
| **Conectividade Residual Origem-Destino** | Falsa (Fluxo Zero) | **Falsa (Fluxo Zero)** |
| **Hermeticidade Topológica (*Reachability*)** | 100% | **100%** |

## 4. Detalhamento por Zona de Contenção

| ID da Zona | Área (km²) | Perímetro (km) | Focos Contidos | Total Propriedades |
| :--- | :--- | :--- | :--- | :--- |
| ZONA_01 | 28,23 | 18,84 | 1 | 3 |
| ZONA_02 | 49,17 | 25,63 | 3 | 4 |

## 5. Postos de Bloqueio Sanitário Alocados (Geométrica Convencional (Interseção de Fronteira))

| ID Bloqueio | Zona | Tipo de Posto | Local / Entroncamento | Classificação | Vias Conectadas | Capacidade | Latitude | Longitude |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| BLOQ_001 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.81620 | -47.52272 |
| BLOQ_002 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.81366 | -47.54420 |
| BLOQ_003 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Secundária / Coletora | 2 | 5,0 | -22.81214 | -47.54680 |
| BLOQ_004 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.80565 | -47.55379 |
| BLOQ_005 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.79685 | -47.50178 |
| BLOQ_006 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.79352 | -47.50106 |
| BLOQ_007 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.79108 | -47.55915 |
| BLOQ_008 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.78302 | -47.50180 |
| BLOQ_009 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.77318 | -47.50711 |
| BLOQ_010 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.77173 | -47.50849 |
| BLOQ_011 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada Municipal Luiz Zangirolamo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.77218 | -47.55196 |
| BLOQ_012 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.76657 | -47.54457 |
| BLOQ_013 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.76971 | -47.54928 |
| BLOQ_014 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada 12 | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76453 | -47.53983 |
| BLOQ_015 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada 12 | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76566 | -47.54273 |
| BLOQ_016 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76533 | -47.51799 |
| BLOQ_017 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada 15 | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76318 | -47.53380 |
| BLOQ_018 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada 13 | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76394 | -47.53790 |
| BLOQ_019 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada Municipal Santa Isabel | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76504 | -47.51871 |
| BLOQ_020 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada 17 | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76403 | -47.52183 |
| BLOQ_021 | ZONA_01 | Fronteira Simples (Geométrica) | Estrada 16 | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76294 | -47.52930 |
| BLOQ_022 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76315 | -47.52630 |
| BLOQ_023 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76307 | -47.52710 |
| BLOQ_024 | ZONA_01 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.76304 | -47.52759 |
| BLOQ_025 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Luiz Soave | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75170 | -47.62964 |
| BLOQ_026 | ZONA_02 | Fronteira Simples (Geométrica) | Rua João Francisco de Oliveira | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75177 | -47.62921 |
| BLOQ_027 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Santa Catarina | Estrada Secundária / Coletora | 2 | 5,0 | -22.75198 | -47.62698 |
| BLOQ_028 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Leogildo Salvagni | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75189 | -47.62841 |
| BLOQ_029 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Professora Laudelina Cotrim de Castro | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75191 | -47.62814 |
| BLOQ_030 | ZONA_02 | Fronteira Simples (Geométrica) | Rua João Tedesco | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75194 | -47.62763 |
| BLOQ_031 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Angelina dos Santos Silva | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74611 | -47.60673 |
| BLOQ_032 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Fernando Rogério Batista Abreu | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75206 | -47.62521 |
| BLOQ_033 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Isaura Sebastião dos Santos | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75204 | -47.62451 |
| BLOQ_034 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Luiz Gomes de Oliveira | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75202 | -47.62382 |
| BLOQ_035 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Rio das Pedras | Estrada Secundária / Coletora | 2 | 5,0 | -22.75167 | -47.62003 |
| BLOQ_036 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Sidney Luiz Brajão | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75182 | -47.62121 |
| BLOQ_037 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Álvaro Correa de Toledo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75174 | -47.62058 |
| BLOQ_038 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Pompéia | Estrada Secundária / Coletora | 2 | 5,0 | -22.75021 | -47.61435 |
| BLOQ_039 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Benedito Campos Viriato | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74850 | -47.61056 |
| BLOQ_040 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Benedito Campos Viriato | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74823 | -47.61006 |
| BLOQ_041 | ZONA_02 | Fronteira Simples (Geométrica) | Rua José Benitiz Gregório | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74764 | -47.60900 |
| BLOQ_042 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.74892 | -47.63862 |
| BLOQ_043 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.74868 | -47.63915 |
| BLOQ_044 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Henrique Rochelle | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74977 | -47.63677 |
| BLOQ_045 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Comendador Luciano Guidotti | Estrada Secundária / Coletora | 2 | 5,0 | -22.74946 | -47.63745 |
| BLOQ_046 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Guilherme Hoeppner | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75063 | -47.63436 |
| BLOQ_047 | ZONA_02 | Fronteira Simples (Geométrica) | Rua José Elias de Morales | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75034 | -47.63518 |
| BLOQ_048 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Engenheiro Agrônomo Romano Coury | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75005 | -47.63601 |
| BLOQ_049 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ernani Braga | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75136 | -47.63159 |
| BLOQ_050 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Carmine Testa | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75085 | -47.63362 |
| BLOQ_051 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Carlos Wingeter | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75112 | -47.63256 |
| BLOQ_052 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Benedito Luiz Siqueira | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75158 | -47.63038 |
| BLOQ_053 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Porto Velho | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.75146 | -47.63120 |
| BLOQ_054 | ZONA_02 | Fronteira Simples (Geométrica) | Travessa 4 B | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74320 | -47.60343 |
| BLOQ_055 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Dois Córregos | Estrada Secundária / Coletora | 2 | 5,0 | -22.74210 | -47.60240 |
| BLOQ_056 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.74177 | -47.60212 |
| BLOQ_057 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia do Açúcar | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.74033 | -47.60095 |
| BLOQ_058 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia do Açúcar | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.74008 | -47.60077 |
| BLOQ_059 | ZONA_02 | Fronteira Simples (Geométrica) | Rua dos Contabilistas | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73889 | -47.59998 |
| BLOQ_060 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Angelo Filipini | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73741 | -47.59909 |
| BLOQ_061 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Angelo Filipini | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73945 | -47.60035 |
| BLOQ_062 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.73708 | -47.59892 |
| BLOQ_063 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia Margarida das Graças Martins | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.73674 | -47.59873 |
| BLOQ_064 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.73502 | -47.59791 |
| BLOQ_065 | ZONA_02 | Fronteira Simples (Geométrica) | Travessa Antártica | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73424 | -47.59760 |
| BLOQ_066 | ZONA_02 | Fronteira Simples (Geométrica) | Travessa Adelino Gomes Dantas | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73324 | -47.59720 |
| BLOQ_067 | ZONA_02 | Fronteira Simples (Geométrica) | Rua João Franco de Oliveira | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73043 | -47.59642 |
| BLOQ_068 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.72966 | -47.59628 |
| BLOQ_069 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Francisco Carlos de Castro Neves | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72796 | -47.59599 |
| BLOQ_070 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Eugênio Losso | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72574 | -47.59584 |
| BLOQ_071 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Phelipe Zaidan Maluf | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72338 | -47.59589 |
| BLOQ_072 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia Luiz de Queiroz | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.72277 | -47.59591 |
| BLOQ_073 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.72221 | -47.59599 |
| BLOQ_074 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.72191 | -47.59603 |
| BLOQ_075 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.72145 | -47.59610 |
| BLOQ_076 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.72108 | -47.59615 |
| BLOQ_077 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.72069 | -47.59621 |
| BLOQ_078 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ataulfo Alves | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74818 | -47.64002 |
| BLOQ_079 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Osório Germano e Silva, Rua Ataulfo Alves | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74834 | -47.63976 |
| BLOQ_080 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Cacilda Becker | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74776 | -47.64075 |
| BLOQ_081 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Castro Alves | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74705 | -47.64191 |
| BLOQ_082 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Fagundes Varela | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74656 | -47.64261 |
| BLOQ_083 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.74521 | -47.64439 |
| BLOQ_084 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida 31 de Março | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.74560 | -47.64394 |
| BLOQ_085 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Olavo Bilac | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74603 | -47.64334 |
| BLOQ_086 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida 31 de Março | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.74503 | -47.64459 |
| BLOQ_087 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Júlio Mesquita Filho | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74387 | -47.64592 |
| BLOQ_088 | ZONA_02 | Fronteira Simples (Geométrica) | Rua 1º de Maio | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74235 | -47.64738 |
| BLOQ_089 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ilídia Bacchi | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74332 | -47.64646 |
| BLOQ_090 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Bairro Verde | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74261 | -47.64713 |
| BLOQ_091 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Dona Hilda | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74286 | -47.64689 |
| BLOQ_092 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Zeferino Bacchi | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74179 | -47.64790 |
| BLOQ_093 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Dona Rosália | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.74116 | -47.64838 |
| BLOQ_094 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Dona Lica | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73972 | -47.64949 |
| BLOQ_095 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Buarque de Macedo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73935 | -47.64974 |
| BLOQ_096 | ZONA_02 | Fronteira Simples (Geométrica) | Rua São João | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73873 | -47.65012 |
| BLOQ_097 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.73785 | -47.65066 |
| BLOQ_098 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Doutor Paulo de Moraes | Estrada Secundária / Coletora | 2 | 5,0 | -22.73735 | -47.65097 |
| BLOQ_099 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Doutor Paulo de Moraes | Estrada Secundária / Coletora | 2 | 5,0 | -22.73703 | -47.65113 |
| BLOQ_100 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Joaquim André | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73578 | -47.65174 |
| BLOQ_101 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Governador Pedro de Toledo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73457 | -47.65229 |
| BLOQ_102 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Boa Morte | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73365 | -47.65422 |
| BLOQ_103 | ZONA_02 | Fronteira Simples (Geométrica) | Rua São Francisco de Assis | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73315 | -47.65508 |
| BLOQ_104 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Antônio Corrêa Barbosa | Estrada Secundária / Coletora | 2 | 5,0 | -22.72774 | -47.66200 |
| BLOQ_105 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Professor Heitor Pinto César | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72825 | -47.66152 |
| BLOQ_106 | ZONA_02 | Fronteira Simples (Geométrica) | Rua do Rosário | Estrada Secundária / Coletora | 2 | 5,0 | -22.73262 | -47.65600 |
| BLOQ_107 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Madre Cecília | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73212 | -47.65681 |
| BLOQ_108 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Fernando Ferraz de Arruda Pinto | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.73159 | -47.65755 |
| BLOQ_109 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Outras Vias | 2 | 1,0 | -22.72681 | -47.66288 |
| BLOQ_110 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Alidor Pecorari | Estrada Secundária / Coletora | 2 | 5,0 | -22.72653 | -47.66310 |
| BLOQ_111 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Sérgio Caldaro | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72429 | -47.66477 |
| BLOQ_112 | ZONA_02 | Fronteira Simples (Geométrica) | Rua do Porto | Outras Vias | 2 | 1,0 | -22.72571 | -47.66373 |
| BLOQ_113 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Presidente Kennedy | Estrada Secundária / Coletora | 2 | 5,0 | -22.72329 | -47.66539 |
| BLOQ_114 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Manoel Chaddad | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72199 | -47.66615 |
| BLOQ_115 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Cardeal Arcoverde | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72135 | -47.66646 |
| BLOQ_116 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Doutor Gabriel de Toledo Piza | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72110 | -47.66658 |
| BLOQ_117 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Padre Joaquim do Canto, Rua Doutor Galdino de Carvalho | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.72047 | -47.66689 |
| BLOQ_118 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Virgolino de Oliveira | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71825 | -47.66776 |
| BLOQ_119 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Marechal Mascarenhas de Moraes | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71751 | -47.66803 |
| BLOQ_120 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Luther King | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71711 | -47.66815 |
| BLOQ_121 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Clemente Candido Gomes | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71666 | -47.66826 |
| BLOQ_122 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Cícero Pompeo de Toledo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71578 | -47.66848 |
| BLOQ_123 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ernesto Papini | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71989 | -47.66717 |
| BLOQ_124 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Doutor Celso Galdino Fraga | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71914 | -47.66744 |
| BLOQ_125 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Francisco Prestes Maia, Rua Aldo Furlan | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71489 | -47.66870 |
| BLOQ_126 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Francisco Prestes Maia, Rua Aldo Furlan | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71448 | -47.66877 |
| BLOQ_127 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Armando Césare Dedini | Estrada Secundária / Coletora | 2 | 5,0 | -22.71410 | -47.66882 |
| BLOQ_128 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Rosa Pizelli D'Abronzo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71337 | -47.66892 |
| BLOQ_129 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Antonio Carlos Galvão Moura Lacerda | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71280 | -47.66900 |
| BLOQ_130 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Lília Guerrine Sêga | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71198 | -47.66910 |
| BLOQ_131 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Tenente Thomaz Nunes | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71119 | -47.66912 |
| BLOQ_132 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Joana D'Arc | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.71064 | -47.66914 |
| BLOQ_133 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Plínio Correia Lara | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70960 | -47.66918 |
| BLOQ_134 | ZONA_02 | Fronteira Simples (Geométrica) | Rua das Pombas | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70891 | -47.66914 |
| BLOQ_135 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Pedro Sacconi | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70830 | -47.66909 |
| BLOQ_136 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Adolpho Schievano | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70768 | -47.66905 |
| BLOQ_137 | ZONA_02 | Fronteira Simples (Geométrica) | Rua João Ducatti | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70706 | -47.66900 |
| BLOQ_138 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ernest Mahle | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70650 | -47.66892 |
| BLOQ_139 | ZONA_02 | Fronteira Simples (Geométrica) | Rua José Bruzantim | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70589 | -47.66881 |
| BLOQ_140 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ana Neri | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70534 | -47.66871 |
| BLOQ_141 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ignácio Martins | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70478 | -47.66861 |
| BLOQ_142 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Maria Stênico | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70413 | -47.66848 |
| BLOQ_143 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Doutor Otávio Amaral Gurgel | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70340 | -47.66827 |
| BLOQ_144 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Manoel Conceição | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70282 | -47.66810 |
| BLOQ_145 | ZONA_02 | Fronteira Simples (Geométrica) | Travessa Rua Madame Curie | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70225 | -47.66794 |
| BLOQ_146 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Doutor João Teodoro | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70182 | -47.66781 |
| BLOQ_147 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Francisco de Souza | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70153 | -47.66771 |
| BLOQ_148 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.72024 | -47.59627 |
| BLOQ_149 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.71863 | -47.59667 |
| BLOQ_150 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.71756 | -47.59694 |
| BLOQ_151 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.71478 | -47.59799 |
| BLOQ_152 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.71340 | -47.59866 |
| BLOQ_153 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.71038 | -47.60043 |
| BLOQ_154 | ZONA_02 | Fronteira Simples (Geométrica) | Via Comendador Pedro Morganti | Estrada Secundária / Coletora | 2 | 5,0 | -22.70593 | -47.60153 |
| BLOQ_155 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia Deputado Laércio Corte | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.70019 | -47.60083 |
| BLOQ_156 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.70412 | -47.60119 |
| BLOQ_157 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Asan | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69011 | -47.60283 |
| BLOQ_158 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.69953 | -47.60085 |
| BLOQ_159 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.69682 | -47.60105 |
| BLOQ_160 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.69409 | -47.60156 |
| BLOQ_161 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia Ernesto Paterniani | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.69337 | -47.60174 |
| BLOQ_162 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.69300 | -47.60183 |
| BLOQ_163 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68956 | -47.60310 |
| BLOQ_164 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68795 | -47.60388 |
| BLOQ_165 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68771 | -47.60400 |
| BLOQ_166 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68657 | -47.60470 |
| BLOQ_167 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68504 | -47.60569 |
| BLOQ_168 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68382 | -47.60664 |
| BLOQ_169 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67294 | -47.62998 |
| BLOQ_170 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Americo Faganello Filho, Rua Lucas Sampronha | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67296 | -47.63068 |
| BLOQ_171 | ZONA_02 | Fronteira Simples (Geométrica) | Rodovia Fausto Santomauro | Rodovia Principal / Federal / Estadual | 2 | 10,0 | -22.67294 | -47.62933 |
| BLOQ_172 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Guilherme Bannitz Netto, Rua Ayrton da Silva | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67322 | -47.63405 |
| BLOQ_173 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Santa Albertina | Estrada Secundária / Coletora | 2 | 5,0 | -22.67293 | -47.62964 |
| BLOQ_174 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Cedral | Estrada Secundária / Coletora | 2 | 5,0 | -22.67298 | -47.62871 |
| BLOQ_175 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Eduardo Fernandes Filho | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67301 | -47.63226 |
| BLOQ_176 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Democlácio José Rossin | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67298 | -47.63121 |
| BLOQ_177 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Diva Pecorari Buldrini | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67311 | -47.63315 |
| BLOQ_178 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68310 | -47.60721 |
| BLOQ_179 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Hyundai | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.68279 | -47.60750 |
| BLOQ_180 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67362 | -47.62349 |
| BLOQ_181 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67350 | -47.62404 |
| BLOQ_182 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67343 | -47.62450 |
| BLOQ_183 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67401 | -47.62192 |
| BLOQ_184 | ZONA_02 | Fronteira Simples (Geométrica) | Estrada Aldo Zulini, Estrada Lázaro Pedro de Oliveira - Whisky | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.67411 | -47.62153 |
| BLOQ_185 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Frei Caneca | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70111 | -47.66754 |
| BLOQ_186 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Américo Vespuccio | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.70069 | -47.66737 |
| BLOQ_187 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Pascoal d'Abronzo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69881 | -47.66655 |
| BLOQ_188 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Pero Vaz de Caminha | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69988 | -47.66704 |
| BLOQ_189 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Domingos Mazzonetto | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69928 | -47.66679 |
| BLOQ_190 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Humberto D'Abronzo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69815 | -47.66620 |
| BLOQ_191 | ZONA_02 | Fronteira Simples (Geométrica) | Rua João Graner | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69787 | -47.66606 |
| BLOQ_192 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Dona Adelina Tarsia | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69722 | -47.66571 |
| BLOQ_193 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Terenzio Galesi | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69671 | -47.66542 |
| BLOQ_194 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Rafael Ducatti | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69577 | -47.66479 |
| BLOQ_195 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Pompilho Rafael Flores | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69526 | -47.66445 |
| BLOQ_196 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Victorio Laerte Furlani | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69474 | -47.66410 |
| BLOQ_197 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Emílio Bertozzi | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69414 | -47.66362 |
| BLOQ_198 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.69389 | -47.66342 |
| BLOQ_199 | ZONA_02 | Fronteira Simples (Geométrica) | Avenida Brasília | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69227 | -47.66204 |
| BLOQ_200 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Ignácio da Cunha Caldeira | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69182 | -47.66159 |
| BLOQ_201 | ZONA_02 | Fronteira Simples (Geométrica) | Rua José Stolf | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.69101 | -47.66076 |
| BLOQ_202 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Jordão Martins | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68931 | -47.65878 |
| BLOQ_203 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67928 | -47.64873 |
| BLOQ_204 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67655 | -47.64451 |
| BLOQ_205 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67760 | -47.64635 |
| BLOQ_206 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Alberto Coral | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68431 | -47.65377 |
| BLOQ_207 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Vitório Coral | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68193 | -47.65169 |
| BLOQ_208 | ZONA_02 | Fronteira Simples (Geométrica) | Acesso Rural Sem Nome | Estrada Rural / Vicinal / Servidão | 2 | 1,0 | -22.67360 | -47.63632 |
| BLOQ_209 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Mário Bortolazzo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68134 | -47.65110 |
| BLOQ_210 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Antônio Bérgamo | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68072 | -47.65047 |
| BLOQ_211 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Cláudio Bere | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68671 | -47.65542 |
| BLOQ_212 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Benedito José Anastácio | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68626 | -47.65512 |
| BLOQ_213 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Amadeu Castanho | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68733 | -47.65595 |
| BLOQ_214 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Casa Branca | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68592 | -47.65489 |
| BLOQ_215 | ZONA_02 | Fronteira Simples (Geométrica) | Rua Caetano Carmignani | Estrada Municipal / Acesso Local | 2 | 1,0 | -22.68498 | -47.65425 |

## 6. Arquivos Vetoriais (Shapefiles / GeoJSON) e Tabulares Gerados

- **Shapefile dos Postos de Bloqueio (Solução Principal):** `bloqueios_sanitarios.shp`
- **Shapefile dos Postos de Bloqueio (Min-Cut Híbrido):** `bloqueios_mincut.shp`
- **Shapefile dos Postos de Bloqueio (Geométrica Convencional):** `bloqueios_geometrico.shp`
- **Shapefile da Malha Viária (Vias OSM):** `malha_viaria.shp`
- **Shapefile das Zonas de Contenção:** `zonas_contencao.shp`
- **GeoJSON dos Postos de Bloqueio:** `bloqueios_sanitarios.geojson`
- **GeoJSON da Malha Viária:** `malha_viaria.geojson`
- **GeoJSON das Zonas de Contenção:** `zonas_contencao.geojson`
- **Planilha CSV dos Postos de Bloqueio:** `bloqueios_sanitarios.csv`
- **Planilha CSV das Propriedades Analisadas:** `propriedades_analisadas.csv`

## 7. Diretrizes Operacionais
1. **Fiscalização Integral:** Qualquer veículo que transite de/para a zona de contenção passará obrigatoriamente por um dos postos listados (Hermeticidade Topológica de 100%, Conectividade Residual Nula).
2. **Equipes de Desinfecção:** Recomenda-se priorizar postos em 'Rodovias Principais' ($c = 10,0$) e 'Estradas Secundárias' ($c = 5,0$) com estrutura reforçada de rodolúvio e arco de desinfecção.
3. **Sinalização:** Instalar placas de advertência e desvio a 500m dos postos de bloqueio.