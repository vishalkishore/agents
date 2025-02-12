from enum import Enum

# Event types for agent communication
class EventType(Enum):
    QUERY_RECEIVED = "query_received"
    ANALYSIS_REQUESTED = "analysis_requested"
    DATA_READY = "data_ready"
    ANALYSIS_COMPLETED = "analysis_completed"
    ERROR_OCCURRED = "error_occurred"
    COORDINATION_NEEDED = "coordination_needed"
    ANALYSIS_PLAN_CREATED = "analysis_plan_created"
   