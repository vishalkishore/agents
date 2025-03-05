from agents.base import BaseAgent
from core.schemas import AgentResponse
from prompts.prompts import FUNDAMENTAL_AGENT_PROMT
from typing import Any, Dict

class FundamentalAgent(BaseAgent):
    def __init__(self):
        super().__init__("FundamentalAgent")
    
    async def process(self, query: str,agent_data: Dict[str,Any]) -> AgentResponse:
        try:
            symbol = agent_data.get("symbol")
            if not symbol:
                raise ValueError("Missing 'symbol' key in agent_data")
            
            data = await self.alpha_vantage.fetch(symbol, "OVERVIEW")
            
            if not data:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "Data fetch failed"},
                    confidence=0.0
                )
            

            
            analysis = await self.gemini.analyze(
                FUNDAMENTAL_AGENT_PROMT,
                symbol=symbol
            )
            
            self.adjust_confidence(True)
            return AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis},
                confidence=self.confidence
            )
        except Exception as e:
            return self.handle_error(e)
