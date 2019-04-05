import abc

from core.common.default_logger import DefaultLogHandler
from core.common.event import MarketEvent


class StrategyTemplate(metaclass=abc.ABCMeta):
    def __init__(self, main_engine, back_test: bool, log_handler=None):
        self.main_engine = main_engine
        self.clock_engine = main_engine.clock_engine
        self.back_test = back_test
        # 优先使用自定义 log 句柄, 否则使用主引擎日志句柄
        self.logger = self.log_handler() or log_handler
        self.init()

    @abc.abstractmethod
    def init(self):
        # 进行相关的初始化操作
        raise NotImplementedError()

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def strategy(self, event: MarketEvent):
        """:param event event.data 为所有股票的信息，结构如下
        {'162411':
        {'ask1': '0.493',
         'ask1_volume': '75500',
         'ask2': '0.494',
         'ask2_volume': '7699281',
         'ask3': '0.495',
         'ask3_volume': '2262666',
         'ask4': '0.496',
         'ask4_volume': '1579300',
         'ask5': '0.497',
         'ask5_volume': '901600',
         'bid1': '0.492',
         'bid1_volume': '10765200',
         'bid2': '0.491',
         'bid2_volume': '9031600',
         'bid3': '0.490',
         'bid3_volume': '16784100',
         'bid4': '0.489',
         'bid4_volume': '10049000',
         'bid5': '0.488',
         'bid5_volume': '3572800',
         'buy': '0.492',
         'close': '0.499',
         'high': '0.494',
         'low': '0.489',
         'name': '华宝油气',
         'now': '0.493',
         'open': '0.490',
         'sell': '0.493',
         'turnover': '420004912',
         'volume': '206390073.351'}}
        """
        raise NotImplementedError()

    def run(self, event):
        self.strategy(event)

    @abc.abstractmethod
    def clock(self, event):
        raise NotImplementedError()

    def log_handler(self):
        """
        优先使用在此自定义 log 句柄, 否则返回None, 并使用主引擎日志句柄
        :return: log_handler or None
        """
        return DefaultLogHandler(self.name(), log_type='stdout', filepath=self.name() + '.log')

    @abc.abstractmethod
    def shutdown(self):
        """
        关闭进程前调用该函数
        :return:
        """
        raise NotImplementedError()
