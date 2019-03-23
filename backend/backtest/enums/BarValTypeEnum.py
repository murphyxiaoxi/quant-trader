from enum import Enum, unique


@unique
class BarValTypeEnum(Enum):
    Open = 0
    High = 1
    Low = 2
    Close = 3
    Volume = 4
    IO = 5

