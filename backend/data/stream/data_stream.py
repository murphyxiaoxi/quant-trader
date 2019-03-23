from abc import ABCMeta, abstractmethod


class DataStream(metaclass=ABCMeta):
    def __init__(self):
        raise NotImplementedError()

    @abstractmethod
    def history_data(self, symbol: str, start_date: str, end_date: str):
        """
        获取某时间范围历史K线数据
        :param symbol
        :param start_date:
        :param end_date:
        :return: data_frame cols:symbol,open,high,low,close,volume,price_change,p_change
        """
        raise NotImplementedError()

    def get_bar_data(self, symbol: str, date: str):
        """
        获取某天K线数据
        :param symbol
        :param date:
        :return:data_frame cols:symbol,open,high,low,close,volume,price_change,p_change
        """
        raise NotImplementedError()

    def get_latest_n_bars(self, symbol: str, n: int = 1):
        """
        获取最近N天的K线数据
        :param symbol
        :param n:
        :return:
        """
        raise NotImplementedError()
