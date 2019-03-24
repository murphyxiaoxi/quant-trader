from enum import Enum


class OrderTypeEnum(Enum):
    """
    MARKET 市价单
    LIMIT 限价单
    """
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class DirectionTypeEnum(Enum):
    BUY = "BUY"
    SELL = "SELL"
