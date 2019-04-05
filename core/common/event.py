import abc
from enum import Enum, unique
from typing import Dict

import pandas


@unique
class EventTypeEnum(Enum):
    """
    事件类型枚举
    """
    CLOCK = 0
    MARKET = 1
    ORDER = 2


@unique
class OrderTypeEnum(Enum):
    SELL = -1
    HOLD = 0
    BUY = 1


class Event(metaclass=abc.ABCMeta):
    def __init__(self, event_type: EventTypeEnum, data=None):
        self.event_type = event_type
        self.data = data

    def __str__(self):
        return "Event(event_type=%s, data=%s)" % (self.event_type, self.data)


class ClockEvent(Event):
    def __init__(self, date: str):
        """

        :param date: 交易日期
        """
        super(ClockEvent, self).__init__(EventTypeEnum.CLOCK, date)


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self, is_previous: bool, data: pandas.DataFrame):
        """
        Initialises the MarketEvent.
        """
        super(MarketEvent, self).__init__(EventTypeEnum.MARKET, data)
        self.is_previous = is_previous


class OrderEvent(Event):
    def __init__(self, date: str, data: Dict[str, OrderTypeEnum]):
        super(OrderEvent, self).__init__(EventTypeEnum.ORDER, data)
        self.date = date
