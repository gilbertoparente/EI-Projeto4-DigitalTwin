import sqlite3
import json
from datetime import datetime
from fastapi import FastAPI
from src.api.routes import graph
from src.core import simulation_state
from src.services.simulation_service import SimulationService


def init_db():
    conn = sqlite3.connect("database/digital_twin.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS simulation_runs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, experiment_type TEXT, 
                       attack_type TEXT, total_compromised INTEGER, num_agents INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS simulation_configs 
                      (run_id INTEGER, config_json TEXT)""")
    # NOVA TABELA: Guarda a topologia da rede/grafo gerado para esta run
    cursor.execute("""CREATE TABLE IF NOT EXISTS simulation_graphs 
                      (run_id INTEGER, graph_json TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS simulation_steps 
                      (run_id INTEGER, tick INTEGER, opened INTEGER, clicked INTEGER, infected INTEGER)""")
    conn.commit()
    conn.close()


init_db()

app = FastAPI(title="Digital Twin Cybersecurity API")


@app.post("/start")
async def start(config: dict):
    # 1. Inicialização original (aqui dentro gera-se o self.graph)
    simulation_state.sim_instance = SimulationService(config)

    experiment_type = config.get("experiment_label", "Live System Run")

    # 2. Gravar o início na Base de Dados
    conn = sqlite3.connect("database/digital_twin.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO simulation_runs (timestamp, experiment_type, attack_type, num_agents, total_compromised) VALUES (?, ?, ?, ?, ?)",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            experiment_type,
            config.get("attack", {}).get("type", "Unknown"),
            len(simulation_state.sim_instance.agents),
            0
        )
    )
    run_id = cursor.lastrowid

    # Guardar a configuração JSON
    cursor.execute(
        "INSERT INTO simulation_configs (run_id, config_json) VALUES (?, ?)",
        (run_id, json.dumps(config))
    )

    # NOVO: Guardar o grafo gerado automaticamente pelo SimulationService
    generated_graph = simulation_state.sim_instance.graph
    cursor.execute(
        "INSERT INTO simulation_graphs (run_id, graph_json) VALUES (?, ?)",
        (run_id, json.dumps(generated_graph))
    )

    conn.commit()
    conn.close()

    simulation_state.sim_instance.run_id = run_id

    return {
        "status": "Simulation Started",
        "agents": len(simulation_state.sim_instance.agents),
        "edges": sum(len(edges) for edges in simulation_state.sim_instance.graph.values()),
        "run_id": run_id
    }


@app.get("/step")
async def step():
    if not simulation_state.sim_instance:
        return {"error": "Simulation not started"}

    data = simulation_state.sim_instance.step()

    run_id = getattr(simulation_state.sim_instance, "run_id", None)
    if run_id:
        conn = sqlite3.connect("database/digital_twin.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO simulation_steps VALUES (?, ?, ?, ?, ?)",
            (run_id, data['tick'], data['result']['opened'], data['result']['clicked'], data['result']['infected'])
        )
        cursor.execute(
            "UPDATE simulation_runs SET total_compromised = ? WHERE id = ?",
            (data['total_compromised'], run_id)
        )
        conn.commit()
        conn.close()

    return data


@app.get("/status")
async def status():
    sim = simulation_state.sim_instance
    if not sim:
        return {"status": "idle"}
    return {"status": "ready", "tick": sim.tick, "agents": len(sim.agents)}


@app.get("/history")
async def get_history():
    conn = sqlite3.connect("database/digital_twin.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulation_runs ORDER BY id DESC")
    runs = cursor.fetchall()

    history_list = []
    for run in runs:
        run_id = run[0]

        # Puxa o JSON da configuração
        cursor.execute("SELECT config_json FROM simulation_configs WHERE run_id = ?", (run_id,))
        config_row = cursor.fetchone()
        config_json = config_row[0] if config_row else "{}"

        # NOVO: Puxa o JSON do grafo correspondente
        cursor.execute("SELECT graph_json FROM simulation_graphs WHERE run_id = ?", (run_id,))
        graph_row = cursor.fetchone()
        graph_json = graph_row[0] if graph_row else "{}"

        history_list.append({
            "id": run_id,
            "timestamp": run[1],
            "experiment_type": run[2],
            "attack_type": run[3],
            "total_compromised": run[4],
            "num_agents": run[5],
            "config": json.loads(config_json),
            "graph": json.loads(graph_json)  # Disponível para a UI desenhar se quiseres
        })

    conn.close()
    return {"runs": history_list}


@app.get("/history/steps/{run_id}")
async def get_history_steps(run_id: int):
    conn = sqlite3.connect("database/digital_twin.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tick, opened, clicked, infected FROM simulation_steps WHERE run_id = ? ORDER BY tick ASC",
                   (run_id,))
    steps = cursor.fetchall()
    conn.close()
    return [{"tick": s[0], "opened": s[1], "clicked": s[2], "infected": s[3]} for s in steps]


app.include_router(graph.router)