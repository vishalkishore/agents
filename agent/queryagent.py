from .base import BaseAgent
from typing import Dict, List, Any, Optional, Tuple
from etypes.event_types import EventType
from schema.schema import Event
from llm.model import gemini as model
import json

class QueryAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing and breaking down queries"""
    
    def __init__(self, config: Dict[str, str]):
        super().__init__("query_analyzer", config)
        self.model = model
    
    
    def handle_event(self, event: Event):
        if event.type == EventType.QUERY_RECEIVED:
            self.logger.info(f"Analyzing query: {event.data['query']}")
            try:
                query_analysis = self._analyze_query(event.data['query'])
                self.logger.info(f"Query analysis: {query_analysis}")
                query_analysis['query'] = event.data['query']
                self.logger.info(f"Query analysis: {query_analysis['symbol']}")
                self.publish_event(Event(
                    EventType.COORDINATION_NEEDED,
                    query_analysis,
                    self.name,
                    "coordinator"
                ))
            except Exception as e:
                self.logger.error(f"Query analysis failed: {e}")
                self.publish_event(Event(
                    EventType.ERROR_OCCURRED,
                    {"error": str(e), "stage": "query_analysis"},
                    self.name
                ))
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query using Gemini"""
        prompt = f"""
        Analyze this trading query in detail: "{query}"
        Return a complete analysis plan including:
        1. Required data types
        2. Analysis steps
        3. Dependencies between analyses
        4. Priority order
        Format as JSON with keys: data_requirements, analysis_steps.

        ### **Output Format (JSON)**
    
    {{  "symbol": "symbol of that stocks",
        "data_requirements": [ 
            "description of required data type 1",
            "description of required data type 2"
        ],
        "analysis_steps": [
            {{
                "step": "Step description",
                "depends_on": ["previous_step_name"]  // If applicable
            }},
            {{
                "step": "Next step description",
                "depends_on": []
            }}
        ]
    }}
    
        
        """
        response = self.model.generate_content(prompt)
        try:
            self.logger.info(f"Query analysis response: {response.text}")
            return json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode response")
            return {"error": "Failed to decode response"}
