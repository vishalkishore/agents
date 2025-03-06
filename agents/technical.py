import pandas as pd
from typing import Any, Dict
from agents.base import BaseAgent
from core.schemas import AgentResponse
from services.cache import CacheService
import pandas as pd
from agents.base import BaseAgent
from core.schemas import AgentResponse
from core.logging import log_execution
from prompts.prompts import TECHNICAL_ANALYSIS_PROMPT

class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__("TechnicalAgent")
        self.cache = CacheService()

    @log_execution
    async def process(self, query: str, agent_data: Dict[str,Any]) -> AgentResponse:
        self.logger.info(f"Technical analysis agent processing query: {query}")
        try:
            symbol = agent_data.get("symbol")
            if not symbol:
                raise ValueError("Missing 'symbol' key in agent_data")
            
            cache_key = self.cache.build_key("technical_analysis", symbol, query)

            cached_analysis = await self.cache.get(cache_key)
            if cached_analysis:
                self.logger.info(f"Cache hit for techinical analysis of {symbol}")
                return AgentResponse(**cached_analysis)
            
            self.logger.info(f"No cache found for {symbol}")

            data = await self.alpha_vantage.fetch(symbol, "TIME_SERIES_INTRADAY")
            
            if not data:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "Data fetch failed"},
                    confidence=0.0
                )

            df = self._prepare_dataframe(data)
            analysis = await self._analyze_data(df, symbol)
            
            self.adjust_confidence(True)
            response =  AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis, "indicators": df.tail(1).to_dict()},
                confidence=self.confidence
            )
            await self.cache.set(cache_key, response.dict())
            return response
        
        except Exception as e:
            return self.handle_error(e)

    def _prepare_dataframe(self, data: dict) -> pd.DataFrame:
        columns = {
                'index' : 'timestamp',
                '1. open' : 'open',
                '2. high' : 'high',
                '3. low' : 'low',
                '4. close' : 'close',
                '5. adjusted close' : 'adjusted_close',
                '6. volume' : 'volume',
                '5. volume' : 'volume',
                '7. dividend amount' : 'dividend_amount',
                '8. split coefficient' : 'split_coefficient'
            }

        time_series_keys = [key for key in data if key.startswith("Time Series")]

        if not time_series_keys:
            raise ValueError("Time Series data not found in the input dictionary")
        time_series_key = time_series_keys[0]

        df = pd.DataFrame(data[time_series_key]).T.reset_index()
        df = df.rename(columns=columns)
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        df['20ma'] = df['close'].rolling(20).mean()
        df['rsi'] = self._calculate_rsi(df['close'])
        
        return df

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    async def _analyze_data(self, df: pd.DataFrame, symbol: str) -> str:
        return await self.gemini.analyze(
            TECHNICAL_ANALYSIS_PROMPT,
            symbol=symbol,
            data=df.tail(30).describe().to_string()
        )
