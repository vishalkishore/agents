from typing import Any, Dict
from agents.base import BaseAgent
from core.schemas import AgentResponse
from core.logging import log_execution
from prompts.prompts import NEWS_SENTIMENT_PROMPT
import time

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("SentimentAgent")
    
    @log_execution
    async def process(self, query: str, agent_data: Dict[str,Any]) -> AgentResponse:
        try:
            symbol = agent_data.get("symbol")
            if not symbol:
                raise ValueError("Missing 'symbol' key in agent_data")
            
            data = await self.alpha_vantage.fetch(symbol, "NEWS_SENTIMENT")
            if not data or "feed" not in data:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "News fetch failed"},
                    confidence=0.0
                )
            
            news_items = [f"{item['title']} ({item['overall_sentiment_score']})" 
                        for item in data["feed"][:5]]
            
            analysis = await self._query_llm(
                NEWS_SENTIMENT_PROMPT,
                symbol=symbol,
                news_items = news_items
            )
            
            self.adjust_confidence(True)
            return AgentResponse(
                agent_name=self.agent_name,
                result={"analysis": analysis, "news": news_items},
                confidence=self.confidence
            )
        except Exception as e:
            return self.handle_error(e)
