import logging
import sys


def setup_logging():
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(name)s - %(message)s')

    # Create a StreamHandler to handle logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Create a logger and add the StreamHandler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the desired logging level
    logger.addHandler(stream_handler)
    # print("EOF setup_logging")
