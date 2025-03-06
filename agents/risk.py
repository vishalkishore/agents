from agents.base import BaseAgent
from core.schemas import AgentResponse
from core.logging import log_execution
from prompts.prompts import RISK_AGENT_PROMPT
import pandas as pd
import numpy as np
from typing import Any, Dict

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent")
    
    @log_execution
    async def process(self, query: str,agent_data: Dict[str,Any]) -> AgentResponse:
        try:
            symbol = agent_data.get("symbol")
            if not symbol:
                raise ValueError("Missing 'symbol' key in agent_data")
            
            data = await self.alpha_vantage.fetch(symbol, "TIME_SERIES_INTRADAY")
            
            if not data:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "Data fetch failed"},
                    confidence=0.0
                )
            

            df = pd.DataFrame(data["Time Series (5min)"]).T
            returns = df["4. close"].astype(float).pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            analysis = await self._query_llm(
                RISK_AGENT_PROMPT,
                symbol=symbol,
                volatility=volatility,
                data= f"Recent returns:\n{returns.describe()}"
            )
            
            self.adjust_confidence(True)
            return AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis, "volatility": volatility},
                confidence=self.confidence
            )
        except Exception as e:
            return self.handle_error(e)
