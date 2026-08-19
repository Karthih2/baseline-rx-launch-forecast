"""
Drug Launch Forecasting Backend -- FastAPI entry point.

Run with:
    uvicorn app.main:app --reload --port 8000

Docs available at /docs once running.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import forecast_router

app = FastAPI(
    title="Drug Launch Forecasting API",
    description=(
        "Modular backend implementing the Analog + Bass Static forecasting "
        "process: data validation, preprocessing, feature engineering, "
        "cosine-similarity analog selection, weighted analog curve blending, "
        "Bass diffusion modelling, Bull/Base/Bear scenario analysis, and "
        "CSV export -- fully reusable across different drugs/analog sets."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Drug Launch Forecasting API is running"}
