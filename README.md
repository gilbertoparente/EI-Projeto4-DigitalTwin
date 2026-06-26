# 🛡️ CyberTwin — Digital Twin de Engenharia Social

Simulação baseada em agentes (Mesa) de ataques de Phishing e Spear Phishing em ambientes corporativos, com avaliação de estratégias defensivas (MFA, formação, segmentação de rede) e análise comparativa de cenários.

---

## 📐 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (porta 8501)             │
│  Experiments │ Live System │ Analytics │ Network │ ...   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP REST
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI (porta 8000)                    │
│  /start  /step  /graph  /metrics  /scenarios  /history  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│            OrganizationModel (Mesa)                     │
│  RandomActivation · NetworkGrid · DataCollector         │
│  CollaboratorAgent · AttackerAgent · BaseAgent          │
│  MFA · Training · Segmentation                          │
└──────────────────────┬──────────────────────────────────┘
                       │ SQLAlchemy
┌──────────────────────▼──────────────────────────────────┐
│              SQLite — digital_twin.db                   │
│  simulation_runs · simulation_steps · simulation_graphs │
└─────────────────────────────────────────────────────────┘
```

**Stack:**
- **Simulação:** [Mesa](https://mesa.readthedocs.io/) ≥ 2.1.1 + NetworkX
- **API:** FastAPI + Uvicorn
- **UI:** Streamlit
- **Base de dados:** SQLAlchemy + SQLite
- **Relatórios:** ReportLab (PDF)

---

## ⚙️ Instalação

### Pré-requisitos
- Python 3.10 ou superior
- pip

### 1. Clonar o repositório

```bash
git clone https://github.com/<org>/EI-Projeto4-DigitalTwin.git
cd EI-Projeto4-DigitalTwin
```

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 🚀 Execução

### Execução automática (recomendada)

Um único comando inicia **ambos** os serviços em simultâneo — a API FastAPI e a interface Streamlit:

```bash
python src/main.py
```

O script faz automaticamente:
1. Lança o **Streamlit** num processo separado (interface disponível em `http://localhost:8501`)
2. Inicia o **servidor FastAPI** no processo principal (API disponível em `http://localhost:8000`)

> **Nota:** A interface abre automaticamente no browser. Se não abrir, navega manualmente para `http://localhost:8501`.

---

### Execução manual (serviços separados)

Se preferires controlar cada serviço individualmente, abre **dois terminais**:

**Terminal 1 — API Backend:**

```bash
uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Interface Streamlit:**

```bash
streamlit run ui/dashboard.py
```

---

## 🖥️ Interface — Vistas disponíveis

| Vista | Descrição |
|---|---|
| **⚗️ Experiments** | Configuração da organização, ataque e defesas. Inicializa o Digital Twin. |
| **📡 Live System** | Execução passo a passo ou em lote. Monitorização em tempo real. |
| **📊 Analytics** | Benchmark automático: 3 experiências comparativas (sem formação / 50% formação / MFA). |
| **🕸️ Network** | Visualização interativa do grafo de confiança com estado de infeção por agente. |
| **⚔️ Comparação** | Dois cenários em paralelo com relatório PDF exportável. |
| **📜 History** | Histórico completo de corridas guardadas na base de dados. |

---

## 🧪 Fluxo de trabalho típico

```
1. python src/main.py
         │
         ▼
2. Experiments → configurar organização + ataque + defesas
         │
         ▼
3. "Inicializar Digital Twin Engine" → cria agentes e grafo social
         │
         ├──▶ Live System   → executar steps manualmente ou em lote
         │
         ├──▶ Analytics     → correr 3 experiências automáticas e comparar
         │
         ├──▶ Network       → inspecionar topologia e estado de infeção
         │
         ├──▶ Comparação    → confrontar dois cenários lado a lado + PDF
         │
         └──▶ History       → rever corridas anteriores da base de dados
