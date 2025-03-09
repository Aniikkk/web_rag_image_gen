import logging
import os

LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs.txt"))

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler() 
    ]
)

def get_logger(name):
    """Returns a logger instance for a given module."""
    return logging.getLogger(name)
