from datetime import datetime
from typing import Dict


class Position(object):
    def __init__(self, date_time: datetime, symbol_position: Dict[str, int]):
        """

        :param date_time:
        :param symbol_position: map(symbol_code -> position)
        """
        self.date_time: datetime = date_time
        self.symbol_position: Dict[str, int] = symbol_position


class Holding(object):
    def __init__(self, date_time: datetime, cash: float, commission: float, total: float,
                 symbol_hold: Dict[str, float]):
        """

        :param date_time:
        :param cash:
        :param commission:
        :param total:
        :param symbol_hold:
        """
        self.date_time: datetime = date_time
        self.cash: float = cash
        self.commission: float = commission
        self.total: float = total
        self.symbol_hold: Dict[str, float] = symbol_hold
