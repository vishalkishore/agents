
from typing import Dict, Any


import json
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from schema.schema import Event
from etypes.event_types import EventType
from agent.coordinator import AgentCoordinator
from agent.base import BaseAgent
from agent.queryagent import QueryAnalysisAgent
from agent.datacollectionagent import DataCollectionAgent
from agent.technicalagent import TechnicalAnalysisAgent
from agent.fundamentalagent import FundamentalAnalysisAgent
from agent.sentimentagent import SentimentAnalysisAgent
from agent.riskagent import RiskAnalysisAgent
from agent.synthesisagent import ResultsSynthesisAgent
from llm.model import gemini as model


class MultiAgentTradingSystem:
    """Main system that manages all agents"""
    
    def __init__(self, config: Dict[str, str]):
        self.coordinator = AgentCoordinator()
        self._initialize_agents(config)
        
        # Start event processing
        self.event_processor = threading.Thread(
            target=self.coordinator.process_events,
            daemon=True
        )
        self.event_processor.start()
    
    def _initialize_agents(self, config: Dict[str, str]):
        """Initialize and register all agents"""
        agents = [
            QueryAnalysisAgent(config),
            DataCollectionAgent(config),
            TechnicalAnalysisAgent(config),
            FundamentalAnalysisAgent(config),
            SentimentAnalysisAgent(config),
            RiskAnalysisAgent(config),
            ResultsSynthesisAgent(config)
        ]
        
        for agent in agents:
            self.coordinator.register_agent(agent.name, agent)
    
    def analyze(self, symbol: str, query: str) -> Dict[str, Any]:
        """Start analysis process"""
        self.coordinator.publish_event(Event(
            EventType.QUERY_RECEIVED,
            {
                'symbol': symbol,
                'query': query
            },
            'system',
            'query_analyzer'
        ))
        
        return self._wait_for_results()
    
    def _wait_for_results(self) -> Dict[str, Any]:
        """Wait for and return analysis results"""
        self.coordinator.completion_event.wait(timeout=120)
        with self.coordinator.lock:
            return self.coordinator.final_result or {"error": "Analysis timed out"}

# Example usage
if __name__ == "__main__":
    config = {
        'gemini_api_key': 'your_gemini_api_key',
        'financial_api_key': 'your_financial_api_key',
        'news_api_key': 'your_news_api_key'
    }
    
    trading_system = MultiAgentTradingSystem(config)
    
    # Example complex query
    results = trading_system.analyze(
        'AAPL',
        "Analyze AAPL's technical patterns, fundamentals, and market sentiment. Assess risks and growth potential."
    )
    
    print("Analysis Results:", json.dumps(results, indent=2))