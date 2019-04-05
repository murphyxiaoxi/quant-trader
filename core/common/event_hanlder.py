import abc

from core.common.event import Event, EventTypeEnum


class EventHandler(metaclass=abc.ABCMeta):
    def __init__(self, event_type: EventTypeEnum):
        self.__event_type = event_type

    def run(self, event: Event):
        if event.event_type == self.__event_type:
            self._process(event)

    @abc.abstractmethod
    def _process(self, event: Event):
        raise NotImplementedError()


class MarketEventHandler(EventHandler):

