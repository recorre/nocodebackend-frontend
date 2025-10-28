"""
FastAPI Proxy para NoCodeBackend
Deploy: Vercel - Versão Simplificada
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()  # Remove o path específico

# ========================
# APP CONFIGURATION
# ========================

app = FastAPI(
    title="Comment Widget Proxy API",
    description="Proxy para NoCodeBackend - Hackathon Edition",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# BASIC ROUTES
# ========================

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "service": "Comment Widget Proxy",
        "status": "online",
        "version": "1.0.0",
        "instance": os.getenv("INSTANCE", "41300_teste")
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Verifica se a API está funcionando"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_url": bool(os.getenv("DATABASE_URL")),
        "redis_url": bool(os.getenv("REDIS_URL"))
    }

# ========================
# VERCEL EXPORT
# ========================

# Para Vercel, apenas exportar o app
# NÃO adicionar handler = app - isso pode causar conflitos