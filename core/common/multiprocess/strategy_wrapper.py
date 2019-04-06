import multiprocessing as mp
from threading import Thread

from core.common.strategyTemplate import StrategyTemplate
from core.engine.main_engine import MainEngine

__author__ = 'murphy xiaoxi'


class ProcessWrapper(object):
    def __init__(self, strategy: StrategyTemplate):
        """
        @:param strategy 策略
        """
        self.__strategy = strategy
        # 事件队列
        self.__market_event_queue = mp.Queue(10000)
        # 时钟队列
        self.__clock_queue = mp.Queue(10000)

        self.__strategy.clock_event_queue = self.__clock_queue
        self.__strategy.market_event_queue = self.__market_event_queue

        self.__main_engine = MainEngine(strategy)
        # 包装进程
        self.__proc = mp.Process(target=self.__process)
        self.__proc.start()

    def stop(self):
        """
        停止
        """
        self.__clock_queue.put(0)
        self.__market_event_queue.put(0)
        self.__proc.join()

    def __run(self):
        """
        处理事件
        """

        self.__main_engine.start()

    def __process(self):
        """
        启动进程
        """
        main_engine_thread = Thread(target=self.__run(), name="ProcessWrapper._process_clock")
        main_engine_thread.start()

        main_engine_thread.join()
