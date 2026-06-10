import requests

BASE_URL = "http://127.0.0.1:8000"


# ── Simulação principal ──────────────────────────────────────────────────────

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


# ── Comparação de cenários ───────────────────────────────────────────────────

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


# ── Departamentos guardados ──────────────────────────────────────────────────

def save_department(name: str, department: dict):
    try:
        r = requests.post(f"{BASE_URL}/departments/save",
                          json={"name": name, "department": department})
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def list_saved_departments():
    try:
        r = requests.get(f"{BASE_URL}/departments/saved")
        return r.json()
    except Exception as e:
        return {"departments": {}}


def get_saved_department(name: str):
    try:
        r = requests.get(f"{BASE_URL}/departments/saved/{name}")
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def delete_saved_department(name: str):
    try:
        r = requests.delete(f"{BASE_URL}/departments/saved/{name}")
        return r.json()
    except Exception as e:
        return {"error": str(e)}