from fastapi import APIRouter, HTTPException, Query, Path
from core.logging import log_execution, log_exception
from services.alpha_vantage import AlphaVantageService
from typing import Optional
import logging
from enum import Enum

from core.logging import log_exception, log_execution
from config.settings import settings

router = APIRouter(prefix="/alphavantage", tags=["alphavantage"])
alpha_vantage_service = AlphaVantageService()
logger = logging.getLogger("fetch_intraday_router")

class TimeSeriesInterval(str, Enum):
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    SIXTY_MIN = "60min"

class OutputSize(str, Enum):
    COMPACT = "compact"
    FULL = "full"

class DataType(str, Enum):
    JSON = "json"
    CSV = "csv"

@router.get("/intraday/{symbol}")
@log_execution
async def get_intraday_data(
    symbol: str = Path(..., description="Stock symbol, e.g. IBM, AAPL"),
    interval: TimeSeriesInterval = Query(TimeSeriesInterval.FIVE_MIN, description="Time interval between data points"),
    adjusted: bool = Query(True, description="Whether to return adjusted data"),
    extended_hours: bool = Query(False, description="Whether to include extended hours data"),
    month: Optional[str] = Query(None, description="Specific month to query (format: YYYY-MM)"),
    outputsize: Optional[OutputSize] = Query(None, description="Data size (compact: latest 100 data points, full: trailing 30 days)"),
    datatype: DataType = Query(DataType.JSON, description="Response format (json or csv)"),
):
    try:
        extra_params = {
            "interval": interval,
            "adjusted": str(adjusted).lower(),
            "extended_hours": str(extended_hours).lower(),
            "datatype": datatype
        }
        
        if month:
            extra_params["month"] = month
        
        if outputsize:
            extra_params["outputsize"] = outputsize
        
        data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_INTRADAY", extra_params)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No intraday data found for {symbol}")
        return data
    except Exception as e:
        log_exception(logger, e)
        raise HTTPException(status_code=500, detail=str(e))