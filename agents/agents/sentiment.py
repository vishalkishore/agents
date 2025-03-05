from typing import Any, Dict
from agents.base import BaseAgent
from core.schemas import AgentResponse
from prompts.prompts import NEWS_SENTIMENT_PROMPT

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("SentimentAgent")
    
    async def process(self, query: str, agent_data: Dict[str,Any]) -> AgentResponse:
        try:
            symbol = agent_data.get("symbol")
            if not symbol:
                raise ValueError("Missing 'symbol' key in agent_data")
            
            data = await self.alpha_vantage.fetch(symbol, "NEWS_SENTIMENT")
            
            if not data or "feed" not in data or len(data["feed"])==0:
                return AgentResponse(
                    agent_name=self.agent_name,
                    result={"error": "News fetch failed"},
                    confidence=0.0
                )
            
            news_items = [f"{item['title']} ({item['overall_sentiment_score']}) ({item['overall_sentiment_label']}) ({item['summary']}))" 
                        for item in data["feed"][:5]]
            
            analysis = await self.gemini.analyze(
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
