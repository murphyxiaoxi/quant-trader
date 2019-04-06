import threading
import time

from core.common.portfolio import Portfolio
from core.common.strategyTemplate import StrategyTemplate
from core.engine.market_engine import MarketEngine


class MainEngine:
    def __init__(self, strategy: StrategyTemplate):
        self.__strategy = strategy

        self.__symbols = strategy.symbols
        self.__init_capital = strategy.init_capital
        self.__back_test = strategy.back_test
        self.__start_date = strategy.start_date
        self.__end_date = strategy.end_date

        self.__market_engine = MarketEngine(self.__symbols,
                                            strategy.market_data_func,
                                            self.__back_test,
                                            self.__start_date,
                                            self.__end_date,
                                            clock_event_queue=strategy.clock_event_queue,
                                            market_event_queue=strategy.market_event_queue)

        self.__portfolio = Portfolio(strategy.id(), strategy.name(), strategy.description(),
                                     self.__symbols, self.__init_capital, self.__back_test)

        self.init()

        self.__thread = threading.Thread(target=self.__run, name="MarketEngine.__thread")
        self.__active = False

    def init(self):
        self.__strategy.portfolio = self.__portfolio

    def start(self):
        self.__active = True
        self.__thread.start()
        self.__market_engine.start()

    def stop(self):
        self.__market_engine.stop()
        self.__active = False
        statistic, equity_curve = self.__portfolio.statistic_summary()
        print("回测结果", statistic)

    def __run(self):
        sleep_time = 0.0
        while self.__active:
            if self.__market_engine.empty():
                time.sleep(0.2)
                sleep_time += 0.2
                # 回测的话 超过60秒没有事件则认为回测结束
                if self.__back_test and sleep_time > 60:
                    self.stop()
                continue
            else:
                event = self.__market_engine.get(block=False)
                # 强制退出
                if event == 0:
                    break

                order_event = self.__strategy.run(event)
                self.__portfolio.order_process(order_event)

        print("MainEngine stopped===")
