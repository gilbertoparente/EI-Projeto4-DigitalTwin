import uvicorn
from fastapi import FastAPI


app = FastAPI()

# ...  endpoints ...

if __name__ == "__main__":
    # Define o host como 0.0.0.0 para ser acessível na rede local se necessário
    # O porto 8000 é o padrão do FastAPI
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)