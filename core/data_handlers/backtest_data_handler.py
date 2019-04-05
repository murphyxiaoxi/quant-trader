from typing import List, Optional
from datetime import datetime as date_time_type
from pandas import DataFrame

from core.data_handlers.abstract_handler import CommonDataHandler
from core.enums.bar_val_type_enums import BarValTypeEnum
from core.enums.symbol_type import SymbolTypeEnum
from data_crawler.xueqiu_2_mongo import StockXueqiuData


class BackTestDataHandler(CommonDataHandler):
    def __init__(self, symbol_type: SymbolTypeEnum, cols_name: List[str]):
        super(BackTestDataHandler, self).__init__(symbol_type, cols_name)
        self._stock_xueqiu_data = StockXueqiuData()

    def get_previous_date(self, symbol: str, current_date_str: str) -> Optional[str]:
        data = self._stock_xueqiu_data.get_his_k_data(symbol, '2000-01-01', current_date_str)
        dates = data.sort_index(ascending=False).index
        for d in dates:
            if d < current_date_str:
                return d
        return None

    def get_history_trade_date(self, symbol, min_date_str: str) -> List[str]:
        end_date = date_time_type.now().strftime('%Y-%m-%d')
        data = self._stock_xueqiu_data.get_his_k_data(symbol, min_date_str, end_date)
        return [d for d in data.index]

    def get_bar(self, symbol: str, current_date_str: str) -> DataFrame:
        return self._stock_xueqiu_data.get_his_k_data(symbol, current_date_str, current_date_str)

    def get_bar_value(self, symbol, current_date_str: str, bar_val_type: BarValTypeEnum) -> float:
        tmp = self._stock_xueqiu_data.get_his_k_data(symbol, current_date_str, current_date_str)
        return tmp['close'][0]

    def get_features(self, symbol: str, current_date_str: str) -> DataFrame:
        return self._stock_xueqiu_data.get_his_k_data(symbol, current_date_str, current_date_str)

    def get_k_data_previous(self, symbol: str, current_date_str: str, count: int) -> DataFrame:
        result = self._stock_xueqiu_data.get_his_k_data(symbol, None, current_date_str)
        result = result.sort_index(ascending=False)
        return result.iloc[1:count + 1]
