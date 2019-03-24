from enum import Enum


class EventTypeEnum(Enum):
    """
    事件类型枚举
    """
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


class DirectionTypeEnum(Enum):
    BUY = "BUY"
    SELL = "SELL"


