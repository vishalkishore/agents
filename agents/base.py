from abc import ABC, abstractmethod
from services.alpha_vantage import AlphaVantageService
from services.gemini import GeminiService
from core.schemas import AgentResponse
from core.logging import log_exception
import logging

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(agent_name)
        self.alpha_vantage = AlphaVantageService()
        self.gemini = GeminiService()
        self.confidence = 0.9

    @abstractmethod
    async def process(self, query: str, symbol: str) -> AgentResponse:
        pass

    def adjust_confidence(self, success: bool):
        adjustment = 0.1 if success else -0.1
        self.confidence = min(max(self.confidence + adjustment, 0), 1)

    def handle_error(self, e: Exception) -> AgentResponse:
        log_exception(self.logger, e)
        return AgentResponse(
            agent_name=self.agent_name,
            result={"error": str(e)},
            confidence=0.0
        )
