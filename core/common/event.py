import abc
import typing
from enum import Enum


class EventTypeEnum(Enum):
    """
    事件类型枚举
    """
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


class Event(metaclass=abc.ABCMeta):
    def __init__(self, event_type: EventTypeEnum, data=None):
        self.event_type = event_type
        self.data = data


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self, data: typing.Dict):
        """
        Initialises the MarketEvent.
        """
        super(MarketEvent, self).__init__(EventTypeEnum.MARKET, data)

    def __str__(self) -> str:
        return "MarketEvent(event_type=%s, data=%s)" % (self.event_type, self.data)
