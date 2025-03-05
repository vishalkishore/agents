import requests
from typing import Any,Optional, Dict
import logging
from core.logging import log_exception
from config.settings import settings
from agents.base import BaseAgent
from services.cache import CacheService
from prompts.prompts import TOPIC_GENERATION_PROMPT

class AlphaVantageService(BaseAgent):
    def __init__(self):
        super().__intit__("alpha_vantage")
        self.api_key = settings.ALPHA_VANTAGE_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.logger = logging.getLogger("AlphaVantageService")
        self.cache = CacheService()

    async def fetch(self, symbol: str, function: str,query: str, extra_params: Optional[Dict] = None, topics: Optional[str]=None) -> Optional[Dict]:
        try:
            self.logger.info(f"Fetching {function} data for {symbol}")
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
            selected_topics  = await self.gemini.analyze(
                TOPIC_GENERATION_PROMPT,
                symbol=symbol,
                query=query

            )
    
            if function in ["TIME_SERIES_INTRADAY"]:
                params.setdefault("interval", "5min")
            if function == "NEWS_SENTIMENT":
                params.setdefault("sort", "RELEVANCE")
                if selected_topics in ["Blockchain", "Earnings","IPO","Mergers & Acquisitions","Financial Markets",
                             "Economy - Fiscal Policy","Economy - Monetary Policy","Economy - Macro/Overall",
                             "Energy & Transportation","Finance","Life Sciences","Manufacturing","Real Estate & Construction",
                             "Retail & Wholesale","Technology"]:
                        params["topic"] = selected_topics

            if extra_params:
                params.update(extra_params)

            self.logger.info(f"Fetching {function} data for {symbol}")
            response = requests.get(self.base_url, params=params)
            data = response.json()

            # self.logger.info(f"Received {data} data for {symbol}")
            
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