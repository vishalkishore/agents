from typing import List
import logging
from core.schemas import AgentResponse
from core.logging import log_exception
from services.llm import GeminiService, ChatGPTService
from prompts.prompts import EXPLAIN_PROMPT

class ExplainabilityEngine:
    def __init__(self):
        self.logger = logging.getLogger("ExplainabilityEngine")
        self.llm = ChatGPTService()

    async def explain(self, results: List[AgentResponse]) -> str:
        try:
            results_str = ""
            for res in results:
                results_str += f"{res.agent_name} ({res.confidence:.2f}): {str(res.result)[:200]}\n"
        
            explanation = await self.llm.analyze(EXPLAIN_PROMPT,results=results_str)
            return explanation
        except Exception as e:
            log_exception(self.logger, e, "Explanation generation failed")
            return "Explanation unavailable due to processing error"
