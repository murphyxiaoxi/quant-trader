from enum import Enum


class EventTypeEnum(Enum):
    """
    事件类型枚举
    """
    MARKET = 0
    SIGNAL = 1
    ORDER = 2
    FILL = 3