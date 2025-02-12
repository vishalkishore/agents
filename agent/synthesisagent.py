from .base import BaseAgent
from typing import Dict, List, Any, Optional, Tuple
from etypes.event_types import EventType
from schema.schema import Event
from llm.model import gemini as model
import threading
from datetime import datetime
import json


class ResultsSynthesisAgent(BaseAgent):
    """Enhanced agent for synthesizing results from multiple analyses"""
    
    def __init__(self, config: Dict[str, str]):
        super().__init__("results_synthesizer", config)
        self.model = model
        
        # Track expected and completed analyses
        self.pending_requests = {}  # {symbol: {'query': str, 'expected': set, 'results': dict}}
        self.lock = threading.Lock()

    def handle_event(self, event: Event):
        try:
            if event.type == EventType.ANALYSIS_PLAN_CREATED:
                self.logger.info(f"<ResultsSynthesisAgent> Received analysis plan: {event.data}")
                self._handle_analysis_plan(event)
            elif event.type == EventType.ANALYSIS_COMPLETED:
                self.logger.info(f"<ResultsSynthesisAgent> Received analysis completed result from {event.source}")
                self._handle_analysis_result(event)
        except Exception as e:
            self.logger.error(f"Error in results synthesizer: {e}")
            self.publish_event(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "stage": "results_synthesis"},
                self.name
            ))

    def _handle_analysis_plan(self, event: Event):
        """Handle new analysis plan from coordinator"""
        self.logger.info(f"in _handle_analysis_plan")
        with self.lock:
            
            symbol = 'AAPL' #event.data['symbol']
            self.logger.info(f"Received analysis plan for {event.data}")
            self.pending_requests[symbol] = {
                'query': event.data['query'],
                'expected': set(event.data['expected_agents']),
                'results': {},
                'received': set(),
                'timestamp': datetime.now()
            }
            self.logger.info(f"New analysis plan received for {symbol}. Waiting for: {event.data['expected_agents']}")

    def _handle_analysis_result(self, event: Event):
        """Handle incoming analysis results"""
        with self.lock:
            symbol = event.data.get('symbol')
            if not symbol or symbol not in self.pending_requests:
                self.logger.warning(f"Received unexpected analysis result for {symbol or 'unknown'}")
                return

            agent_name = event.source
            request = self.pending_requests[symbol]
            # if agent_name in request['received']:
            #     return
            if agent_name not in request['expected']:
                self.logger.warning(f"Unexpected result from {agent_name} for {symbol}")
                return

            request['received'].add(agent_name)
            request['results'][agent_name] = event.data
            self.logger.info( f"Received {agent_name} results for {symbol} ({len(request['results'])}/{len(request['expected'])})" )

            if len(request['results']) == len(request['expected']):
                self.logger.info(f"All results received for {symbol}. Synthesizing...")
                synthesis = self._synthesize_results(
                    request['results'],
                    request['query'],
                    symbol
                )
                self.logger.info(f"!!!<ResultsSynthesisAgent> Synthesis completed for {synthesis}")
                # self._cleanup_request(symbol)
                self.logger.info(f"!!!<ResultsSynthesisAgent> Cleaned up request for {symbol}")
                self.publish_event(Event(
                    EventType.ANALYSIS_COMPLETED,
                    synthesis,
                    self.name,
                    "coordinator"
                ))

    def _synthesize_results(self, results: Dict[str, Any], query: str, symbol: str) -> Dict[str, Any]:
        """Synthesize results using Gemini with enhanced contextual understanding"""
        synthesis = {
            "summary": "Comprehensive Analysis Summary",
            "symbol": symbol,
            "query": query,
            "details": {},
            "recommendations": []
        }

        self.logger.info(f"Synthesizing results for {symbol} based on query: {query}")
        
        if self.model:
            try:
                prompt = f"""
                Synthesize this financial analysis for {symbol} based on the query: "{query}".
                Consider the following analyses:
                
                Technical Analysis: {results.get('technical_analyzer', {})}
                Fundamental Analysis: {results.get('fundamental_analyzer', {})}
                Sentiment Analysis: {results.get('sentiment_analyzer', {})}
                Risk Analysis: {results.get('risk_analyzer', {})}

                Provide:
                1. A comprehensive summary connecting all analyses
                2. Key insights and contradictions between different analyses
                3. Specific, actionable recommendations based on the combined data
                4. Confidence level in the recommendations (high/medium/low)
                5. Potential risks and mitigating strategies

                Format the response in JSON with these keys:
                - summary
                - key_insights
                - recommendations
                - confidence_level
                - risks
                - next_steps
                """
                
                response = self.model.generate_content(prompt)
                if response.text:
                    ai_synthesis = json.loads(response.text)
                    synthesis.update(ai_synthesis)
                    synthesis["details"] = results  # Include raw results for reference
                    self.logger.info(f"Synthesis completed: {synthesis}")
            except Exception as e:
                self.logger.error(f"Synthesis error: {e}")
                synthesis["error"] = str(e)

        return synthesis

    def _cleanup_request(self, symbol: str):
        """Clean up completed requests"""
        with self.lock:
            if symbol in self.pending_requests:
                del self.pending_requests[symbol]
                self.logger.info(f"Cleaned up completed analysis for {symbol}")

