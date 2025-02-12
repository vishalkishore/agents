from etypes.event_types import EventType
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from schema.schema import Event
import logging
from .coordinator import AgentCoordinator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, config: Dict[str, str]):
        self.name = name
        self.config = config
        self.coordinator = None
        self.logger = logging.getLogger(f"Agent.{name}")
    
    def set_coordinator(self, coordinator: AgentCoordinator):
        """Set the coordinator for this agent"""
        self.coordinator = coordinator
    
    @abstractmethod
    def handle_event(self, event: Event):
        """Handle incoming events"""
        pass
    
    def publish_event(self, event: Event):
        """Publish an event through the coordinator"""
        if self.coordinator:
            self.coordinator.publish_event(event)
