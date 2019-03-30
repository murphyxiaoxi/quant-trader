from typing import List

from pandas import DataFrame

from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums.bar_val_type_enums import BarValTypeEnum
from backend.commons.enums.symbol_type import SymbolTypeEnum


class OnlineDataHandler(CommonDataHandler):
    def __int__(self, symbol_type: SymbolTypeEnum, cols_name: List[str]):
        super(OnlineDataHandler, self).__int__(symbol_type, cols_name)

    def get_previous_date(self, symbol: str, current_date_str: str) -> str:
        pass

    def get_history_trade_date(self, symbol, min_date_str: str) -> List[str]:
        pass

    def get_bar(self, symbol: str, current_date_str: str) -> DataFrame:
        pass

    def get_bar_value(self, symbol, current_date_str: str, bar_val_type: BarValTypeEnum) -> float:
        pass

    def get_features(self, symbol: str, current_date_str: str) -> DataFrame:
        pass
