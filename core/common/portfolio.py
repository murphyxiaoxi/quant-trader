import threading
from collections import OrderedDict, defaultdict
from typing import List, Dict

import pandas

from core.common.event import OrderEvent, EventTypeEnum, OrderTypeEnum
from core.common.performance import create_sharpe_ratio, create_draw_downs
from dao.mongo_base import MongoBase


class Portfolio(object):
    def __init__(
            self,
            strategy_id: int,
            strategy_name: str,
            description: str,
            symbols: List[str],
            initial_capital: float = 100000.0,
            is_back_test: bool = False
    ):
        """
        证券投资组合账户
        :param strategy_id:
        :param strategy_name:
        :param description:
        :param symbols:
        :param initial_capital:
        :param is_back_test:
        """
        self.__mongo = MongoBase("portfolio", "back_test" if is_back_test else "online")
        self.strategy_id = strategy_id
        self.strategy_name = strategy_name
        self.description = description
        self.symbols = symbols
        self.init_capital = initial_capital
        self.is_back_test = is_back_test
        self.__lock = threading.Lock()

        self._equity_curve: pandas.DataFrame = None

    def __init_document(self):
        document = {
            'strategy_id': self.strategy_id,
            'strategy_name': self.strategy_name,
            'description': self.description,
            'symbols': self.symbols,
            'init_capital': self.init_capital,
            'is_back_test': self.is_back_test,
            'all_position': [],
            'all_holding': []
        }
        self.__lock.acquire()
        self.__mongo.table.update({"strategy_id": self.strategy_id, 'strategy_name': self.strategy_name},
                                  {"$set": document}, upsert=True)

        self.__lock.release()

    def __append_position(self, date: str, symbol_position: OrderedDict[str, int]):
        self.__lock.acquire()
        position = {
            'date': date,
            'symbol_position': symbol_position
        }

        document = self.__mongo.table.find_one({'strategy_id': self.strategy_id, 'strategy_name': self.strategy_name})
        document['all_position'].append(position)

        self.__mongo.table.update({"strategy_id": self.strategy_id, 'strategy_name': self.strategy_name},
                                  {'$set': document}, upsert=True)
        self.__lock.release()

    def latest_position(self):
        self.__lock.acquire()

        document = self.__mongo.table.find_one({'strategy_id': self.strategy_id, 'strategy_name': self.strategy_name})

        self.__lock.release()

        if len(document['all_position']) == 0:
            return None

        return document['all_position'][-1]

    def __append_holding(self, date: str, cash: float,
                         total: float, commission: float,
                         symbol_holding: OrderedDict[str, float]):
        self.__lock.acquire()
        holding = {
            'date': date,
            'cash': cash,
            'total': total,
            'commission': commission,
            'symbol_holding': symbol_holding
        }

        document = self.__mongo.table.find_one({'strategy_id': self.strategy_id, 'strategy_name': self.strategy_name})
        document['all_holding'].append(holding)

        self.__mongo.table.update({"strategy_id": self.strategy_id, 'strategy_name': self.strategy_name},
                                  {'$set': document}, upsert=True)
        self.__lock.release()

    def latest_holding(self):
        self.__lock.acquire()

        document = self.__mongo.table.find_one({'strategy_id': self.strategy_id, 'strategy_name': self.strategy_name})

        self.__lock.release()

        if len(document['all_holding']) == 0:
            return None

        return document['all_holding'][-1]

    def __all_holding(self):
        self.__lock.acquire()

        document = self.__mongo.table.find_one({'strategy_id': self.strategy_id, 'strategy_name': self.strategy_name})

        self.__lock.release()

        if len(document['all_holding']) == 0:
            return defaultdict(float)

        return document['all_holding']

    # ======================
    # FILL/POSITION HANDLING
    # ======================
    def order_process(self, order_event: OrderEvent):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolios logic.
        """
        if order_event.event_type != EventTypeEnum.ORDER:
            return

        last_position = self.latest_holding()
        last_holding = self.latest_position()

        if last_position is None:
            last_position = {
                'date': order_event.date,
                'symbol_position': defaultdict(int)
            }

        if last_holding is None:
            last_holding = {
                'date': order_event.date,
                'cash': self.init_capital,
                'total': self.init_capital,
                'commission': 0.0,
                'symbol_holding': defaultdict(float)
            }

        cash = last_holding['cash']
        total = last_holding['total']
        commission = last_holding['commission']

        for symbol in order_event.quantity.keys():
            direction = order_event.direction[symbol]
            fill_dir = self.__dir_int(direction)  # 买1 卖-1 其他0
            quantity = order_event.quantity[symbol]

            last_position[symbol] += fill_dir * quantity

            cost = fill_dir * quantity * order_event.price[symbol]
            last_holding[symbol] -= cost

            cash -= cost

        cash -= order_event.total_commission
        # 当前持有股票市值 + 现金
        last_holding['total'] = cash + sum([(order_event.price[symbol] * position) for symbol, position in
                                            last_position['symbol_position']])

        commission += order_event.total_commission

        self.__append_position(order_event.date, last_position)
        self.__append_holding(order_event.date, cash, total, commission, last_holding)

    @staticmethod
    def __dir_int(direction: OrderTypeEnum):
        """

        :param direction:
        :return: 买 1   卖 -1  其他0
        """
        if direction == OrderTypeEnum.BUY:
            return 1
        elif direction == OrderTypeEnum.SELL:
            return -1
        else:
            return 0

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================
    def statistic_summary(self):
        """
        Creates a list of summary statistics for the portfolios.
        """
        self._create_equity_curve_data_frame()

        total_return = self._equity_curve['equity_curve'][-1]
        returns = self._equity_curve['returns']
        pnl = self._equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        draw_down, max_drawn_down, drawn_down_duration = create_draw_downs(pnl)
        self._equity_curve['draw_down'] = draw_down

        stats = {
            'total_return': (total_return - 1.0) * 100.0,
            'sharpe_ratio': sharpe_ratio,
            'max_drawn_down': max_drawn_down * 100.0,
            'drawn_down_duration': drawn_down_duration
        }

        return stats, self._equity_curve

    def equity_curve(self):
        return self._equity_curve

    def _create_equity_curve_data_frame(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        converted_all_holding = []
        for holding in self.__all_holding():
            d: Dict[str, float] = holding['symbol_holding']
            d['date'] = holding['date']
            d['cash'] = holding['cash']
            d['total'] = holding['total']
            d['commission'] = holding['commission']
            converted_all_holding.append(d)

        curve = pandas.DataFrame(converted_all_holding)
        curve.set_index('date', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self._equity_curve = curve
