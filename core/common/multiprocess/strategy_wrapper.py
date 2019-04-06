import multiprocessing as mp
from threading import Thread

from core.common.strategyTemplate import StrategyTemplate

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
        # 包装进程
        self.__proc = mp.Process(target=self._process)
        self.__proc.start()

    def stop(self):
        """
        停止
        """
        self.__market_event_queue.put(0)
        self.__clock_queue.put(0)
        self.__proc.join()

    def on_event(self, event):
        """
        推送消息
        """
        # print(event)
        self.__market_event_queue.put(event)

    def on_clock(self, event):
        """
        推送时钟
        """
        self.__clock_queue.put(event)

    def _process_event(self):
        """
        处理事件
        """
        while True:
            try:
                event = self.__market_event_queue.get(block=True)
                # 退出
                if event == 0:
                    break
                self.__strategy.run(event)
            except Exception as e:
                self.__strategy.log_handler().error("Strategy:%s _process_event error %s", self.__strategy.name(), e)

    def _process_clock(self):
        """
        处理时间
        """
        while True:
            try:
                event = self.__clock_queue.get(block=True)
                # 退出
                if event == 0:
                    break
                self.__strategy.clock(event)
            except Exception as e:
                self.__strategy.log_handler().error("Strategy:%s _process_clock error, e:%s", e)

    def _process(self):
        """
        启动进程
        """
        event_thread = Thread(target=self._process_event, name="ProcessWrapper._process_event")
        event_thread.start()
        clock_thread = Thread(target=self._process_clock, name="ProcessWrapper._process_clock")
        clock_thread.start()

        event_thread.join()
        clock_thread.join()
