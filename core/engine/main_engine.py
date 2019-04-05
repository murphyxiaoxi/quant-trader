import threading
import time
from typing import List

from core.common.portfolio import Portfolio
from core.common.strategyTemplate import StrategyTemplate
from core.engine.market_engine import MarketEngine


class MainEngine:
    def __init__(self, symbols: List[str], strategy: StrategyTemplate,
                 init_capital: float,
                 back_test=True, start_date=None, end_date=None):
        self.__symbols = symbols
        self.__back_test = back_test
        self.__start_date = start_date
        self.__end_date = end_date
        self.__market_engine = MarketEngine(symbols, back_test, start_date, end_date)
        self.__strategy = strategy
        self.__active = False
        self.__portfolio = Portfolio(strategy.id(), strategy.name(), strategy.description(), symbols, init_capital,
                                     back_test)
        self.__thread = threading.Thread(target=self._run(), name='MainEngine.__thread')
        self.init()

    def init(self):
        self.__market_engine.run()

    def _run(self):
        while self.__active:
            if self.__market_engine.empty():
                time.sleep(0.2)
            else:
                event = self.__market_engine.get(block=False)
                order_event = self.__strategy.run(event)
                self.__portfolio.order_process(order_event)

    def start(self):
        self.__active = True
        self.__thread.start()

    def stop(self):
        self.__active = False
        statistic, equity_curve = self.__portfolio.statistic_summary()
        print(statistic)
        self.__thread.join()
