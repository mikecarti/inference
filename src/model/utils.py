import sys
import textwrap
from loguru import logger


def wrap(text):
    return textwrap.fill(text, width=100)


def init_logging():
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss}: {message}")
    logger.add("logs.log")
