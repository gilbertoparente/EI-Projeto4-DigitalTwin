# EI-Projeto4-DigitalTwin
# Digital Twin: Simulação de Cibersegurança (Engenharia Social)

Este projeto consiste num **Digital Twin** desenvolvido para modelar e simular ataques de phishing e propagação de ameaças numa organização de ~150 colaboradores. O objetivo é analisar a eficácia de diferentes camadas de defesa (MFA, Formação, Segmentação) através de simulações baseadas em agentes.

## 🏗️ Arquitetura do Sistema

O sistema está estruturado em 3 camadas principais:

1.  **Camada de Input:** Interface Web (Mesa Visualization) onde são configurados os parâmetros do cenário (ex: % de funcionários formados, ativação de MFA).
2.  **Camada de Processamento:** Motor de simulação baseado no **Mesa Framework** e **NetworkX**, que gere a lógica de agentes e o grafo sociotécnico da organização.
3.  **Camada de Output:** Dashboards e gráficos em tempo real que monitorizam métricas como a taxa de propagação e o tempo de deteção (MTTD).

                ┌──────────────────────────┐
                │   INPUT LAYER FastAPI    │
                │  (dados reais / sinais)  │
                └──────────┬───────────────┘
                           ↓
        ┌────────────────────────────────────────┐
        │          PROCESSING LAYER Mesa         │
        │  models/ + agents/ (Mesa simulation)   │
        └────────────────┬──────────────────────┘
                         ↓
                ┌──────────────────────────┐
                │        OUTPUT LAYER json  │
                │  resultados / métricas    │
                │  gráficos / logs / API    │
                └──────────────────────────┘


## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **Mesa:** Framework para modelação baseada em agentes (ABM).
* **NetworkX:** Criação e manipulação de grafos de redes complexas.
* **Matplotlib:** Geração de gráficos estatísticos.
* **Tornado:** Servidor para visualização web.



## 🚀 Como Executar

1. Abrir o terminal na pasta do prjecto e iniciar o servidor:
2. python -m src.main

Abrir o Dashboard:
 $env:PYTHONPATH = "."       
streamlit run ui/dashboard.py


### 1. Clonar o repositório
```bash
git clone https://github.com/gilbertoparente/EI-Projeto4-DigitalTwin.git
cd DigitalTwin




# 