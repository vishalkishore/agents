from abc import ABC, abstractmethod
from typing import Dict, Any
from services.alpha_vantage import AlphaVantageService
from services.llm import GeminiService, ChatGPTService
from core.schemas import AgentResponse
from core.logging import log_exception, get_agent_logger
from config.settings import settings

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = get_agent_logger(agent_name)
        self.alpha_vantage = AlphaVantageService()

        self.llms = self._initialize_llms()

        self.confidence = 0.9

    def _initialize_llms(self):
        llm_instances = []
        for llm in settings.LLM_PIORITY:
            if llm == "OPENAI":
                llm_instances.append(ChatGPTService())
            elif llm == "GEMINI":
                llm_instances.append(GeminiService())
        return llm_instances
    
    async def _query_llm(self, query: str, **kwargs) -> str:
        for llm in self.llms:
            try:
                self.logger.info(f"Querying LLM: {llm.__class__.__name__}")
                response = await llm.analyze(query, **kwargs)
                if response:
                    return response
            except Exception as e:
                log_exception(self.logger, e) 

    @abstractmethod
    async def process(self, query: str, data: Dict[str,Any]) -> AgentResponse:
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
