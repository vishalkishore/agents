from fastapi import APIRouter, HTTPException, Query, Path, WebSocket, WebSocketDisconnect
from core.logging import log_execution, log_exception
from services.alpha_vantage import AlphaVantageService
from typing import Optional
import logging
from enum import Enum
import json
from core.logging import log_exception, log_execution
from config.settings import settings

router = APIRouter(tags=["fetch_intraday"])
ws_router = APIRouter(tags=["ws_fetch_intraday"])
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
    
@ws_router.websocket("/intraday/{symbol}")
@log_execution
async def websocket_intraday_data(
    websocket: WebSocket,
    symbol: str,
    interval: str = "5min",
    adjusted: str = "true",
    extended_hours: str = "false",
    month: Optional[str] = None,
    outputsize: Optional[str] = None,
    datatype: str = "json"
):
    await websocket.accept()
    
    try:
        # Initialize parameters
        param_validators = {
            "interval": lambda v: TimeSeriesInterval(v),
            "outputsize": lambda v: OutputSize(v) if v else None,
            "datatype": lambda v: DataType(v),
            "adjusted": lambda v: str(v).lower() == "true",
            "extended_hours": lambda v: str(v).lower() == "true",
            "month": lambda v: v
        }
        
        param_values = {
            "interval": interval,
            "adjusted": adjusted,
            "extended_hours": extended_hours,
            "month": month,
            "outputsize": outputsize,
            "datatype": datatype
        }

        try:
            validated_params = {}
            for key, validator in param_validators.items():
                if param_values[key] is not None:
                    validated_params[key] = validator(param_values[key])
        except ValueError as e:
            await websocket.send_json({"error": f"Invalid parameter: {str(e)}"})
            await websocket.close()
            return
        
        current_datatype = validated_params.get("datatype", DataType.JSON)
        extra_params = {
            "interval": validated_params.get("interval"),
            "adjusted": str(validated_params.get("adjusted", True)).lower(),
            "extended_hours": str(validated_params.get("extended_hours", False)).lower(),
            "datatype": current_datatype
        }
        
        if validated_params.get("month"):
            extra_params["month"] = validated_params.get("month")
        
        if validated_params.get("outputsize"):
            extra_params["outputsize"] = validated_params.get("outputsize")
            
        data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_INTRADAY", extra_params)
        
        if not data:
            await websocket.send_json({"error": f"No intraday data found for {symbol}"})
            await websocket.close()
            return
            
        if current_datatype == DataType.JSON:
            await websocket.send_json(data)
        else:
            await websocket.send_text(data)
            
        while True:
            message = await websocket.receive_text()
            request = json.loads(message)
            
            if request.get("action") == "refresh":
                data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_INTRADAY", extra_params)
                if current_datatype == DataType.JSON:
                    await websocket.send_json(data)
                else:
                    await websocket.send_text(data)
                    
            elif request.get("action") == "update_params":
                params_changed = False
                validation_errors = []
                
                for param_name, validator in param_validators.items():
                    if param_name in request:
                        try:
                            new_value = validator(request[param_name])
                            
                            if param_name not in validated_params or validated_params[param_name] != new_value:
                                validated_params[param_name] = new_value
                                params_changed = True

                                if param_name == "datatype":
                                    current_datatype = new_value
                        except ValueError as e:
                            validation_errors.append(f"Invalid {param_name}: {request[param_name]}")
                
                if validation_errors:
                    await websocket.send_json({"errors": validation_errors})
                    continue
                
                if params_changed:
                    extra_params = {
                        "interval": validated_params.get("interval"),
                        "adjusted": str(validated_params.get("adjusted", True)).lower(),
                        "extended_hours": str(validated_params.get("extended_hours", False)).lower(),
                        "datatype": current_datatype
                    }
                    
                    if validated_params.get("month"):
                        extra_params["month"] = validated_params.get("month")
                    
                    if validated_params.get("outputsize"):
                        extra_params["outputsize"] = validated_params.get("outputsize")
                    
                    data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_INTRADAY", extra_params)
                    if current_datatype == DataType.JSON:
                        await websocket.send_json(data)
                    else:
                        await websocket.send_text(data)
                else:
                    await websocket.send_json({"message": "No parameters changed"})
            else:
                await websocket.send_json({"error": "Unknown action"})
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from intraday data stream for {symbol}")
    except Exception as e:
        log_exception(logger, e)
        try:
            await websocket.send_json({"error": str(e)})
            await websocket.close()
        except:
            pass