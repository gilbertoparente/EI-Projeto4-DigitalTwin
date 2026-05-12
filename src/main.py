import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Importamos o teu modelo (ajusta o caminho se necessário)
from models.digital_twin_model import DigitalTwinModel

app = FastAPI(title="Digital Twin Cybersecurity API")


# Definimos o que o utilizador pode enviar
class SimulacaoRequest(BaseModel):
    n_agentes: int = 150
    mfa_ativo: bool = False


@app.get("/")
def read_root():
    return {"status": "Online", "projeto": "Digital Twin IPVC"}


@app.post("/executar")
def executar_teste(config: SimulacaoRequest):
    # 1. Criar o modelo com os dados recebidos do browser
    modelo = DigitalTwinModel(n=config.n_agentes, mfa=config.mfa_ativo)

    # 2. Correr 1 passo
    modelo.step()

    # 3. Devolver uma resposta
    return {
        "mensagem": "Simulação iniciada",
        "agentes_no_modelo": modelo.num_agents,
        "mfa_estado": modelo.mfa_ativo
    }


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)