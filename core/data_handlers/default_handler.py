from abc import ABCMeta, abstractmethod
from typing import List

from pandas import DataFrame

from data_crawler.xueqiu_2_mongo import StockXueqiuData


class CommonDataHandler(metaclass=ABCMeta):
    def __init__(self, cols_name: List[str]):
        """
        :param cols_name: 待获取列名称
        """
        self._cols_name: List[str] = cols_name
        self._stock_xueqiu_data = StockXueqiuData()

    @abstractmethod
    def get_previous_date(self, symbol: str, current_date_str: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_history_trade_date(self, symbol: str, min_date_str: str) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_bar(self, symbol: str, current_date_str: str) -> DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def get_bar_value(self, symbol, current_date_str: str, bar_val_type: BarValTypeEnum) -> float:
        raise NotImplementedError()

    @abstractmethod
    def get_features(self, symbol: str, current_date_str: str) -> DataFrame:
        raise NotImplementedError()

    def get_k_data_previous(self, symbol: str, current_date_str: str, count: int) -> DataFrame:
        raise NotImplementedError()
