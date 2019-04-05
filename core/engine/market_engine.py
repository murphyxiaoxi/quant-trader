import queue
import time
from typing import List

import pandas

from core.common import trade_date_util
from core.common.event import EventTypeEnum, MarketEvent
from core.engine.clock_engine import BackTestClockEngine, OnlineClockEngine
from dao.stock_data import StockXueqiuData


class MarketEngine:
    def __init__(self, symbols: List[str], back_test: bool = True, start_date: str = None, end_date: str = None):
        self.__clock_engine = BackTestClockEngine(start_date, end_date) if back_test else OnlineClockEngine()
        self.__queue = queue.Queue()
        self.__active = True
        self.__stock_data_api = StockXueqiuData()
        self.__symbols = symbols
        self.init()

    def init(self):
        if self.__symbols is None or len(self.__symbols) == 0:
            raise Exception("股票列表不为空")

        self.__clock_engine.start()

    def run(self):
        while self.__active:
            if self.__clock_engine.empty():
                time.sleep(0.1)
            else:
                event = self.__clock_engine.get()
                if event <= 0:
                    break
                if event.event_type != EventTypeEnum.CLOCK:
                    continue

                # 日期 20180101
                date = event.data
                previous_date = trade_date_util.previous_trade_date(date)

                market_event = MarketEvent(True, self.__get_stock_data(previous_date))
                self.__queue.put(market_event)

    def empty(self):
        return self.__queue.empty()

    def get(self, block=False):
        return self.__queue.get(block=block)

    def __get_stock_data(self, date: str):
        dfs = []
        for symbol in self.__symbols:
            dfs.append(self.__stock_data_api.get_his_k_data(symbol, date, date))
        return pandas.concat(dfs)
