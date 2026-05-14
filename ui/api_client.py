import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

def start_simulation(payload):
    try:
        response = requests.post(f"{BASE_URL}/start", json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def step_simulation():
    try:
        response = requests.get(f"{BASE_URL}/step")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_status():
    try:
        response = requests.get(f"{BASE_URL}/status")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_graph():
    try:
        response = requests.get(f"{BASE_URL}/graph")
        return response.json()
    except Exception as e:
        return {"nodes": [], "edges": []}