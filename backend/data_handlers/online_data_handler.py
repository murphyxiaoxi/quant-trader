from datetime import datetime
from typing import List

from pandas import DataFrame

from backend.data_handlers.abstract_handler import CommonDataHandler


class OnlineDataHandler(CommonDataHandler):
    def __int__(self, data_frame: DataFrame, cols_name: List[str], symbol_list: List[str]):
        super().__init__(data_frame, cols_name, symbol_list)

    def get_latest_bar(self, date: datetime):
        pass


