from fastapi import FastAPI
from core.logging import setup_logging
from routers import analysis
from routers import healthcheck
from routers import fetch_intraday, fetch_daily
from config.settings import settings

setup_logging()

app = FastAPI(title="Financial Analysis Service")

app.include_router(analysis.router, prefix="/api")
app.include_router(healthcheck.router, prefix="/api")
app.include_router(fetch_intraday.router,prefix="/api")
app.include_router(fetch_daily.router, prefix="/api")

app.include_router(fetch_intraday.ws_router, prefix="/ws")
app.include_router(fetch_daily.ws_router, prefix="/ws")