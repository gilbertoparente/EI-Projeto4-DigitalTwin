from fastapi import FastAPI
from src.core.organization_model import OrganizationModel
from src.services.graph_services import GraphService
from src.api.routes.config import SimulacaoRequest

app = FastAPI(title="Digital Twin Cybersecurity API")

_sim: OrganizationModel | None = None
_graph_service = GraphService()


@app.post("/start")
async def start(config: dict):
    global _sim
    _sim = OrganizationModel(config)
    return {
        "status": "Simulação iniciada",
        "agentes": len(_sim.agents),
    }


@app.post("/start/simple")
async def start_simple(req: SimulacaoRequest):
    global _sim
    _sim = OrganizationModel(_build_config(req))
    return {
        "status": "started",
        "agents": len(_sim.agents),
        "attack": req.tipo_ataque,
        "mfa": req.mfa_ativo,
    }


@app.get("/step")
async def step():
    if _sim is None:
        return {"error": "Simulação não iniciada"}
    return _sim.step()


@app.get("/status")
async def status():
    if _sim is None:
        return {"status": "idle"}
    return {
        "tick": _sim.tick,
        "agents": len(_sim.agents),
    }


@app.get("/graph")
async def graph():
    if _sim is None:
        return {"nodes": [], "edges": []}
    return _graph_service.get_graph_data(_sim.agents, _sim.graph)


@app.get("/metrics")
async def metrics():
    if _sim is None:
        return {"error": "Simulação não iniciada"}
    df = _sim.datacollector.get_model_vars_dataframe()
    return df.reset_index().rename(columns={"index": "tick"}).to_dict(orient="records")


@app.get("/departments")
async def departments():
    if _sim is None:
        return {"error": "Simulação não iniciada"}
    return _sim.department_stats


def _build_config(req: SimulacaoRequest) -> dict:
    n = req.n_agentes
    dept_size = n // 3
    return {
        "organization": {
            "departments": [
                {
                    "name": dept,
                    "agents": [
                        {
                            "name": f"{dept}_User_{i}",
                            "hierarchy_level": (i % 3) + 1,
                            "risk_propensity": 0.5,
                            "awareness_level": 0.3,
                        }
                        for i in range(dept_size)
                    ],
                }
                for dept in ["IT", "Finance", "HR"]
            ]
        },
        "attack": {
            "type": "Spear Phishing" if req.tipo_ataque == "spear" else "Phishing",
            "click_rate": 0.5,
        },
        "defense": {
            "mfa": req.mfa_ativo,
            "training": req.prob_formacao,
            "segmentation": 0.5,
        },
    }