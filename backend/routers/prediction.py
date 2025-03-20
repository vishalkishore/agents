from fastapi import APIRouter, HTTPException, Query, Path,  WebSocket, WebSocketDisconnect
from core.logging import log_execution, log_exception
from services.alpha_vantage import AlphaVantageService
from typing import Optional
import logging
import json
from enum import Enum
from services.price_tool import PricePredictionTool

router = APIRouter(tags=["prediction"])
alpha_vantage_service = AlphaVantageService()
logger = logging.getLogger("fetch_daily_router")

@router.post("/analyse_prediction")
@log_execution
async def get_daily_data(
    data: dict
):
    symbol = data.get("symbol")
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    
    price_tool = PricePredictionTool()
    prediction = await price_tool.run_analysis(symbol)
    logger.info(f"Prediction for {symbol}: {prediction}")

    return {"prediction": prediction}
