from fastapi import APIRouter, HTTPException
from core.schemas import UserQuery, ProcessedResponse
from services.agent_selector import AgentSelector
from services.aggregator import ResultAggregator
from services.explainer import ExplainabilityEngine
from core.logging import log_execution, log_exception
import logging
import asyncio
from typing import List, Dict, Any
from services.llm import ChatGPTService, GeminiService
router = APIRouter()
logger = logging.getLogger("analysis_router")

@router.post("/query", response_model=ProcessedResponse)
@log_execution
async def process_query(query: UserQuery):
    logger.info(f"Received request body: {query.dict()}")  
    selector = AgentSelector()
    aggregator = ResultAggregator()
    explainer = ExplainabilityEngine()
    llm = ChatGPTService()
    try:

        financial_check = await llm.is_financial_query(query.text)

        if not financial_check.get("is_appropriate", True):
            FINANCIAL_REJECTION_TEMPLATES = [
    "I appreciate your question, but I'm not able to provide specific financial advice. {reason} Instead, I'd be happy to share general financial education or point you toward reliable resources where you can learn more.",
    "Thank you for your query. {reason} While I can't provide personalized financial guidance, I can explain general financial concepts or direct you to professional resources that might help.",
    "I understand you're looking for financial insights. {reason} For your financial wellbeing, this type of advice is best obtained from qualified financial professionals who understand your complete situation.",
    "I notice you're asking about financial matters. {reason} Would you like me to provide some general information about this topic instead, or perhaps explain what factors you might want to consider?"
]
            rejection_message = generate_kind_rejection(
                financial_check.get("reason", ""),
                FINANCIAL_REJECTION_TEMPLATES
            )
            
            logger.info(f"Financial query rejected: {financial_check.get('reason')}")
            
            # Return early with the rejection message
            return ProcessedResponse(
                results=[],
                explanation=rejection_message,
                session_id=query.session_id
            )

        agents, response = await selector.select_agents(query.text)
        if not agents:
            raise HTTPException(status_code=400, detail="No suitable agents found for query")
        logger.info(f"Selected agents: {[agent.__class__.__name__ for agent in agents]}")
        # Process query with selected agents
        agent_tasks = [
            asyncio.create_task(agent.process(response["paraphrased_queries"].get(agent.__class__.__name__), response))
            for agent in agents
        ]
        results = await asyncio.gather(*agent_tasks)

        processed_results = await aggregator.aggregate(results)

        # Generate explanation
        explanation = await explainer.explain(processed_results,user_query=query.text)

        return ProcessedResponse(
            results=results,
            explanation=explanation,
            session_id=query.session_id
        )
    except Exception as e:
        log_exception(logger, e)
        raise HTTPException(status_code=500, detail=str(e))
    

def generate_kind_rejection(reason: str, templates: List[str]) -> str:
    import random
    if not templates:
        # Fallback template if none are provided
        return f"I'm sorry, but I cannot provide financial advice. {reason} Please consult with a qualified financial professional."
    
    template = random.choice(templates)
    return template.format(reason=reason)


