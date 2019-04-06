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
        self.__running = threading.Event()
        self.__pause = threading.Event()

    def init(self):
        self.__market_engine.start()
        self.__strategy.portfolio = self.__portfolio

    def start(self):
        self.__running.set()
        self.__pause.set()
        self.__thread.start()
        self.__market_engine.start()

    def pause(self):
        self.__market_engine.pause()
        self.__pause.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__pause.set()  # 设置为True, 让线程停止阻塞
        self.__market_engine.resume()

    def stop(self):
        self.__market_engine.stop()
        self.__pause.set()
        self.__running.clear()
        statistic, equity_curve = self.__portfolio.statistic_summary()
        print("回测结果", statistic)

    def __run(self):
        sleep_time = 0.0
        while self.__running.isSet():
            self.__pause.wait()
            if self.__market_engine.empty():
                time.sleep(0.2)
                sleep_time += 0.2
                continue
            else:
                event = self.__market_engine.get(block=False)
                # 强制退出
                if event == 0:
                    break

                order_event = self.__strategy.run(event)
                self.__portfolio.order_process(order_event)
            # 回测的话 超过60秒没有事件则认为回测结束
            if self.__back_test and sleep_time > 60:
                self.stop()
