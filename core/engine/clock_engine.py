import abc
import queue
import threading
import time

import tushare

from core.common.event import ClockEvent


class ClockEngine(metaclass=abc.ABCMeta):
    def __init__(self, clock_event_queue=None):
        """
        时钟引擎
        """
        self._clock_queue = clock_event_queue or queue.Queue()
        self.__thread = threading.Thread(target=self._tick, name="ClockEngine.__thread")
        self._active = False

    @abc.abstractmethod
    def _tick(self):
        raise NotImplementedError()

    def empty(self):
        return self._clock_queue.empty()

    def get(self) -> ClockEvent:
        return self._clock_queue.get(block=False)

    def start(self):
        self._active = True
        self.__thread.start()

    def stop(self):
        self._active = False


class BackTestClockEngine(ClockEngine):
    def __init__(self, start_date: str, end_date: str, clock_event_queue=None):
        super(BackTestClockEngine, self).__init__(clock_event_queue)

        self._start_date = start_date
        self._end_date = end_date

    def _tick(self):
        while self._active:
            pro_api = tushare.pro_api('65ff56dd66d10436614eefa5a87498c265acb97fdb8be9937c4f2d80')
            cal_df = pro_api.trade_cal(exchange='', start_date=self._start_date, end_date=self._end_date)
            cals = cal_df[cal_df['is_open'] == 1]['cal_date']
            for cal in cals:
                self._clock_queue.put(ClockEvent(cal), block=False)

            time.sleep(60)
        print("BackTestClockEngine stopped===")

    def start(self):
        super().start()
        time.sleep(2)
        super().stop()


class OnlineClockEngine(ClockEngine):
    def __init__(self, clock_event_queue=None):
        super(OnlineClockEngine, self).__init__(clock_event_queue)

    def _tick(self):
        # todo
        pass


if __name__ == '__main__':
    engine = BackTestClockEngine('20190401', '20190620')
    engine.start()

    while True:
        print(engine.get())
