from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.routers import session, chat, schema, query

# Ensure data directory exists
Path("./data").mkdir(exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session.router, prefix="/api", tags=["session"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(schema.router, prefix="/api", tags=["schema"])
app.include_router(query.router, prefix="/api", tags=["query"])

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


# Root
@app.get("/")
async def root():
    return {
        "message": "AIData Backend API",
        "docs": "/docs",
        "health": "/health",
    }
