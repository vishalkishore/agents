import logging
import traceback
from functools import wraps

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [AGENT: %(name)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S.%f'
    )

def get_agent_logger(agent_name: str) -> logging.Logger:
    """Get a logger specifically for an agent"""
    logger = logging.getLogger(agent_name)
    return logger

def log_exception(logger, error, additional_msg=""):
    logger.error(f"{error}\n{additional_msg}\n{traceback.format_exc()}")

def log_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        agent_name = args[0].agent_name if args and hasattr(args[0], 'agent_name') else func.__name__
        logger = logging.getLogger(agent_name)
        try:
            logger.info(f"Executing {func.__name__}")
            result = await func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}")
            return result
        except Exception as e:
            log_exception(logger, e, f"Error in {func.__name__}")
            raise
    return wrapper