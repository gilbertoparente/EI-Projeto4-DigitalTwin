from fastapi import FastAPI
import src.api.routes.simulation as simulation_module

app = FastAPI(
    title="Digital Twin API",
    version="2.0"
)

# =========================================================
# ROUTER
# =========================================================

app.include_router(simulation_module.router)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Digital Twin API running"
    }

# =========================================================
# STATUS
# =========================================================

@app.get("/status")
def status():

    sim_instance = simulation_module.sim_instance

    if sim_instance is None:

        return {
            "agents": 0,
            "state": {
                "opened": 0,
                "clicked": 0,
                "infected": 0
            }
        }

    opened = sum(sim_instance.metrics["opened"])
    clicked = sum(sim_instance.metrics["clicked"])
    infected = sum(sim_instance.metrics["infected"])

    return {
        "agents": len(sim_instance.agents),
        "state": {
            "opened": opened,
            "clicked": clicked,
            "infected": infected
        }
    }