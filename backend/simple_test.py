from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Backend funcionando!"}

@app.get("/health")
async def health():
    return {"status": "OK"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
