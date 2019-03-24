from datetime import datetime
from typing import List

from pandas import DataFrame

from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums.bar_val_type_enums import BarValTypeEnum


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

    def get_history_trade_date(self, symbol_code, min_date_time: datetime) -> List[datetime]:
        pass

    def get_bar(self, symbol_code: str, date_time: datetime) -> DataFrame:
        pass

    def get_bar_value(self, symbol_code, date_time: datetime, bar_val_type: BarValTypeEnum) -> float:
        pass

    def get_features(self, symbol_code: str, date_time: datetime) -> DataFrame:
        pass
