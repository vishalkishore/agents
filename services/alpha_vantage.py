import requests
from typing import Optional, Dict
import logging
from core.logging import log_exception
from config.settings import settings
from services.cache import CacheService

class AlphaVantageService:
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.logger = logging.getLogger("AlphaVantageService")
        self.cache = CacheService()

    async def fetch(self, symbol: str, function: str) -> Optional[Dict]:
        try:
            self.logger.info(f"Fetching {function} data for {symbol}")
            symbol = "IBM"
            cache_key = self.cache.build_key("alphavantage", symbol, function)

            cached_data = await self.cache.get(cache_key)
            if cached_data:
                self.logger.info(f"Cache hit for {symbol} {function}")
                return cached_data
            
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            if function in ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY"]:
                params["interval"] = "5min"

            self.logger.info(f"Fetching {function} data for {symbol}")
            response = requests.get(self.base_url, params=params)
            data = response.json()

            self.logger.info(f"Received {data} data for {symbol}")
            
            if "Error Message" in data:
                raise ValueError(data["Error Message"])
            
            if "Information" in data and "rate limit" in data["Information"].lower():
                raise ValueError("API rate limit exceeded")
            self.logger.info(f"Setting cache for {symbol} {function}")
            await self.cache.set(cache_key, data)
            
            return data
        except Exception as e:
            log_exception(self.logger, e, "AlphaVantage fetch error:")
            return None