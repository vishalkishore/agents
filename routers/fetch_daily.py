from fastapi import APIRouter, HTTPException, Query, Path
from core.logging import log_execution, log_exception
from services.alpha_vantage import AlphaVantageService
from typing import Optional
import logging
from enum import Enum

router = APIRouter(prefix="/alphavantage", tags=["alphavantage"])
alpha_vantage_service = AlphaVantageService()
logger = logging.getLogger("fetch_daily_router")

class OutputSize(str, Enum):
    COMPACT = "compact"
    FULL = "full"

class DataType(str, Enum):
    JSON = "json"
    CSV = "csv"

@router.get("/daily/{symbol}")
@log_execution
async def get_daily_data(
    symbol: str = Path(..., description="Stock symbol, e.g. IBM, AAPL"),
    outputsize: Optional[OutputSize] = Query(None, description="Data size (compact: latest 100 data points, full: 20+ years of data)"),
    datatype: DataType = Query(DataType.JSON, description="Response format (json or csv)"),
):
    try:
        extra_params = {"datatype": datatype}
        
        if outputsize:
            extra_params["outputsize"] = outputsize
        
        data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_DAILY", extra_params)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No daily data found for {symbol}")
        return data
    except Exception as e:
        log_exception(logger, e)
        raise HTTPException(status_code=500, detail=str(e))
