from .base import BaseAgent
from typing import Dict, List, Any, Optional, Tuple
from etypes.event_types import EventType
from schema.schema import Event
from llm.model import gemini as model
import json
import yfinance as yf

class DataCollectionAgent(BaseAgent):
    """Agent responsible for collecting and preparing data"""
    
    def __init__(self, config: Dict[str, str]):
        super().__init__("data_collector", config)
        self.data_sources = self._initialize_data_sources()
    
    def handle_event(self, event: Event):
        if event.type == EventType.ANALYSIS_REQUESTED:
            self.logger.info("Starting data collection")
            try:
                data = self._collect_data(event.data)
                self.publish_event(Event(
                    EventType.DATA_READY,
                    data,
                    self.name,
                    "coordinator"
                ))
            except Exception as e:
                self.logger.error(f"Data collection failed: {e}")
                self.publish_event(Event(
                    EventType.ERROR_OCCURRED,
                    {"error": str(e), "stage": "data_collection"},
                    self.name
                ))
    
    def _initialize_data_sources(self) -> Dict[str, Any]:
        """Initialize connections to different data sources"""
        return {
            'market': yf.Ticker,
            'news': lambda symbol: [f"News article about {symbol}"],
            'social': lambda symbol: [f"Social post about {symbol}"]
        }
    
    def _collect_data(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Collect required data from various sources"""
        symbol = requirements.get('symbol', 'AAPL')
        collected_data = {'symbol': symbol}
        
        # Market data
        ticker = self.data_sources['market'](symbol)
        hist = ticker.history(period="1y")
        collected_data['market'] = {
            'history': hist.to_dict(),
            'info': ticker.info
        }
        # News data
        collected_data['news'] =  "News data not available "#self.data_sources['news'](symbol)
        
        # Social data
        collected_data['social'] = "Social data not available " #self.data_sources['social'](symbol)
        
        return collected_data
