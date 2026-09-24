# ---------------------------------------------------------
# PCB AI Inspection System
# FastAPI Main Application
# ---------------------------------------------------------

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.api.inspection import (
    router as inspection_router
)

from backend.app.api.dashboard import (
    router as dashboard_router
)


# ---------------------------------------------------------
# Project root directory
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------
# Frontend directory
# ---------------------------------------------------------

FRONTEND_DIR = (
    PROJECT_ROOT / "frontend"
)


# ---------------------------------------------------------
# Prediction directory
# ---------------------------------------------------------

PREDICTION_DIR = (
    PROJECT_ROOT
    / "backend"
    / "predictions"
)


# ---------------------------------------------------------
# Create FastAPI application
# IMPORTANT: app must be created BEFORE app.mount()
# ---------------------------------------------------------

app = FastAPI(
    title="PCB AI Inspection System",
    description="AI-powered PCB defect inspection backend",
    version="1.0.0"
)


# ---------------------------------------------------------
# Register inspection API
# ---------------------------------------------------------

app.include_router(
    inspection_router
)

app.include_router(
    dashboard_router
)


# ---------------------------------------------------------
# Serve frontend files
# ---------------------------------------------------------

app.mount(
    "/frontend",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="frontend"
)


# ---------------------------------------------------------
# Serve prediction images
# ---------------------------------------------------------

app.mount(
    "/predictions",
    StaticFiles(
        directory=PREDICTION_DIR
    ),
    name="predictions"
)


# ---------------------------------------------------------
# Main frontend page
# ---------------------------------------------------------

@app.get("/")
def root():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ---------------------------------------------------------
# Health check API
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():

    return {
        "status": "ok",
        "service": "PCB AI Inspection API"
    }