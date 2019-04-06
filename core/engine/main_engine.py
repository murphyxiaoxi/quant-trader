import threading
import time

from core.common.portfolio import Portfolio
from core.common.strategyTemplate import StrategyTemplate
from core.engine.market_engine import MarketEngine


class MainEngine:
    def __init__(self, strategy: StrategyTemplate):
        self.__strategy = strategy

        self.__symbols = strategy.symbols
        self.__back_test = strategy.back_test
        self.__start_date = strategy.start_date
        self.__end_date = strategy.end_date
        self.__market_engine = MarketEngine(self.__symbols, self.__back_test, self.__start_date, self.__end_date)

        self.__portfolio = Portfolio(strategy.id(), strategy.name(), strategy.description(),
                                     self.__symbols, self.__init_capital, self.__back_test)

        self.__active = False
        self.__thread = threading.Thread(target=self._run(), name='MainEngine.__thread')
        self.init()

    def init(self):
        self.__market_engine.run()

    def _run(self):
        sleep_time = 0.0
        while self.__active:

            if self.__market_engine.empty():
                time.sleep(0.2)
                sleep_time += 0.2
            else:
                event = self.__market_engine.get(block=False)
                order_event = self.__strategy.run(event)
                self.__portfolio.order_process(order_event)
            # 回测的话 超过60秒没有事件则认为回测结束
            if self.__back_test and sleep_time > 60:
                self.stop()

    def start(self):
        self.__active = True
        self.__thread.start()

    def stop(self):
        self.__active = False
        statistic, equity_curve = self.__portfolio.statistic_summary()
        print(statistic)
        self.__thread.join()
