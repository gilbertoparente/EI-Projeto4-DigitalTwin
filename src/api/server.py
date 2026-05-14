from fastapi import FastAPI
from src.core import simulation_state
from src.services.simulation_service import SimulationService

# 1. IMPORTA O TEU FICHEIRO DE ROTAS
# Ajusta o caminho conforme a tua estrutura (ex: src.api.routes)
try:
    from src.api.routes import graph
except ImportError:
    # Se a pasta se chamar apenas 'routes' dentro de api:
    from .routes import graph

app = FastAPI(title="Digital Twin Cybersecurity API")

# =====================================================
# ROTAS PRINCIPAIS (Diretas no server.py)
# =====================================================

@app.post("/start")
async def start(config: dict):
    simulation_state.sim_instance = SimulationService(config)
    return {
        "status": "Simulação Iniciada",
        "agentes": len(simulation_state.sim_instance.agents)
    }

@app.get("/step")
async def step():
    if not simulation_state.sim_instance:
        return {"error": "Simulação não iniciada"}
    return simulation_state.sim_instance.step()

@app.get("/status")
async def status():
    sim = simulation_state.sim_instance
    if not sim: return {"status": "idle"}
    return {"tick": sim.tick, "agents": len(sim.agents)}

# =====================================================
# REGISTO DE ROUTERS EXTERNOS
# =====================================================

# 2. INCLUI O ROUTER DO GRAPH
app.include_router(graph.router)