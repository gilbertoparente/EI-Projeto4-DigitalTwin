import os
import sys
import subprocess
import uvicorn

# 1. Calcula dinamicamente a raiz do projeto (DigitalTwin/)
# __file__ é 'src/main.py', o primeiro dirname dá 'src/', o segundo dá 'DigitalTwin/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Garante que a raiz do projeto está no path do Python
sys.path.append(BASE_DIR)


def run_streamlit():
    """Inicia o Streamlit num processo separado utilizando caminhos absolutos."""
    # Deteta o caminho correto para o executável do Streamlit dentro do teu venv
    streamlit_path = os.path.join(os.path.dirname(sys.executable), "streamlit")

    if not os.path.exists(streamlit_path) and not os.path.exists(streamlit_path + ".exe"):
        streamlit_path = "streamlit"

    print("\n🚀 [CyberTwin] A iniciar a Interface Gráfica (Streamlit)...")

    # Calcula o caminho absoluto para o ficheiro dashboard.py
    dashboard_path = os.path.join(BASE_DIR, "ui", "dashboard.py")

    # Passamos as variáveis de ambiente necessárias
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR

    # Executa o Streamlit apontando para o caminho absoluto do ficheiro
    # e força o diretório de trabalho (cwd) para a raiz do projeto
    subprocess.Popen([streamlit_path, "run", dashboard_path], env=env, cwd=BASE_DIR)


if __name__ == "__main__":
    # Força o script a trabalhar a partir da raiz do projeto,
    # não importa onde foi chamado ou clicado.
    os.chdir(BASE_DIR)
    os.environ["PYTHONPATH"] = BASE_DIR

    # Disparar o Streamlit em segundo plano
    run_streamlit()

    print("⚡ [CyberTwin] A iniciar o Servidor API (FastAPI)...")

    # Inicia o Uvicorn no processo principal
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=False)