from .base import BaseAgent
from typing import Dict, List, Any, Optional, Tuple
from etypes.event_types import EventType
from schema.schema import Event
from llm.model import gemini as model
import json
import pandas as pd

class TechnicalAnalysisAgent(BaseAgent):
    """Enhanced Technical Analysis Agent"""
    
    def __init__(self, config: Dict[str, str]):
        super().__init__("technical_analyzer", config)
        self.model = model
    
    def handle_event(self, event: Event):
        self.logger.info(f"Handling event: {event.type}")
        if event.type == EventType.DATA_READY:
            self.logger.info("Performing technical analysis")
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
                self.logger.error(f"Technical analysis failed: {e}")
                self.publish_event(Event(
                    EventType.ERROR_OCCURRED,
                    {"error": str(e), "stage": "technical_analysis"},
                    self.name
                ))
    
    def _perform_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform technical analysis using Gemini and traditional methods"""
        df = pd.DataFrame(data['market']['history'])
        
        # Calculate technical indicators
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        latest = df.iloc[-1].to_dict()
        
        # Generate Gemini interpretation
        analysis = {"indicators": latest}
        if self.model:
            prompt = f"Interpret these technical indicators: {latest}"
            response = self.model.generate_content(prompt)
            analysis['interpretation'] = response.text
            self.logger.info(f"Technical analysis: {analysis}")
        
        return analysis
