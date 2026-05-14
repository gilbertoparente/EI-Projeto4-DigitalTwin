from fastapi import APIRouter
from services.simulation_service import SimulationService

router = APIRouter()

sim_instance = None

# =========================================================
# START SIMULATION
# =========================================================

@router.post("/start")
def start_simulation(config: dict):

    global sim_instance

    sim_instance = SimulationService(config)

    return {
        "status": "started",
        "agents": len(sim_instance.agents)
    }

# =========================================================
# STEP
# =========================================================

@router.get("/step")
def step_simulation():

    global sim_instance

    if sim_instance is None:
        return {
            "error": "simulation not started"
        }

    return sim_instance.step()