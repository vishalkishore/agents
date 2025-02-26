# services/agent_selector.py
from typing import List, Tuple, Dict, Type
import json
import logging
from core.logging import log_exception
from services.gemini import GeminiService
from agents.base import BaseAgent
from agents.technical import TechnicalAgent
from agents.sentiment import SentimentAgent
from agents.risk import RiskAgent
from agents.portfolio import PortfolioAgent
from config.settings import settings
from prompts.prompts import AGENT_SELECTOR_PROMPT

class AgentSelector:
    def __init__(self):
        self.logger = logging.getLogger("AgentSelector")
        self.gemini = GeminiService()
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize agent mapping based on configuration"""
        self.agent_mapping: Dict[str, Type[BaseAgent]] = {
            "technical": TechnicalAgent,
            "sentiment": SentimentAgent,
            "risk": RiskAgent,
            "portfolio": PortfolioAgent
        }
        
        # Filter out disabled agents from settings
        self.available_agents = {
            name: agent_class 
            for name, agent_class in self.agent_mapping.items()
            if settings.AGENT_CONFIGS[name]["enabled"]
        }

    async def select_agents(self, query: str) -> Tuple[List[BaseAgent], str]:
        try:
            prompt = self._build_selection_prompt(query)
            response_text = await self.gemini.analyze(prompt)
            # Parse the response
            try:
                response = json.loads(response_text)
                selected_agents = response.get('selected', [])
                symbol = response.get('symbol', '').strip().upper()
            except json.JSONDecodeError as e:
                log_exception(self.logger, e, "Failed to parse Gemini response")
                # Fallback to default selection
                selected_agents = ['technical','sentiment']
                symbol = self._extract_symbol_fallback(query)

            # Validate symbol
            if not symbol:
                symbol = self._extract_symbol_fallback(query)
                self.logger.warning(f"Using fallback symbol detection: {symbol}")

            agents = self._initialize_selected_agents(selected_agents)
            response['symbol'] = symbol
            self.logger.info(f"Selected agents: {[a.__class__.__name__ for a in agents]} for symbol: {symbol}")
            return agents, response

        except Exception as e:
            log_exception(self.logger, e, "Agent selection failed")
            # Fallback to technical analysis only
            return [TechnicalAgent()], "IBM"

    def _build_selection_prompt(self, query: str) -> str:
        available_agents = list(self.available_agents.keys()) if self.available_agents else []
        return AGENT_SELECTOR_PROMPT.format(available_agents=", ".join(available_agents), query=query)

    def _initialize_selected_agents(self, selected_agents: List[str]) -> List[BaseAgent]:
        """Initialize the selected agents"""
        initialized_agents = []
        
        for agent_name in selected_agents:
            if agent_name in self.available_agents:
                try:
                    agent_class = self.available_agents[agent_name]
                    initialized_agents.append(agent_class())
                except Exception as e:
                    log_exception(self.logger, e, f"Failed to initialize {agent_name}")
        
        # Ensure at least technical agent is included
        if not initialized_agents:
            self.logger.warning("No valid agents selected, falling back to TechnicalAgent")
            initialized_agents.append(TechnicalAgent())
            
        return initialized_agents

    def _extract_symbol_fallback(self, query: str) -> str:
        """Fallback method to extract symbol from query"""
        common_symbols = ["IBM", "AAPL", "GOOGL", "MSFT", "AMZN"]
        
        for symbol in common_symbols:
            if symbol in query.upper():
                return symbol
                
        return "IBM" 
