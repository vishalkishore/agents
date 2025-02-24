from agents.base import BaseAgent
from core.schemas import AgentResponse
import pandas as pd
import numpy as np

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent")
    
    async def process(self, query: str,symbol: str) -> AgentResponse:
        try:
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
            
            analysis = await self.gemini.analyze(
                f"Assess risk for {symbol} with annualized volatility {volatility:.2%}:",
                f"Recent returns:\n{returns.describe()}"
            )
            
            self.adjust_confidence(True)
            return AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis, "volatility": volatility},
                confidence=self.confidence
            )
        except Exception as e:
            return self.handle_error(e)
