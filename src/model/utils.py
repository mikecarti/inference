import json
import sys
import textwrap
from loguru import logger
from random import choice


def wrap(text):
    return textwrap.fill(text, width=100)


def init_logging():
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss}: {message}")
    logger.add("logs.log")


def get_random_hint() -> str:
    with open('data/hints.json') as file:
        data = json.load(file)
        hints = data['data']
        return choice(hints)
