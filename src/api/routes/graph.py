from fastapi import APIRouter
from src.core import simulation_state
from src.services.graph_services import GraphService

router = APIRouter()
graph_service = GraphService()

@router.get("/graph")
def get_graph():
    sim = simulation_state.sim_instance

    if not sim:
        return {"nodes": [], "edges": []}

    return graph_service.get_graph_data(sim.agents, sim.graph)