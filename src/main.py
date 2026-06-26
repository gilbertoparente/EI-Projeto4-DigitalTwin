import os
import subprocess
import sys

import uvicorn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def run_streamlit():
    streamlit_path = os.path.join(os.path.dirname(sys.executable), "streamlit")
    if not os.path.exists(streamlit_path) and not os.path.exists(streamlit_path + ".exe"):
        streamlit_path = "streamlit"

    print("\n[CyberTwin] Starting UI (Streamlit)...")
    dashboard_path = os.path.join(BASE_DIR, "ui", "dashboard.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR
    subprocess.Popen([streamlit_path, "run", dashboard_path], env=env, cwd=BASE_DIR)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    os.environ["PYTHONPATH"] = BASE_DIR

    run_streamlit()

    print("[CyberTwin] Starting API Server (FastAPI)...")
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=False)