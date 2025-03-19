from typing import List
import logging
from core.schemas import AgentResponse
from core.logging import log_exception
from services.llm import GeminiService, ChatGPTService
from prompts.prompts import EXPLAIN_PROMPT, EXPLAIN_SYSTEM_PROMPT
import re
            
class ExplainabilityEngine:
    def __init__(self):
        self.logger = logging.getLogger("ExplainabilityEngine")
        self.llm = ChatGPTService()

    async def explain(self, results: List[AgentResponse]) -> str:
        try:
            results_str = ""
            for res in results:
                results_str += f"{res.agent_name} ({res.confidence:.2f}): {str(res.result)[:200]}\n"
        
            explanation = await self.llm.analyze(EXPLAIN_PROMPT,system_prompt=EXPLAIN_SYSTEM_PROMPT,results=results_str) 
            explanation = re.sub(
            r'<card>(.*?)</card>', 
            r'<div class="card">\1</div>', 
            explanation, 
            flags=re.DOTALL
            )
            return explanation
        except Exception as e:
            log_exception(self.logger, e, "Explanation generation failed")
            return "Explanation unavailable due to processing error"
