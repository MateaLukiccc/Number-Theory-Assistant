from fastapi import FastAPI
import uvicorn
from chromadb import PersistentClient
from functools import lru_cache

app = FastAPI()

@lru_cache(maxsize=1)
def get_chroma_client():
    return PersistentClient(path="./chroma_db")

@app.get("/health_check")
def get_health():
    get_chroma_client()
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)