import requests

BASE_URL = "http://127.0.0.1:8000"


def start_simulation(payload):
    try:
        r = requests.post(f"{BASE_URL}/start", json=payload)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def step_simulation():
    try:
        r = requests.get(f"{BASE_URL}/step")
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_status():
    try:
        r = requests.get(f"{BASE_URL}/status")
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_graph():
    try:
        r = requests.get(f"{BASE_URL}/graph")
        return r.json()
    except Exception as e:
        return {"nodes": [], "edges": []}


def get_metrics():
    try:
        r = requests.get(f"{BASE_URL}/metrics")
        return r.json()
    except Exception as e:
        return []


def get_departments():
    try:
        r = requests.get(f"{BASE_URL}/departments")
        return r.json()
    except Exception as e:
        return {}


def run_analytics(config: dict, ticks: int, attack_type: str):
    try:
        r = requests.post(f"{BASE_URL}/analytics/run",
                          json={"config": config, "ticks": ticks, "attack_type": attack_type})
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def start_scenarios(config_a: dict, config_b: dict):
    try:
        r = requests.post(f"{BASE_URL}/scenarios/start",
                          json={"scenario_a": config_a, "scenario_b": config_b})
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def step_scenarios(n: int = 1):
    try:
        r = requests.get(f"{BASE_URL}/scenarios/step", params={"n": n})
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_scenarios_status():
    try:
        r = requests.get(f"{BASE_URL}/scenarios/status")
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_scenarios_compare():
    try:
        r = requests.get(f"{BASE_URL}/scenarios/compare")
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_history():
    try:
        r = requests.get(f"{BASE_URL}/history")
        return r.json()
    except Exception as e:
        return {"runs": []}


def get_history_steps(run_id: int):
    try:
        r = requests.get(f"{BASE_URL}/history/steps/{run_id}")
        return r.json()
    except Exception as e:
        return []