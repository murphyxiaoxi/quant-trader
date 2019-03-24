import pandas


class StatisticSummary:
    def __init__(self,
                 total_return: float,
                 sharpe_ratio: float,
                 max_drawn_down: float,
                 drawn_down_duration: int
                 ):
        self.total_return: float = total_return
        self.sharpe_ratio: float = sharpe_ratio
        self.max_drawn_down: float = max_drawn_down
        self.drawn_down_duration: int = drawn_down_duration


class EquityCurve:
    def __init__(self, data: pandas.DataFrame):
        self.data: pandas.DataFrame = data
