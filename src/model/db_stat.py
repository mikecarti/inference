import datetime
import sqlite3
from enum import Enum
from typing import Any, List
from loguru import logger

from src.model.message import AbstractMessage


class StatisticsDB:
    """
    To load db file from a container to host run:
    docker cp helpdesk_container:/app/helpdesk/stats/useful_stats.db helpdesk/stats/useful_stats.db
    """
    DB_FILE_PATH: str = 'stats/useful_stats.db'
    TABLE_NAME: str = 'Requests'

    def __init__(self):
        self.initialize_db_if_not_exists()
        self.test_db()

    def connection(self) -> sqlite3.Connection:
        """
        Receive DB connection object
        :return:
        """
        return sqlite3.connect(self.DB_FILE_PATH)

    def initialize_db_if_not_exists(self):
        """
        :return:
        """
        with self.connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            id INTEGER PRIMARY KEY,
            datetime date NOT NULL,
            ip_port TEXT NOT NULL,
            input_tokens FLOAT NOT NULL,
            output_tokens FLOAT NOT NULL,
            input_text TEXT NOT NULL,
            output_text TEXT NOT NULL,
            
            input_expense_usd FLOAT,
            output_expense_usd FLOAT, 
            total_expense_usd FLOAT
            )
            ''')

    def insert_row(self, data: dict):
        """
        Create new row and insert all fields
        :param data:
        :return:
        """

        # TODO: find a way to solve it
        with self.connection() as conn:
            cursor = conn.cursor()
            values = list(data.values())
            column_names = ", ".join([col_name.value for col_name in data.keys()])
            placeholders = ", ".join(["?"] * len(values))
            # logger.debug(f"StatData: {data}")
            # logger.debug(f"column_names, values, placeholders: {column_names}, {values}, {placeholders}")
            sql_query = f"INSERT INTO {self.TABLE_NAME} ({column_names}) VALUES ({placeholders})"
            logger.debug(f"Sql query: {sql_query}")

            cursor.execute(sql_query, values)

    def test_db(self):
        """
        Test entry
        :return:
        """
        data = {
            StatType.DATETIME: '2023-10-20',
            StatType.IP_PORT: '127.0.0.1',
            StatType.INPUT_TEXT: 'TEST',
            StatType.OUTPUT_TEXT: 'TEST',
            StatType.INPUT_TOKENS: 0.0,
            StatType.OUTPUT_TOKENS: 0.0,
            StatType.INPUT_EXPENSE: 0.0,
            StatType.OUTPUT_EXPENSE: 0.0,
            StatType.TOTAL_EXPENSE: 0.0
        }

        self.insert_row(data)


class StatType(Enum):
    """
    Statistic Types. All DataBase column should be contained here in correct names as in db
    """
    DATETIME = "datetime"
    IP_PORT = "ip_port"
    INPUT_TEXT = "input_text"
    OUTPUT_TEXT = "output_text"
    INPUT_TOKENS = "input_tokens"
    OUTPUT_TOKENS = "output_tokens"
    INPUT_EXPENSE = "input_expense_usd"
    OUTPUT_EXPENSE = "output_expense_usd"
    TOTAL_EXPENSE = "total_expense_usd"

    @classmethod
    def types(cls) -> List:
        """
        Returns a list of all stat. types
        :return:
        """
        types = [value for key, value in cls.__dict__.items() if not key.startswith("__")]
        assert len(types) != 0, f"Len of types: {len(types)}"
        assert all(types), f"Types contains None"

        return types


class StatisticsWatcher:
    GPT_3_5_CHARACTER_TO_TOKEN_RATIO_RU = 0.427
    GPT_3_5_INPUT_TOKEN_TO_USD_RATIO_16K = 1e-6 * 3
    GPT_3_5_OUTPUT_TOKEN_TO_USD_RATIO_16K = 1e-6 * 3

    def __init__(self, stats_db: StatisticsDB):
        self.stats_db = stats_db
        self.stats_row = {}
        self.stat_types = StatType.types()

    def collect_info(self, user_message: AbstractMessage, ai_answer: str):
        """
        Collect useful statistics from request, and store it into db.

        :param user_message:
        :param ai_answer:
        :return:
        """
        date_time = user_message.date
        ip_port = user_message.from_user.id
        input_text = user_message.text
        output_text = ai_answer
        input_tokens = self._text_to_tokens(text=input_text)
        output_tokens = self._text_to_tokens(text=output_text)
        input_expense = self._input_tokens_to_usd(num_of_tokens=input_tokens)
        output_expense = self._output_tokens_to_usd(num_of_tokens=output_tokens)
        total_expense = input_expense + output_expense

        assert isinstance(date_time, datetime.datetime)

        self.add(date_time, stat_type=StatType.DATETIME)
        self.add(ip_port, stat_type=StatType.IP_PORT)
        self.add(input_text, stat_type=StatType.INPUT_TEXT)
        self.add(output_text, stat_type=StatType.OUTPUT_TEXT)
        self.add(input_tokens, stat_type=StatType.INPUT_TOKENS)
        self.add(output_tokens, stat_type=StatType.OUTPUT_TOKENS)
        self.add(input_expense, stat_type=StatType.INPUT_EXPENSE)
        self.add(output_expense, stat_type=StatType.OUTPUT_EXPENSE)
        self.add(total_expense, stat_type=StatType.TOTAL_EXPENSE)

        self._send_stats()

    def add(self, data: Any, stat_type: StatType) -> None:
        """
        Add data to a buffer of watcher
        :param data:
        :param stat_type:
        :return:
        """
        self(data, stat_type=stat_type)

    def __call__(self, data: Any, stat_type: StatType) -> None:
        """
        Add data to buffer of a watcher
        :param data:
        :param stat_type:
        :return:
        """
        assert stat_type in self.stat_types, f"Unrecognized stat_type: {stat_type}"
        assert self.stats_row.get(
            stat_type) is None, f"Data {data} of stat_type {stat_type} cant be inserted in stats_row. Previous was not deleted, " \
                                f"or you are trying to save one data_type twice per a request, self.stats_row.get(" \
                                f"stat_type) expected None, got: {self.stats_row.get(stat_type)}"

        self.stats_row[stat_type] = data

    def _send_stats(self) -> None:
        """
        Send collected buffer on a single request to db.
        :return:
        """
        logger.debug(f"Data saved to statistics database.")
        self.stats_db.insert_row(self.stats_row)
        self.stats_row = {}

    def _text_to_tokens(self, text: str) -> int:
        """
        Transforms number of characters into approximate number of tokens
        :param text:
        :return estimate num. of tokens:
        """
        return int(len(text) * self.GPT_3_5_CHARACTER_TO_TOKEN_RATIO_RU)

    def _input_tokens_to_usd(self, num_of_tokens: int) -> float:
        """
        Transforms number of tokens on input to LLM declared in chain.py into USD price according to pricing for 20.10.2023
        :param num_of_tokens:
        :return USD price:
        """
        return num_of_tokens * self.GPT_3_5_INPUT_TOKEN_TO_USD_RATIO_16K

    def _output_tokens_to_usd(self, num_of_tokens: int) -> float:
        """
        Transforms number of tokens on output from LLM declared in chain.py into USD price according to pricing for 20.10.2023
        :param num_of_tokens:
        :return USD price:
        """
        return num_of_tokens * self.GPT_3_5_OUTPUT_TOKEN_TO_USD_RATIO_16K
