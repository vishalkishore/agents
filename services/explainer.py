from typing import List
import logging
from core.schemas import AgentResponse
from core.logging import log_exception
from services.gemini import GeminiService

class ExplainabilityEngine:
    def __init__(self):
        self.logger = logging.getLogger("ExplainabilityEngine")
        self.gemini = GeminiService()

    async def explain(self, results: List[AgentResponse]) -> str:
        try:
            results_str = ""
            for res in results:
                results_str += f"{res.agent_name} ({res.confidence:.2f}): {str(res.result)[:200]}\n"
            
            EXPLAIN_PROMPT = (
                "Synthesize a comprehensive explanation for the user in plain English.\n"
                "Instructions:\n"
                "- Highlight key findings from each analysis perspective.\n"
                "- Note the confidence levels of each result.\n"
                "- Mention any potential limitations.\n\n"
                "Agent Results:\n{results}\n"
            )
            prompt = EXPLAIN_PROMPT.format(results=results_str)
            explanation = await self.gemini.analyze(prompt)
            return explanation
        except Exception as e:
            log_exception(self.logger, e, "Explanation generation failed")
            return "Explanation unavailable due to processing error"
