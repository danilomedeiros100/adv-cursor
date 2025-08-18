#!/usr/bin/env python3
"""
Servidor simples para testar se o problema está na aplicação principal
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Backend funcionando!"}

@app.get("/test")
async def test():
    return {"status": "OK", "message": "Test endpoint working"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Server is running"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
