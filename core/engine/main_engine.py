import queue
import threading
import time
from collections import defaultdict
from typing import List

from core.common.default_logger import logger

from core.common.event import Event, EventTypeEnum
from core.common.strategyTemplate import StrategyTemplate
from core.engine.market_engine import MarketEngine


class MainEngine:
    def __init__(self, symbols: List[str], strategy: StrategyTemplate, back_test=True, start_date=None, end_date=None):
        self.__symbols = symbols
        self.__back_test = back_test
        self.__start_date = start_date
        self.__end_date = end_date
        self.__market_engine = MarketEngine(symbols, back_test, start_date, end_date)
        self.__strategy = strategy
        self.__active = False
        self.__thread = threading.Thread(target=self._run(), name='MainEngine.__thread')

    def _run(self):
        while self.__active:
            if self.__market_engine.empty():
                time.sleep(1)
            else:
                event = self.__market_engine.get(block=False)
                order_event = self.__strategy.run(event)


    def __process(self, event: Event):
        if event.event_type in self.__handlers:
            for handler in self.__handlers[event.event_type]:
                handler(event)

    def start(self):
        self.__active = True
        self.__thread.start()

    def stop(self):
        self.__active = False
        self.__thread.join()

    def register(self, event_type: EventTypeEnum, handler):
        if handler not in self.__handlers[event_type]:
            self.__handlers[event_type].append(handler)

    def unregister(self, event_type: EventTypeEnum, handler):
        """注销事件处理函数"""
        handler_list = self.__handlers.get(event_type)
        if handler_list is None:
            return
        if handler in handler_list:
            handler_list.remove(handler)
        if len(handler_list) == 0:
            self.__handlers.pop(event_type)

    def put(self, event: Event):
        self.__queue.put(event)

    @property
    def queue_size(self):
        return self.__queue.qsize()
