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
