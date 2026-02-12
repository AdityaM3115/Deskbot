import logging
import os
from datetime import datetime

# Create logs directory if not exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Daily log file
log_filename = datetime.now().strftime("deskbot_%Y-%m-%d.log")
log_path = os.path.join(LOG_DIR, log_filename)

# Configure logging (FILE ONLY)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_info(message):
    logging.info(message)


def log_warning(message):
    logging.warning(message)


def log_error(message):
    logging.error(message)
