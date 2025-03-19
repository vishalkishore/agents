from fastapi import APIRouter, HTTPException, Query, Path,  WebSocket, WebSocketDisconnect
from core.logging import log_execution, log_exception
from services.alpha_vantage import AlphaVantageService
from typing import Optional
import logging
import json
from enum import Enum

router = APIRouter(tags=["fetch_intraday"])
ws_router = APIRouter(tags=["ws_fetch_intraday"])
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

@ws_router.websocket("/daily/{symbol}")
@log_execution
async def websocket_daily_data(
    websocket: WebSocket,
    symbol: str,
    outputsize: Optional[str] = None,
    datatype: str = "json"
):
    await websocket.accept()
    
    try:
        try:
            if outputsize:
                outputsize = OutputSize(outputsize)
            datatype = DataType(datatype)
        except ValueError as e:
            await websocket.send_json({"error": f"Invalid parameter: {str(e)}"})
            await websocket.close()
            return
            
        # Prepare parameters
        extra_params = {"datatype": datatype}
        if outputsize:
            extra_params["outputsize"] = outputsize
            
        # Get initial data
        data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_DAILY", extra_params)
        
        if not data:
            await websocket.send_json({"error": f"No daily data found for {symbol}"})
            await websocket.close()
            return
            
        # Send initial data
        if datatype == DataType.JSON:
            await websocket.send_json(data)
        else:
            await websocket.send_text(data)
        
        while True:
            message = await websocket.receive_text()
            request = json.loads(message)
            
            # Handle client commands
            if request.get("action") == "refresh":
                data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_DAILY", extra_params)
                if datatype == DataType.JSON:
                    await websocket.send_json(data)
                else:
                    await websocket.send_text(data)
            elif request.get("action") == "update_params":
                if "outputsize" in request:
                    try:
                        outputsize = OutputSize(request["outputsize"])
                        extra_params["outputsize"] = outputsize
                    except ValueError:
                        await websocket.send_json({"error": f"Invalid outputsize: {request['outputsize']}"})
                        continue
                        
                if "datatype" in request:
                    try:
                        datatype = DataType(request["datatype"])
                        extra_params["datatype"] = datatype
                    except ValueError:
                        await websocket.send_json({"error": f"Invalid datatype: {request['datatype']}"})
                        continue

                data = await alpha_vantage_service.fetch(symbol, "TIME_SERIES_DAILY", extra_params)
                if datatype == DataType.JSON:
                    await websocket.send_json(data)
                else:
                    await websocket.send_text(data)
            else:
                await websocket.send_json({"error": "Unknown action"})
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from daily data stream for {symbol}")
    except Exception as e:
        log_exception(logger, e)
        try:
            await websocket.send_json({"error": str(e)})
            await websocket.close()
        except:
            pass