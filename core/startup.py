from shared.config.settings import settings
from shared.logging.logger import setup_logger

logger = setup_logger()


def start():
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Version: {settings.VERSION}")