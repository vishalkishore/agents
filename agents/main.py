# /app # /config # __init_
# /app
#   /config
#     __init__.py
#     settings.py
#   /core
#     __init__.py
#     base.py
#     schemas.py
#   /services
#     __init__.py
#     alpha_vantage.py
#     gemini.py
#     agent_selector.py
#     aggregator.py
#     explainer.py
#     feedback.py
#   /agents
#     __init__.py
#     technical.py
#     sentiment.py
#     risk.py
#     portfolio.py
#   /routers
#     __init__.py
#     analysis.py
#     feedback.py
#   main.py

from fastapi import FastAPI
from core.logging import setup_logging
from routers import analysis
from routers import healthcheck
from config.settings import settings

setup_logging()

app = FastAPI(title="Financial Analysis Service")

app.include_router(analysis.router, prefix="/api")
app.include_router(healthcheck.router, prefix="/api")