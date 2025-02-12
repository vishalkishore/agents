from .base import BaseAgent
from typing import Dict, List, Any, Optional, Tuple
from etypes.event_types import EventType
from schema.schema import Event
from llm.model import gemini as model

class SentimentAnalysisAgent(BaseAgent):
    """Enhanced Sentiment Analysis Agent"""
    
    def __init__(self, config: Dict[str, str]):
        super().__init__("sentiment_analyzer", config)
    
    def handle_event(self, event: Event):
        if event.type == EventType.DATA_READY:
            self.logger.info("Performing sentiment analysis")
            try:
                analysis = self._perform_analysis(event.data)
                analysis.update({
                    'symbol': event.data['symbol'],
                    'query': event.data.get('query', ''),
                    'agent_type': self.name
                })

                self.publish_event(Event(
                    EventType.ANALYSIS_COMPLETED,
                    analysis,
                    self.name,
                    "coordinator"
                ))
            except Exception as e:
                self.logger.error(f"Sentiment analysis failed: {e}")
                self.publish_event(Event(
                    EventType.ERROR_OCCURRED,
                    {"error": str(e), "stage": "sentiment_analysis"},
                    self.name
                ))
    
    def _perform_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        return {
            'news_sentiment': 0.75,
            'social_sentiment': 0.82 
        }
