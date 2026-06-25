from fastapi import FastAPI

from src.api.routes import graph
from src.core import simulation_state
from src.services.simulation_service import SimulationService


app = FastAPI(title="Digital Twin Cybersecurity API")


@app.post("/start")
async def start(config: dict):
    simulation_state.sim_instance = SimulationService(config)
    return {
        "status": "Simulation Started",
        "agents": len(simulation_state.sim_instance.agents),
        "edges": sum(len(edges) for edges in simulation_state.sim_instance.graph.values()),
    }


@app.get("/step")
async def step():
    if not simulation_state.sim_instance:
        return {"error": "Simulation not started"}
    return simulation_state.sim_instance.step()


@app.get("/status")
async def status():
    sim = simulation_state.sim_instance
    if not sim:
        return {"status": "idle"}
    return {"status": "ready", "tick": sim.tick, "agents": len(sim.agents)}


app.include_router(graph.router)