```

---

## 📁 Estrutura do projeto

```
EI-Projeto4-DigitalTwin/
├── src/
│   ├── main.py                        # Ponto de entrada (inicia API + Streamlit)
│   ├── api/
│   │   └── server.py                  # FastAPI — todos os endpoints
│   ├── core/
│   │   ├── organization_model.py      # OrganizationModel (mesa.Model)
│   │   ├── agents/
│   │   │   ├── base_agent.py          # BaseAgent (mesa.Agent) + education modifier
│   │   │   ├── collaborator_agent.py  # CollaboratorAgent com step() nativo
│   │   │   └── attaker_agent.py       # AttackerAgent com step() nativo
│   │   └── mitigations/
│   │       ├── mfa.py                 # Multi-Factor Authentication
│   │       ├── training.py            # Formação contínua (apply + tick)
│   │       └── segmentation.py        # Segmentação de rede / Zero Trust
│   └── services/
│       ├── graph_services.py          # Transformação do grafo para a UI
│       └── kpi_services.py            # Cálculo de KPIs
├── database/
│   ├── db.py                          # SQLAlchemy engine + sessão
│   └── models.py                      # Modelos ORM (runs, steps, graphs, configs)
├── ui/
│   ├── dashboard.py                   # Entrada Streamlit + router de vistas
│   ├── api_client.py                  # Funções de acesso à API REST
│   ├── components/
│   │   └── config_builder.py          # Builder de configuração com presets
│   └── pages/
│       ├── experiments.py
│       ├── live_system.py
│       ├── analytics.py
│       ├── network.py
│       ├── scenario_comparison.py
│       └── history.py
├── requirements.txt
└── README.md
```

---

## 🔬 Modelo de simulação

### Agentes

| Tipo | Descrição |
|---|---|
| `CollaboratorAgent` | Funcionário da organização. Recebe mensagens, decide se clica, propaga comprometimento. |
| `AttackerAgent` | Atacante externo. Lança campanhas por tick conforme o tipo de ataque. |

### Parâmetros dos agentes

| Parâmetro | Intervalo | Descrição |
|---|---|---|
| `risk_propensity` | 0.0 – 1.0 | Propensão base a clicar em mensagens suspeitas |
| `awareness_level` | 0.0 – 1.0 | Literacia em cibersegurança (modificada pelo nível de educação) |
| `education_level` | enum | `"High School"` (×0.8) · `"Bachelor's Degree"` (×1.0) · `"Master's / PhD"` (×1.2) |
| `hierarchy_level` | 1 – 3 | Nível na organização (influencia targeting no Spear Phishing) |

### Defesas

| Módulo | Parâmetro | Efeito |
|---|---|---|
| **MFA** | `enabled`, `block_rate` (default 0.9) | Bloqueia 90% das tentativas mesmo após credenciais roubadas |
| **Training** | `effectiveness` (0.0 – 1.0) | Boost inicial + aumento gradual de `awareness_level` por tick |
| **Segmentation** | `isolation_level` (0.0 – 1.0) | Limita propagação lateral; +30% de bloqueio entre departamentos |

### Tipos de ataque

| Tipo | Comportamento |
|---|---|
| **Phishing** | Campanha massiva — seleciona ~5% da população por tick aleatoriamente |
| **Spear Phishing** | Direcionado — ataca os 5 agentes com `hierarchy_level` mais alto |

---

## 🗄️ Base de dados

A base de dados SQLite (`database/digital_twin.db`) é criada automaticamente na primeira execução.

| Tabela | Conteúdo |
|---|---|
| `simulation_runs` | Metadados de cada corrida (timestamp, ataque, MFA, formação, comprometidos) |
| `simulation_configs` | Configuração JSON completa da corrida |
| `simulation_graphs` | Snapshot da topologia de rede gerada |
| `simulation_steps` | Métricas por tick (opened, clicked, infected, total_compromised) |

---

## 🌐 API — Endpoints principais

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/start` | Inicializa simulação com configuração JSON |
| `GET` | `/step` | Avança 1 tick e devolve métricas |
| `GET` | `/status` | Estado atual (tick, agentes, comprometidos) |
| `GET` | `/graph` | Grafo de confiança (nodes + edges) |
| `GET` | `/metrics` | Série temporal do DataCollector (Mesa) |
| `GET` | `/departments` | Estatísticas por departamento |
| `POST` | `/analytics/run` | Corre 3 experiências automáticas em batch |
| `POST` | `/scenarios/start` | Inicializa dois cenários para comparação |
| `GET` | `/scenarios/step?n=N` | Avança N ticks em ambos os cenários |
| `GET` | `/scenarios/compare` | KPIs comparativos + histórico completo |
| `GET` | `/history` | Lista todas as corridas da base de dados |
| `GET` | `/history/steps/{run_id}` | Métricas por tick de uma corrida específica |

Documentação interativa disponível em `http://localhost:8000/docs` (Swagger UI).

---

## 👥 Projeto

**Projeto IV — Engenharia Informática**  
Instituto Politécnico de Viana do Castelo (IPVC) © 2026