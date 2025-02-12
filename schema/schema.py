from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from etypes.event_types import EventType

@dataclass
class Event:
    """Event for inter-agent communication"""
    type: EventType
    data: Dict[str, Any]
    source: str
    target: Optional[str] = None
    priority: int = 1
    timestamp: datetime = datetime.now()