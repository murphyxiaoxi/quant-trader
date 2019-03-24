from typing import List

from pandas import DataFrame

from backend.commons.data_handlers.abstract_handler import CommonDataHandler


class BackTestDataHandler(CommonDataHandler):
    def __init__(self, data_frame: DataFrame, cols_name: List[str]):
        super().__init__(data_frame, cols_name)

    def get_latest_bar(self, symbol_code: str, date: str) -> DataFrame:
        """
        :param symbol_code:
        :param date: format -> 2018-09-20
        :return:
        """
        raise NotImplementedError()
