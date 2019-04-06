import abc
from enum import Enum, unique
from typing import Dict


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
    def __init__(self, event_type: EventTypeEnum):
        self.event_type = event_type

    def __str__(self):
        return "Event(event_type=%s)" % self.event_type


class ClockEvent(Event):
    def __init__(self, date: str):
        """

        :param date: 交易日期
        """
        super(ClockEvent, self).__init__(EventTypeEnum.CLOCK)
        self.date = date

    def __str__(self):
        return "ClockEvent(event_type=%s,date=%s)" % (self.event_type, self.date)


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self, data):
        """
        Initialises the MarketEvent.
        """
        super(MarketEvent, self).__init__(EventTypeEnum.MARKET)
        self.data = data

    def __str__(self):
        return "MarketEvent(event_type=%s,data=%s)" % \
               (self.event_type, self.data)


class OrderEvent(Event):
    def __init__(self,
                 date: str,
                 direction: Dict[str, OrderTypeEnum],
                 quantity: Dict[str, int],
                 price: Dict[str, float],
                 total_commission: float):
        super(OrderEvent, self).__init__(EventTypeEnum.ORDER)
        self.date = date
        self.direction = direction
        self.quantity = quantity
        self.price = price
        self.total_commission = total_commission

    def __str__(self):
        return "OrderEvent(event_type=%s,date=%s,direction=%s,quantity=%s,price=%s,total_commission=%s)" % \
               (self.event_type, self.date, self.direction, self.quantity, self.price, self.total_commission)
