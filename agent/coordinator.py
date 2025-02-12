
from etypes.event_types import EventType
from schema.schema import Event
from typing import Dict, List, Any, Optional, Tuple
import traceback
from queue import Queue
import threading
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .base import BaseAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """Coordinates communication and tasks between agents"""
    
    def __init__(self):
        self.name = "coordinator"
        self.event_queue = Queue()
        self.agents = {}
        self.results_cache = {}
        self.final_result = None
        self.lock = threading.Lock()
        self.completion_event = threading.Event()
        self.logger = logging.getLogger("AgentCoordinator")
    
    def register_agent(self, agent_name: str, agent: 'BaseAgent'):
        """Register an agent with the coordinator"""
        self.agents[agent_name] = agent
        agent.set_coordinator(self)
    
    def publish_event(self, event: Event):
        """Publish an event to the event queue"""
        self.event_queue.put(event)
    
    def process_events(self):
        """Process events from the queue"""
        self.logger.info("Starting event processing loop")
        while True:
            event = self.event_queue.get()
            self._handle_event(event)
            self.event_queue.task_done()
    
    def _handle_event(self, event: Event):
        """Handle different types of events"""
        try:
            self.logger.info(f"Processing event: {event.type} from {event.source}")
            if event.target and event.target in self.agents:
                self.logger.info(f"Forwarding event to {event.target}")
                self.agents[event.target].handle_event(event)
            elif event.type == EventType.COORDINATION_NEEDED:
                self._coordinate_analysis(event)
            elif event.type == EventType.ERROR_OCCURRED:
                self._handle_error(event)
            elif event.type == EventType.DATA_READY and event.source == 'data_collector':
                # Forward data to analysis agents
                analysis_agents = [
                    'technical_analyzer',
                    'fundamental_analyzer',
                    'sentiment_analyzer',
                    'risk_analyzer'
                ]
                for agent_name in analysis_agents:
                    self.publish_event(Event(
                        EventType.DATA_READY,
                        event.data,
                        self.name,
                        agent_name
                    ))
                # no use as of now 
                self.publish_event(Event(
                    EventType.DATA_READY,
                    event.data,
                    self.name,
                    'results_synthesizer'
                ))
            
            elif event.type == EventType.ANALYSIS_COMPLETED:
                if event.source == "results_synthesizer":
                    with self.lock:
                        self.final_result = event.data
                        
                        self.completion_event.set()
                else:
                    # Forward analysis results to synthesizer
                    self.publish_event(Event(
                        EventType.ANALYSIS_COMPLETED,
                        event.data,
                        event.source,
                        'results_synthesizer'
                    ))
           
        except Exception as e:
            self.logger.error(f"Error handling event: {e}")
            self._handle_error(Event(
                EventType.ERROR_OCCURRED,
                {"error": str(e), "original_event": event},
                "coordinator"
            ))
    
    def _coordinate_analysis(self, event: Event):
        """Coordinate analysis workflow with proper plan tracking"""
        self.logger.info("Coordinating analysis workflow")
        
        # Extract critical information from query analysis
        # self.logger.info(f"Query analysis: {event.data}")
        symbol = event.data['symbol']
        query = event.data['query']
        self.logger.info(f"2) Query:")
        analysis_plan = self._create_analysis_plan(event.data)
        # self.logger.info(f"3) Analysis plan: {analysis_plan}")
        
        # Identify analysis agents involved
        analysis_agents = [step['agent'] for step in analysis_plan if step['agent'] != 'data_collector']
        
        
        # Notify synthesizer about expected agents
        self.publish_event(Event(
            EventType.ANALYSIS_PLAN_CREATED,
            {
                'symbol': symbol,
                'query': query,
                'expected_agents': analysis_agents
            },
            self.name,
            'results_synthesizer'
        ))
        self.logger.info(f"Expected agents: {analysis_agents}")
        for step in analysis_plan:
            agent_name = step['agent']
            if agent_name in self.agents:
                self.publish_event(Event(
                    EventType.ANALYSIS_REQUESTED,
                    {'symbol': symbol, **step['parameters']},
                    "coordinator",
                    agent_name
                ))
                self.logger.info(f"5) Done analysis from {agent_name}")

    def _create_analysis_plan(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a detailed analysis plan based on query requirements"""
        # This would normally come from the query analysis, simplified for example
        return [
            {'agent': 'data_collector', 'parameters': data},
            {'agent': 'technical_analyzer', 'parameters': {}},
            {'agent': 'fundamental_analyzer', 'parameters': {}},
            {'agent': 'sentiment_analyzer', 'parameters': {}},
            {'agent': 'risk_analyzer', 'parameters': {}},
        ]

    def _handle_error(self, event: Event):
        """Handle error events"""
        error_data = event.data
        self.logger.error(f"Error occurred: {error_data['error']}")
        self.logger.error(f"Original event: {error_data.get('original_event')}")
        self.logger.error("Full traceback:\n" + traceback.format_exc())
