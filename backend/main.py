from fastapi import FastAPI
from core.logging import setup_logging
from routers import analysis
from routers import healthcheck
from routers import fetch_intraday, fetch_daily
from config.settings import settings
from fastapi.middleware.cors import CORSMiddleware


setup_logging()

app = FastAPI(title="Financial Analysis Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api")
app.include_router(healthcheck.router, prefix="/api")
app.include_router(fetch_intraday.router,prefix="/api")
app.include_router(fetch_daily.router, prefix="/api")

app.include_router(fetch_intraday.ws_router, prefix="/ws")
app.include_router(fetch_daily.ws_router, prefix="/ws")