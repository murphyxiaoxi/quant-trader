from typing import List, Optional, Dict, Any

import pandas
import pandas as pd

from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums import order_type_enums, bar_val_type_enums
from backend.commons.enums.date_format_enums import DateFormatStrEnum
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.order_type_enums import OrderTypeEnum
from backend.commons.enums.signal_type_enums import SignalTypeEnum
from backend.commons.enums.symbol_type import SymbolTypeEnum
from backend.commons.events.base import FillEvent, OrderEvent, SignalEvent, MarketEvent
from backend.commons.performance import StatisticSummary, EquityCurve
from backend.commons.performance.base_performance import create_sharpe_ratio, create_draw_downs
from backend.commons.portfolios.domain import PositionDO, HoldingDO, PortfolioDO
# todo 完善功能 重要
from dao.mongo import MongoBase


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.

    The positions DataFrame stores a time-index of the
    quantity of positions held.

    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular
    time-index, as well as the percentage change in
    portfolios total across bars.
    """

    def __init__(
            self,
            portfolio_id: int,
            name: str,
            description: str,
            start_date_str: str,
            date_format: DateFormatStrEnum,
            symbol_list: List[str],
            initial_capital: float = 100000.0,
            is_back_test: bool = False
    ):
        """
        证券投资组合账户
        :param portfolio_id:
        :param start_date_str:
        :param symbol_list:
        :param initial_capital:
        :param is_back_test:
        """
        """
        Initialises the portfolios with bars and an event queue.
        Also includes a starting datetime index and initial capital
        (USD unless otherwise stated).

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolios.
        initial_capital - The starting capital in USD.
        """
        self._mongo = MongoBase("portfolio", "back_test" if is_back_test else "online")
        self._portfolio_do = PortfolioDO(
            portfolio_id, name, description, start_date_str, date_format,
            symbol_list, initial_capital,
            self._init_all_positions(start_date_str, symbol_list),
            self._init_current_positions(start_date_str, symbol_list),
            self._init_all_holdings(start_date_str, initial_capital, symbol_list),
            self._init_current_holdings(start_date_str, initial_capital, symbol_list)
        )
        self._mongo.table.update({"portfolio_id": self._portfolio_do.portfolio_id},
                                 {"$set": self._portfolio_do.convert_2_dict()}, upsert=True)

        self._equity_curve: pandas.DataFrame = None

    def _update_portfolio_2_mongo(self):
        self._mongo.table.update({"portfolio_id": self._portfolio_do.portfolio_id},
                                 {"$set": self._portfolio_do.convert_2_dict()}, upsert=True)

    @staticmethod
    def _init_all_positions(start_date_str: str, symbol_list: List[str]) -> List[PositionDO]:
        """
                Constructs the positions list using the start_date
                to determine when the time index will begin.
                """
        d = dict([(s, 0) for s in symbol_list])
        return [PositionDO(start_date_str, d)]

    @staticmethod
    def _init_current_positions(start_date_str, symbol_list: List[str]) -> PositionDO:
        """
                Constructs the positions list using the start_date
                to determine when the time index will begin.
                """
        d = dict([(s, 0) for s in symbol_list])
        return PositionDO(start_date_str, d)

    @staticmethod
    def _init_all_holdings(start_date_str: str, init_capital: float, symbol_list: List[str]) -> List[HoldingDO]:
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict([(s, 0.0) for s in symbol_list])
        return [HoldingDO(start_date_str, init_capital, 0.0, init_capital, d)]

    @staticmethod
    def _init_current_holdings(start_date_str: str, init_capital: float, symbol_list: List[str]) -> HoldingDO:
        """
        Constructs the holdings list using the start_dated
        to determine when the time index will begin.
        """
        d = dict([(s, 0.0) for s in symbol_list])
        return HoldingDO(start_date_str, init_capital, 0.0, init_capital, d)

    def update_time_index_for_market_event(self, market_event: MarketEvent, data_handler: CommonDataHandler):
        """
        Adds a new record to the positions matrix for the current
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """
        previous_date_time = market_event.previous_date_time()

        # Update positions
        # ================
        dp = dict([(s, 0) for s in self._portfolio_do.symbol_list])
        position = PositionDO(previous_date_time, dp)

        # 复制previousPosition 方便后续计算
        for symbol_code in self._portfolio_do.symbol_list:
            dp[symbol_code] = self._portfolio_do.current_position.symbol_position[symbol_code]

        # Append the current positions
        self._portfolio_do.all_position.append(position)

        # Update holdings
        # ===============
        dh = dict((k, v) for k, v in [(s, 0) for s in self._portfolio_do.symbol_list])
        holding = HoldingDO(previous_date_time, self._portfolio_do.current_holding.cash,
                            self._portfolio_do.current_holding.commission,
                            self._portfolio_do.current_holding.total, dh)

        # 复制previousHolding 方便后续计算
        for symbol_code in self._portfolio_do.symbol_list:
            # Approximation to the real value
            market_value: float = float(
                self._portfolio_do.current_position.symbol_position[symbol_code]
                * data_handler.get_bar_value(symbol_code, previous_date_time,
                                             bar_val_type_enums.BarValTypeEnum.ADJ_CLOSE)
            )
            dh[symbol_code] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self._portfolio_do.all_holding.append(holding)
        self._update_portfolio_2_mongo()

    # ======================
    # FILL/POSITION HANDLING
    # ======================
    def generate_order_event(self, signal_event: SignalEvent) -> Optional[OrderEvent]:
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolios logic.
        """
        if signal_event.event_type() == EventTypeEnum.SIGNAL:
            order_event = self._generate_naive_order(signal_event)
            return order_event
        else:
            return None

    def update_fill(self, fill_event: FillEvent, data_handler: CommonDataHandler):
        """
        Updates the portfolios current positions and holdings
        from a FillEvent.
        """
        if fill_event.event_type() == EventTypeEnum.FILL:
            self._update_positions_from_fill(fill_event)
            self._update_holdings_from_fill(fill_event, data_handler)

    def _update_positions_from_fill(self, fill_event: FillEvent):
        """
        Takes a Fill object and updates the position matrix to
        reflect the new position.

        Parameters:
        fill - The Fill object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill_event.direction_type == order_type_enums.DirectionTypeEnum.BUY:
            fill_dir = 1
        if fill_event.direction_type == order_type_enums.DirectionTypeEnum.SELL:
            fill_dir = -1

        # Update positions list with new quantities
        self._portfolio_do.current_position.symbol_position[fill_event.symbol_code()] += fill_dir * fill_event.quantity
        self._update_portfolio_2_mongo()

    def _update_holdings_from_fill(self, fill_event: FillEvent, data_handler: CommonDataHandler):
        """
        Takes a Fill object and updates the holdings matrix to
        reflect the holdings value.

        Parameters:
        fill - The Fill object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill_event.direction_type == order_type_enums.DirectionTypeEnum.BUY:
            fill_dir = 1
        if fill_event.direction_type == order_type_enums.DirectionTypeEnum.SELL:
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = data_handler.get_bar_value(
            fill_event.symbol_code, fill_event.date_time(), bar_val_type_enums.BarValTypeEnum.ADJ_CLOSE
        )
        cost = fill_dir * fill_cost * fill_event.quantity

        self._portfolio_do.current_holding.symbol_hold[fill_event.symbol_code()] += cost
        self._portfolio_do.current_holding.commission += fill_event.commission
        self._portfolio_do.current_holding.cash -= (cost + fill_event.commission)
        self._portfolio_do.current_holding.total -= (cost + fill_event.commission)
        self._update_portfolio_2_mongo()

    def _generate_naive_order(self, signal_event: SignalEvent) -> OrderEvent:
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None

        symbol_code = signal_event.symbol_code()
        signal_type = signal_event.signal_type
        strength = signal_event.strength

        mkt_quantity = 100
        cur_quantity = self._portfolio_do.current_position.symbol_position[symbol_code]
        order_type = OrderTypeEnum.MARKET

        if signal_type == SignalTypeEnum.UP and cur_quantity == 0:
            order = OrderEvent(symbol_code, signal_event.date_time(), order_type, mkt_quantity,
                               order_type_enums.DirectionTypeEnum.BUY)

        if signal_type == SignalTypeEnum.DOWN and cur_quantity == 0:
            order = OrderEvent(symbol_code, signal_event.date_time(), order_type, mkt_quantity,
                               order_type_enums.DirectionTypeEnum.SELL)

        if signal_type == SignalTypeEnum.HOLD and cur_quantity > 0:
            order = OrderEvent(symbol_code, signal_event.date_time(), order_type, abs(cur_quantity),
                               order_type_enums.DirectionTypeEnum.SELL)

        if signal_type == SignalTypeEnum.HOLD and cur_quantity < 0:
            order = OrderEvent(symbol_code, signal_event.date_time(), order_type, abs(cur_quantity),
                               order_type_enums.DirectionTypeEnum.BUY)
        return order

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================
    def statistic_summary(self, symbol_type: SymbolTypeEnum) -> (StatisticSummary, EquityCurve):
        """
        Creates a list of summary statistics for the portfolios.
        """
        self._create_equity_curve_data_frame()

        total_return = self._equity_curve['equity_curve'][-1]
        returns = self._equity_curve['returns']
        pnl = self._equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, symbol_type)
        draw_down, max_drawn_down, drawn_down_duration = create_draw_downs(pnl)
        self._equity_curve['draw_down'] = draw_down

        stats = StatisticSummary(
            (total_return - 1.0) * 100.0,
            sharpe_ratio,
            max_drawn_down * 100.0,
            drawn_down_duration
        )

        return stats, EquityCurve(self._equity_curve)

    def equity_curve(self):
        return self._equity_curve

    def _create_equity_curve_data_frame(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        converted_all_holding = []
        for holding in self._portfolio_do.all_holding:
            d: Dict[str, Any] = holding.symbol_hold
            d['date'] = holding.date_str
            d['cash'] = holding.cash
            d['total'] = holding.total
            d['commission'] = holding.commission
            converted_all_holding.append(d)

        curve = pd.DataFrame(converted_all_holding)
        curve.set_index('date', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self._equity_curve = curve
        self._update_portfolio_2_mongo()
