import logging
import traceback
from functools import wraps

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def log_exception(logger, error, additional_msg=""):
    logger.error(f"{error}\n{additional_msg}\n{traceback.format_exc()}")

def log_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__name__)
        try:
            logger.info(f"Executing {func.__name__}")
            result = await func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}")
            return result
        except Exception as e:
            log_exception(logger, e, f"Error in {func.__name__}")
            raise
    return wrapper