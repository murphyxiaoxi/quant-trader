from enum import Enum, unique


@unique
class BarValTypeEnum(Enum):
    Open = "OPEN"
    High = "HIGH"
    Low = "LOW"
    Close = "CLOSE"
    Volume = "VOLUME"
    ADJ_CLOSE = "ADJ_CLOSE"


