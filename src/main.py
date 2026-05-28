import uvicorn
import os
import sys

# Garante que a raiz do projeto está no path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=True)