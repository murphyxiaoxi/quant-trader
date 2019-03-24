from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List

from pandas import DataFrame

from backend.commons.enums.bar_val_type_enums import BarValTypeEnum
from backend.commons.enums.symbol_type import SymbolTypeEnum


class CommonDataHandler(metaclass=ABCMeta):
    def __init__(self, symbol_type: SymbolTypeEnum, data_frame: DataFrame, cols_name: List[str]):
        """

        :param symbol_type
        :param data_frame: pandas dataFrame
        :param cols_name: 待获取列名称
        """
        self.symbol_type = symbol_type
        self.data_frame = data_frame
        self.cols_name: List[str] = cols_name

    @abstractmethod
    def get_previous_date(self, current_date: datetime):
        raise NotImplementedError()

    @abstractmethod
    def get_history_trade_date(self, symbol_code, min_date_time: datetime) -> List[datetime]:
        raise NotImplementedError()

    @abstractmethod
    def get_bar(self, symbol_code: str, date_time: datetime) -> DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def get_bar_value(self, symbol_code, date_time: datetime, bar_val_type: BarValTypeEnum) -> float:
        raise NotImplementedError()

    @abstractmethod
    def get_features(self, symbol_code: str, date_time: datetime) -> DataFrame:
        raise NotImplementedError()
