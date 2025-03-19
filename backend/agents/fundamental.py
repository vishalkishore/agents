from typing import Any, Dict
from agents.base import BaseAgent
from core.schemas import AgentResponse
from core.logging import log_execution
from prompts.prompts import NEWS_SENTIMENT_PROMPT

#cache wala part not added because woh samaj mai nahi aaya ,can just copy paste from technical agent 
class FundamentalAgent(BaseAgent):
    def __init__(self):
        super().__init__("FundamentalAgent")
        #abhi ke liye assume you already have symbol and hence the company name

    @log_execution
    async def process(self, query: str, agent_data: Dict[str,Any]) -> AgentResponse:
        try:
            symbol = agent_data.get("symbol")
            if not symbol:
                raise ValueError("Missing 'symbol' key in agent_data")
            data = await self.alpha_vantage.fetch(symbol, "OVERVIEW")
            #need to write code if unable to fetch
            if not data:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "Data fetch failed"},
                    confidence=0.0
                )
            
            analysis = await self._query_llm(
                FUNDAMENTAL_PROMPT,
                symbol=symbol,
                #add all the other things that need to be added to prompt
                company_data = data.to_string()
            )

            self.adjust_confidence(True)

            return AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis },
                confidence=self.confidence
            )
        except Exception as e:
            return self.handle_error(e)