from fastapi import APIRouter
from src.services.simulation_service import SimulationService
from src.core import simulation_state as state

router = APIRouter()


@router.post("/start")
def start_simulation(config: dict):

    global state
    state = SimulationService(config)

    return {
        "status": "started",
        "agents": len(state.agents)
    }


@router.get("/step")
def step_simulation():

    if state is None:
        return {"error": "simulation not started"}

    return state.step()


@router.get("/status")
def status():

    if state is None:
        return {
            "agents": 0,
            "state": {"opened": 0, "clicked": 0, "infected": 0}
        }

    return {
        "agents": len(state.agents),
        "state": {
            "opened": sum(state.metrics["opened"]),
            "clicked": sum(state.metrics["clicked"]),
            "infected": sum(state.metrics["infected"])
        }
    }