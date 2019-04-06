import queue
import threading
import time
from typing import List

import pandas

from core.common import trade_date_util
from core.common.event import EventTypeEnum, MarketEvent
from core.engine.clock_engine import BackTestClockEngine, OnlineClockEngine
from dao.stock_data import StockXueqiuData


class MarketEngine:
    def __init__(self, symbols: List[str], market_data_func, back_test: bool = True,
                 start_date: str = None, end_date: str = None,
                 clock_event_queue=None,
                 market_event_queue=None):
        """

        :param symbols:
        :param market_data_func 市场数据处理函数 传参 current_date
        :param back_test:
        :param start_date:
        :param end_date:
        :param market_event_queue:
        """
        self.__clock_engine = BackTestClockEngine(start_date, end_date, clock_event_queue) \
            if back_test else OnlineClockEngine(clock_event_queue)

        self.__queue = market_event_queue or queue.Queue()
        self.__stock_data_api = StockXueqiuData()
        self.__symbols = symbols
        self.__market_data_func = market_data_func
        self.init()
        self.__thread = threading.Thread(target=self.__run, name="MarketEngine.__thread")
        self.__active = False

    def init(self):
        if self.__symbols is None or len(self.__symbols) == 0:
            raise Exception("股票列表不为空")
        if self.__market_data_func is None:
            raise Exception("市场数据处理函数market_data_func不可为空")

    def empty(self):
        return self.__queue.empty()

    def get(self, block=False, timeout=None):
        return self.__queue.get(block=block, timeout=timeout)

    def start(self):
        self.__active = True
        self.__thread.start()
        self.__clock_engine.start()

    def stop(self):
        self.__clock_engine.stop()
        self.__active = False
        self.__thread.join()

    def __run(self):
        while self.__active:
            if self.__clock_engine.empty():
                time.sleep(0.1)
            else:
                event = self.__clock_engine.get()
                if event.event_type != EventTypeEnum.CLOCK:
                    continue

                # 强制退出
                if event == 0:
                    break

                # 日期 20180101
                current_date = event.date

                market_event = MarketEvent(current_date, self.__market_data_func(current_date))
                self.__queue.put(market_event)

        print("MarketEngine stopped===")

    def __default_market_data_func(self, date: str):
        previous_date = trade_date_util.previous_trade_date(date)
        dfs = []
        for symbol in self.__symbols:
            dfs.append(self.__stock_data_api.get_his_k_data(symbol, previous_date, date))

        return pandas.concat(dfs)
