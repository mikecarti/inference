import json
import sys
import textwrap
from typing import List, Callable

from loguru import logger
from random import choice


def wrap(text):
    return textwrap.fill(text, width=100)


def init_logging():
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss}: {message}")
    logger.add("logs.log")


def get_random_hint() -> str:
    with open('data/hints.json', encoding="utf-8") as file:
        data = json.load(file)
        hints = data['data']
        return choice(hints)


def return_with_name(func: Callable) -> (str, List[str]):
    """
    Not only the function result(s) is (are) returned, but also pythonic function's name.
    :param func:
    :return: function name and list of output
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if type(result) != list and type(result) != tuple:
            result = [result]
        result = [str(out) for out in result]
        return func.__name__, result

    wrapper.__name__ = func.__name__
    return wrapper
