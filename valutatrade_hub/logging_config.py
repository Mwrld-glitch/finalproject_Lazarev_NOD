import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(
        "logs/actions.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logging()
