import json
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database.db import init_db, get_db
from database.models import SimulationRun, SimulationConfig, SimulationGraph, SimulationStep
from src.core.organization_model import OrganizationModel
from src.services.graph_services import GraphService
from src.services.kpi_services import KPIService

init_db()

app = FastAPI(title="Digital Twin Cybersecurity API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph_service = GraphService()
_kpi_service   = KPIService()

_sim: OrganizationModel | None = None
_sim_run_id: int | None = None

_scenario_a: OrganizationModel | None = None
_scenario_b: OrganizationModel | None = None
_scenario_a_history: list[dict] = []
_scenario_b_history: list[dict] = []


@app.post("/start")
async def start(config: dict, db: Session = Depends(get_db)):
    global _sim, _sim_run_id

    _sim = OrganizationModel(config)

    experiment_label = config.get("experiment_label", "Live System Run")
    defense          = config.get("defense", {})

    run = SimulationRun(
        timestamp          = datetime.utcnow(),
        experiment_label   = experiment_label,
        attack_type        = config.get("attack", {}).get("type", "Unknown"),
        num_agents         = len(_sim.agents),
        total_compromised  = 0,
        mfa_enabled        = defense.get("mfa", False),
        training_level     = defense.get("training", 0.0),
        segmentation_level = defense.get("segmentation", 0.5),
    )
    db.add(run)
    db.flush()

    db.add(SimulationConfig(run_id=run.id, config_json=json.dumps(config)))
    db.add(SimulationGraph(run_id=run.id, graph_json=json.dumps(_sim.graph)))
    db.commit()

    _sim_run_id = run.id

    return {
        "status":  "Simulation Started",
        "agents":  len(_sim.agents),
        "edges":   sum(len(v) for v in _sim.graph.values()),
        "run_id":  run.id,
    }


@app.get("/step")
async def step(db: Session = Depends(get_db)):
    if _sim is None:
        return {"error": "Simulation not started"}

    data = _sim.step()

    if _sim_run_id:
        result = data.get("result", {})
        db.add(SimulationStep(
            run_id            = _sim_run_id,
            tick              = data["tick"],
            opened            = result.get("opened", 0),
            clicked           = result.get("clicked", 0),
            infected          = result.get("infected", 0),
            total_compromised = data.get("total_compromised", 0),
        ))
        run = db.get(SimulationRun, _sim_run_id)
        if run:
            run.total_compromised = data.get("total_compromised", 0)
        db.commit()

    return data


@app.get("/status")
async def status():
    if _sim is None:
        return {"status": "idle"}
    compromised = sum(1 for a in _sim.schedule.agents if a.compromised)
    return {
        "status":      "ready",
        "tick":        _sim.tick,
        "agents":      len(_sim.agents),
        "compromised": compromised,
        "run_id":      _sim_run_id,
    }


@app.get("/graph")
async def graph():
    if _sim is None:
        return {"nodes": [], "edges": []}
    return _graph_service.get_graph_data(_sim.agents, _sim.graph)


@app.get("/metrics")
async def metrics():
    if _sim is None:
        return {"error": "Simulation not started"}
    df = _sim.datacollector.get_model_vars_dataframe()
    return df.reset_index().rename(columns={"index": "tick"}).to_dict(orient="records")


@app.get("/departments")
async def departments():
    if _sim is None:
        return {"error": "Simulation not started"}
    return _sim.department_stats


@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    runs = db.query(SimulationRun).order_by(SimulationRun.id.desc()).all()
    result = []
    for run in runs:
        cfg_json   = run.config.config_json  if run.config  else "{}"
        graph_json = run.graph.graph_json    if run.graph   else "{}"
        result.append({
            "id":               run.id,
            "timestamp":        run.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "experiment_type":  run.experiment_label,
            "attack_type":      run.attack_type,
            "total_compromised":run.total_compromised,
            "num_agents":       run.num_agents,
            "mfa_enabled":      run.mfa_enabled,
            "training_level":   run.training_level,
            "segmentation_level": run.segmentation_level,
            "config":           json.loads(cfg_json),
            "graph":            json.loads(graph_json),
        })
    return {"runs": result}


@app.get("/history/steps/{run_id}")
async def get_history_steps(run_id: int, db: Session = Depends(get_db)):
    steps = (
        db.query(SimulationStep)
        .filter(SimulationStep.run_id == run_id)
        .order_by(SimulationStep.tick)
        .all()
    )
    return [
        {
            "tick":              s.tick,
            "opened":            s.opened,
            "clicked":           s.clicked,
            "infected":          s.infected,
            "total_compromised": s.total_compromised,
        }
        for s in steps
    ]


@app.post("/scenarios/start")
async def scenarios_start(payload: dict):
    global _scenario_a, _scenario_b, _scenario_a_history, _scenario_b_history
    _scenario_a = OrganizationModel(payload["scenario_a"])
    _scenario_b = OrganizationModel(payload["scenario_b"])
    _scenario_a_history = []
    _scenario_b_history = []
    return {
        "status": "Scenarios started",
        "scenario_a_agents": len(_scenario_a.agents),
        "scenario_b_agents": len(_scenario_b.agents),
    }


@app.get("/scenarios/step")
async def scenarios_step(n: int = 1):
    if _scenario_a is None or _scenario_b is None:
        return {"error": "Scenarios not started."}
    for _ in range(n):
        r_a = _scenario_a.step()
        r_b = _scenario_b.step()
        _scenario_a_history.append({
            "tick":              r_a["tick"],
            "total_compromised": r_a["total_compromised"],
            "total_agents":      r_a["total_agents"],
            "infected":          r_a["result"]["infected"],
            "opened":            r_a["result"]["opened"],
            "clicked":           r_a["result"]["clicked"],
        })
        _scenario_b_history.append({
            "tick":              r_b["tick"],
            "total_compromised": r_b["total_compromised"],
            "total_agents":      r_b["total_agents"],
            "infected":          r_b["result"]["infected"],
            "opened":            r_b["result"]["opened"],
            "clicked":           r_b["result"]["clicked"],
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
        return {"error": "No history available."}

    def summary(history, model):
        last  = history[-1]
        total = last["total_agents"] or 1
        max_inf = max(h["total_compromised"] for h in history)
        mttd = next((h["tick"] for h in history if h["total_compromised"] > 0), None)
        kpis = _kpi_service.compute(
            {"infected": last["total_compromised"], "clicked": last["clicked"], "opened": last["opened"]},
            total,
        )
        growth_rates = []
        for i in range(1, len(history)):
            prev       = history[i-1]["total_compromised"]
            curr       = history[i]["total_compromised"]
            susceptible = total - prev
            if susceptible > 0:
                growth_rates.append((curr - prev) / susceptible)
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0

        return {
            "ticks_run":                      last["tick"],
            "final_compromised":              last["total_compromised"],
            "max_compromised":                max_inf,
            "infection_rate":                 kpis["infection_rate"],
            "click_rate":                     kpis["click_rate"],
            "open_rate":                      kpis["open_rate"],
            "conversion_rate":                kpis["conversion_rate"],
            "infection_probability_per_tick": round(avg_growth, 4),
            "mttd":                           mttd,
            "attack_type":                    model.config["attack"]["type"],
            "mfa":                            model.config["defense"].get("mfa", False),
            "training":                       model.config["defense"].get("training", 0.5),
            "segmentation":                   model.config["defense"].get("segmentation", 0.5),
            "n_agents":                       total,
        }

    return {
        "scenario_a": summary(_scenario_a_history, _scenario_a),
        "scenario_b": summary(_scenario_b_history, _scenario_b),
        "history_a":  _scenario_a_history,
        "history_b":  _scenario_b_history,
    }


@app.post("/analytics/run")
async def analytics_run(payload: dict):
    import copy
    base   = payload.get("config", {})
    ticks  = int(payload.get("ticks", 15))
    attack = payload.get("attack_type", base.get("attack", {}).get("type", "Phishing"))

    def run_exp(cfg, n):
        model = OrganizationModel(cfg)
        hist  = []
        prev  = 0
        for _ in range(n):
            r = model.step()
            cur = r["total_compromised"]
            hist.append({
                "tick":                    r["tick"],
                "opened":                  r["result"]["opened"],
                "clicked":                 r["result"]["clicked"],
                "infected":                r["result"]["infected"],
                "total_network_infection": cur,
            })
            prev = cur
        return hist

    def make_cfg(base, atk, training_cov, mfa, training_eff, label):
        c = copy.deepcopy(base)
        c["experiment_label"]     = label
        c["attack"]               = {"type": atk}
        c.setdefault("defense", {})
        c["defense"]["mfa"]               = mfa
        c["defense"]["training"]          = training_eff
        c["defense"]["training_coverage"] = training_cov
        return c

    return {
        "exp1": run_exp(make_cfg(base, attack, 0.0, False, 0.3, "No training"), ticks),
        "exp2": run_exp(make_cfg(base, attack, 0.5, False, 0.6, "50% training"), ticks),
        "exp3": run_exp(make_cfg(base, attack, 0.0, True,  0.3, "MFA"), ticks),
    }