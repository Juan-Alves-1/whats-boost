import logging
import sys

def init_logging(level=logging.INFO):
    # Get a logger instance with the given name (usually __name__)
    logger = logging.getLogger()

    # Set the minimum log level this logger will handle
    # INFO means it will show INFO, WARNING, ERROR, and CRITICAL messages (but not DEBUG)
    logger.setLevel(level)

    # Prevent adding multiple handlers if this logger is already configured
    if not logger.handlers:
        # Send log messages to the console (stdout)
        handler = logging.StreamHandler(sys.stdout)
        # Example: 2024-04-25 17:00:01 - INFO - services.media - Message sent
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        # Attach the formatter to the handler
        handler.setFormatter(formatter)
        # Attach the handler to the logger
        logger.addHandler(handler)
        
    # Configured logger so other modules can use it
    return logger