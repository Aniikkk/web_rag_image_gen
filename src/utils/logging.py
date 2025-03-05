import logging
import os

# Get the absolute path to the root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "logs.txt")  # Log file in project root

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Save logs to file
        logging.StreamHandler()  # Print logs to console
    ]
)

def get_logger(name):
    """Returns a logger instance for a given module."""
    return logging.getLogger(name)
