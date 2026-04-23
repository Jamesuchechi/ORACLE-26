"""
ORACLE-26 — Main API Entry Point
==================================
FastAPI application for the WC2026 Prediction Engine.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

app = FastAPI(
    title="🔮 ORACLE-26 API",
    description="Multi-Signal Intelligence Engine for FIFA World Cup 2026",
    version="1.0.0"
)

# CORS configuration for Interactive App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to ORACLE-26",
        "docs": "/docs",
        "status": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
