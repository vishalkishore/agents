from typing import List
import logging
from core.schemas import AgentResponse
from core.logging import log_exception

class ResultAggregator:
    def __init__(self):
        self.logger = logging.getLogger("ResultAggregator")

    async def aggregate(self, agent_results: List[AgentResponse]) -> List[AgentResponse]:
        try:
            valid_results = [
                result for result in agent_results 
                if result and not result.error
            ]

            if not valid_results:
                self.logger.warning("No valid results from any agents")
                return agent_results

            sorted_results = sorted(
                valid_results,
                key=lambda x: x.confidence,
                reverse=True
            )

            self.logger.info(
                f"Aggregated {len(sorted_results)} valid results from "
                f"{len(agent_results)} total responses"
            )
            
            return sorted_results

        except Exception as e:
            log_exception(self.logger, e, "Result aggregation failed")
            return agent_results
