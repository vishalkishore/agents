from agents.base import BaseAgent
from core.schemas import AgentResponse
import pandas as pd

class PortfolioAgent(BaseAgent):
    def __init__(self):
        super().__init__("PortfolioAgent")
    
    async def process(self, query: str,symbol: str) -> AgentResponse:
        try:
            symbols = [word for word in query.split() if word.isupper() and len(word) < 5]
            if not symbols:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "No symbols detected"},
                    confidence=0.0
                )
            
            portfolio_data = {}
            for symbol in symbols:
                data = await self.alpha_vantage.fetch(symbol, "TIME_SERIES_DAILY")
                if data:
                    df = pd.DataFrame(data["Time Series (Daily)"]).T
                    portfolio_data[symbol] = df["close"].astype(float).pct_change().dropna()
            
            corr_matrix = pd.DataFrame(portfolio_data).corr()
            
            # Analyze with Gemini
            analysis = await self.gemini.analyze(
                f"Provide portfolio optimization advice for {len(symbols)} assets:",
                f"Correlation Matrix:\n{corr_matrix.to_string()}"
            )
            
            self.adjust_confidence(True)
            return AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis, "correlations": corr_matrix.to_dict()},
                confidence=self.confidence
            )
        except Exception as e:
            return self.handle_error(e)
