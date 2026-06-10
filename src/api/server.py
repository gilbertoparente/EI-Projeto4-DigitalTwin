import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.organization_model import OrganizationModel
from src.services.graph_services import GraphService
from src.services.kpi_services import KPIService

app = FastAPI(title="Digital Twin Cybersecurity API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_sim: OrganizationModel | None = None
_graph_service = GraphService()
_kpi_service = KPIService()

# ── Cenários lado a lado
_scenario_a: OrganizationModel | None = None
_scenario_b: OrganizationModel | None = None
_scenario_a_history: list[dict] = []
_scenario_b_history: list[dict] = []

# ── Departamentos guardados (persistência em ficheiro JSON)
DEPTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                           "saved_departments.json")

def _load_departments() -> dict:
    if os.path.exists(DEPTS_FILE):
        try:
            with open(DEPTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_departments(depts: dict):
    with open(DEPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(depts, f, ensure_ascii=False, indent=2)

_saved_departments: dict = _load_departments()

#  Simulação principal

@app.post("/start")
async def start(config: dict):
    global _sim
    _sim = OrganizationModel(config)
    return {"status": "Simulação iniciada", "agentes": len(_sim.agents)}

@app.get("/step")
async def step():
    if _sim is None:
        return {"error": "Simulação não iniciada"}
    return _sim.step()

@app.get("/status")
async def status():
    if _sim is None:
        return {"status": "idle"}
    compromised = sum(1 for a in _sim.schedule.agents if a.compromised)
    return {"tick": _sim.tick, "agents": len(_sim.agents), "compromised": compromised}

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

#  Comparação de cenários A / B

@app.post("/scenarios/start")
async def scenarios_start(payload: dict):
    global _scenario_a, _scenario_b, _scenario_a_history, _scenario_b_history
    _scenario_a = OrganizationModel(payload["scenario_a"])
    _scenario_b = OrganizationModel(payload["scenario_b"])
    _scenario_a_history = []
    _scenario_b_history = []
    return {
        "status": "Cenários iniciados",
        "scenario_a_agents": len(_scenario_a.agents),
        "scenario_b_agents": len(_scenario_b.agents),
    }

@app.get("/scenarios/step")
async def scenarios_step(n: int = 1):
    if _scenario_a is None or _scenario_b is None:
        return {"error": "Cenários não iniciados."}
    for _ in range(n):
        r_a = _scenario_a.step()
        r_b = _scenario_b.step()
        _scenario_a_history.append({
            "tick": r_a["tick"],
            "total_compromised": r_a["total_compromised"],
            "total_agents": r_a["total_agents"],
            "infected": r_a["result"]["infected"],
            "opened": r_a["result"]["opened"],
            "clicked": r_a["result"]["clicked"],
        })
        _scenario_b_history.append({
            "tick": r_b["tick"],
            "total_compromised": r_b["total_compromised"],
            "total_agents": r_b["total_agents"],
            "infected": r_b["result"]["infected"],
            "opened": r_b["result"]["opened"],
            "clicked": r_b["result"]["clicked"],
        })
    return {"scenario_a": _scenario_a_history, "scenario_b": _scenario_b_history}

@app.get("/scenarios/status")
async def scenarios_status():
    if _scenario_a is None or _scenario_b is None:
        return {"status": "idle"}
    c_a = sum(1 for ag in _scenario_a.schedule.agents if ag.compromised)
    c_b = sum(1 for ag in _scenario_b.schedule.agents if ag.compromised)
    return {
        "scenario_a": {"tick": _scenario_a.tick, "agents": len(_scenario_a.agents), "compromised": c_a},
        "scenario_b": {"tick": _scenario_b.tick, "agents": len(_scenario_b.agents), "compromised": c_b},
    }

@app.get("/scenarios/compare")
async def scenarios_compare():
    if not _scenario_a_history or not _scenario_b_history:
        return {"error": "Sem histórico."}

    def summary(history, model):
        last = history[-1]
        total = last["total_agents"] or 1
        max_inf = max(h["total_compromised"] for h in history)
        mttd = next((h["tick"] for h in history if h["total_compromised"] > 0), None)
        kpis = _kpi_service.compute(
            {"infected": last["total_compromised"], "clicked": last["clicked"], "opened": last["opened"]},
            total,
        )
        # Probabilidade de infeção estimada por agente
        # Baseada na taxa média de crescimento da infeção ao longo dos ticks
        growth_rates = []
        for i in range(1, len(history)):
            prev = history[i-1]["total_compromised"]
            curr = history[i]["total_compromised"]
            susceptible = total - prev
            if susceptible > 0:
                growth_rates.append((curr - prev) / susceptible)
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0

        return {
            "ticks_run": last["tick"],
            "final_compromised": last["total_compromised"],
            "max_compromised": max_inf,
            "infection_rate": kpis["infection_rate"],
            "click_rate": kpis["click_rate"],
            "open_rate": kpis["open_rate"],
            "conversion_rate": kpis["conversion_rate"],
            "infection_probability_per_tick": round(avg_growth, 4),
            "mttd": mttd,
            "attack_type": model.config["attack"]["type"],
            "mfa": model.config["defense"].get("mfa", False),
            "training": model.config["defense"].get("training", 0.5),
            "segmentation": model.config["defense"].get("segmentation", 0.5),
            "n_agents": total,
        }

    return {
        "scenario_a": summary(_scenario_a_history, _scenario_a),
        "scenario_b": summary(_scenario_b_history, _scenario_b),
        "history_a": _scenario_a_history,
        "history_b": _scenario_b_history,
    }

#  Guardar / carregar departamentos (persistência em JSON)

@app.post("/departments/save")
async def save_department(payload: dict):
    key = payload.get("name")
    dept = payload.get("department")
    if not key or not dept:
        return {"error": "Campos 'name' e 'department' obrigatórios."}
    _saved_departments[key] = dept
    _save_departments(_saved_departments)
    return {"status": "Departamento guardado", "name": key}

@app.get("/departments/saved")
async def list_saved_departments():
    return {"departments": _saved_departments}

@app.get("/departments/saved/{name}")
async def get_saved_department(name: str):
    dept = _saved_departments.get(name)
    if dept is None:
        return {"error": f"Departamento '{name}' não encontrado."}
    return dept

@app.delete("/departments/saved/{name}")
async def delete_saved_department(name: str):
    if name not in _saved_departments:
        return {"error": f"Departamento '{name}' não encontrado."}
    del _saved_departments[name]
    _save_departments(_saved_departments)
    return {"status": "Eliminado", "name": name}