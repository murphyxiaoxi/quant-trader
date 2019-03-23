from enum import Enum


class OrderTypeEnum(Enum):
    """
    MARKET 市价单
    LIMIT 限价单
    """
    MARKET = 0
    LIMIT = 1
