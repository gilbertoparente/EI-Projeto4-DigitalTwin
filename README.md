# CyberTwin — Digital Twin de Cibersegurança

Simulação baseada em agentes (ABM) de ataques de engenharia social (Phishing / Spear Phishing) numa organização fictícia. Permite configurar defesas (MFA, Formação, Segmentação de Rede) e observar a propagação de ameaças em tempo real através de um dashboard web.

---

## Arquitectura

```
┌─────────────────────────────────┐
│   UI  — Streamlit (porta 8501)  │
│   ui/dashboard.py               │
│   ui/pages/  (experiments,      │
│              live_system,        │
│              network)            │
└────────────────┬────────────────┘
                 │ HTTP (requests)
                 ▼
┌─────────────────────────────────┐
│   API — FastAPI (porta 8000)    │
│   src/api/server.py             │
│   POST /start                   │
│   GET  /step  /status  /graph   │
│        /metrics  /departments   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Motor — Mesa + NetworkX       │
│   src/core/organization_model   │
│   src/core/agents/              │
│   src/core/attacks/             │
│   src/core/mitigations/         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Persistência — SQLite         │
│   database/db.py                │
│   digital_twin.db  (auto-criado)│
└─────────────────────────────────┘
```

---

## Pré-requisitos

- Python **3.10** ou superior
- pip actualizado (`python -m pip install --upgrade pip`)

---

## Instalação

```bash
git clone https://github.com/gilbertoparente/EI-Projeto4-DigitalTwin.git
cd EI-Projeto4-DigitalTwin

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Execução

### Terminal 1 — API (FastAPI)

```bash
python -m src.main

```

A API fica disponível em `http://127.0.0.1:8000`.  
Documentação interactiva: `http://127.0.0.1:8000/docs`

### Terminal 2 — Dashboard (Streamlit)

```bash
streamlit run ui/dashboard.py

```

O dashboard abre automaticamente em `http://localhost:8501`.

---

## Utilização

1. Abrir o dashboard no browser (`http://localhost:8501`).
2. Ir à página **Experiments** — configurar o cenário (tipo de ataque, número de agentes, defesas activas) e clicar **Iniciar Simulação**.
3. Ir à página **Live System** — clicar **Step** para avançar ticks ou usar o modo automático.
4. Ir à página **Network** — visualizar o grafo de confiança e os agentes comprometidos.

---

## Estrutura do projecto

```
├── src/
│   ├── api/
│   │   ├── server.py              # FastAPI app (ponto de entrada da API)
│   │   └── routes/
│   │       └── config.py          # Schema SimulacaoRequest
│   ├── core/
│   │   ├── organization_model.py  # Mesa Model — orquestra a simulação
│   │   ├── agents/
│   │   │   ├── base_agent.py
│   │   │   ├── collaborator_agent.py
│   │   │   └── attacker_agent.py
│   │   ├── attacks/
│   │   │   ├── base_attack.py
│   │   │   ├── phishing.py
│   │   │   └── spear_phishing.py
│   │   └── mitigations/
│   │       ├── mfa.py
│   │       ├── segmentation.py
│   │       └── training.py
│   ├── services/
│   │   ├── graph_services.py
│   │   └── kpi_services.py
│   └── main.py                    # Arranca o uvicorn
├── ui/
│   ├── dashboard.py               # Ponto de entrada do Streamlit
│   ├── api_client.py              # Wrapper HTTP para a API
│   ├── components/
│   │   └── config_builder.py
│   └── pages/
│       ├── experiments.py
│       ├── live_system.py
│       └── network.py
├── database/
│   ├── db.py                      # SQLAlchemy engine + helpers
│   └── models.py                  # ORM models
├── requirements.txt
└── README.md
```

---

## Endpoints da API

| Método | Rota               | Descrição                                              |
|--------|--------------------|--------------------------------------------------------|
| POST   | `/start`           | Inicia simulação com config JSON completo              |
| POST   | `/start/simple`    | Inicia simulação com schema simplificado (`SimulacaoRequest`) |
| GET    | `/step`            | Avança um tick e devolve resultado                     |
| GET    | `/status`          | Estado actual (tick, agentes)                          |
| GET    | `/graph`           | Grafo de nós e arestas para visualização               |
| GET    | `/metrics`         | Série temporal de métricas (DataCollector)             |
| GET    | `/departments`     | Taxa de comprometimento por departamento               |

---

## Tecnologias

| Biblioteca  | Versão mínima | Uso                              |
|-------------|---------------|----------------------------------|
| Mesa        | 2.1.1         | Motor ABM (agentes, scheduler)   |
| NetworkX    | 3.1           | Grafo sociotécnico               |
| FastAPI     | 0.100         | API REST                         |
| Uvicorn     | 0.23.0        | Servidor ASGI                    |
| Streamlit   | 1.28.0        | Dashboard web                    |
| SQLAlchemy  | 2.0           | Persistência SQLite              |
| Pandas      | 2.0.0         | Tratamento de métricas           |
| Matplotlib  | 3.7.0         | Gráficos no dashboard            |
| Requests    | 2.31.0        | Comunicação UI → API             |
