from core.common.default_logger import logger
import queue
import threading
from collections import defaultdict

from core.common.event import Event, EventTypeEnum


class EventEngine:
    def __init__(self):
        self.__queue = queue.Queue()
        self.__active = False
        self.__thread = threading.Thread(target=self._run(), name='EventEngine.__thread')
        self.__handlers = defaultdict(list)

    def _run(self):
        while self.__active:
            try:
                event = self.__queue.get(True, timeout=1)
                event_handle_thread = threading.Thread(target=self.__process, name='EventEngine.__process',
                                                       args=(event,))
                event_handle_thread.start()
            except Exception as e:
                logger.error("EventEngine _run error, e:%s", e)

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

    def unregister(self, event_type, handler):
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
