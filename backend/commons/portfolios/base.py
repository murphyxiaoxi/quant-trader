from datetime import datetime
from typing import List, Optional

import pandas as pd

from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums import order_type_enums, bar_val_type_enums
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.order_type_enums import OrderTypeEnum
from backend.commons.enums.signal_type_enums import SignalTypeEnum
from backend.commons.events.base import FillEvent, OrderEvent, SignalEvent, MarketEvent
from backend.commons.performance.base_performance import create_sharpe_ratio, create_draw_downs


# todo 完善功能 重要
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

    def __init__(self, data_handler: CommonDataHandler, start_date: datetime, symbol_code_list: List[str],
                 initial_capital: float = 100000.0):
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
        self.data_handler: CommonDataHandler = data_handler
        self.symbol_code_list = symbol_code_list
        self.start_date: datetime = start_date
        self.initial_capital: float = initial_capital

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k, v) for k, v in [(s, 0) for s in self.symbol_code_list])

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        self.equity_curve = None

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbol_code_list])
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_code_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolios across all symbols.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_code_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def update_time_index_for_market_event(self, market_event: MarketEvent):
        """
        Adds a new record to the positions matrix for the current
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = market_event.date_time()

        # Update positions
        # ================
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_code_list])
        dp['datetime'] = latest_datetime

        for s in self.symbol_code_list:
            dp[s] = self.current_positions[s]

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        # ===============
        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_code_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_code_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * \
                           self.data_handler.get_latest_bar_value(s, bar_val_type_enums.BarValTypeEnum.ADJ_CLOSE)
            dh[s] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    # ======================
    # FILL/POSITION HANDLING
    # ======================

    def update_positions_from_fill(self, fill_event: FillEvent):
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
        self.current_positions[fill_event.symbol_code] += fill_dir * fill_event.quantity

    def update_holdings_from_fill(self, fill_event: FillEvent):
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
        fill_cost = self.data_handler.get_latest_bar_value(
            fill_event.symbol_code, bar_val_type_enums.BarValTypeEnum.ADJ_CLOSE
        )
        cost = fill_dir * fill_cost * fill_event.quantity
        self.current_holdings[fill_event.symbol_code] += cost
        self.current_holdings['commission'] += fill_event.commission
        self.current_holdings['cash'] -= (cost + fill_event.commission)
        self.current_holdings['total'] -= (cost + fill_event.commission)

    def update_fill(self, fill_event: FillEvent):
        """
        Updates the portfolios current positions and holdings
        from a FillEvent.
        """
        if fill_event.event_type() == EventTypeEnum.FILL:
            self.update_positions_from_fill(fill_event)
            self.update_holdings_from_fill(fill_event)

    def _generate_naive_order(self, signal_event: SignalEvent) -> OrderEvent:
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None

        symbol_code = signal_event.symbol_code
        signal_type = signal_event.signal_type
        strength = signal_event.strength

        mkt_quantity = 100
        cur_quantity = self.current_positions[symbol_code]
        order_type = OrderTypeEnum.MARKET

        if signal_type == SignalTypeEnum.LONG and cur_quantity == 0:
            order = OrderEvent(symbol_code, order_type, mkt_quantity, order_type_enums.DirectionTypeEnum.BUY)
        if signal_type == SignalTypeEnum.SHORT and cur_quantity == 0:
            order = OrderEvent(symbol_code, order_type, mkt_quantity, order_type_enums.DirectionTypeEnum.SELL)

        if signal_type == SignalTypeEnum.EXIT and cur_quantity > 0:
            order = OrderEvent(symbol_code, order_type, abs(cur_quantity), order_type_enums.DirectionTypeEnum.SELL)
        if signal_type == SignalTypeEnum.EXIT and cur_quantity < 0:
            order = OrderEvent(symbol_code, order_type, abs(cur_quantity), order_type_enums.DirectionTypeEnum.BUY)
        return order

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

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================

    def create_equity_curve_data_frame(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolios.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252 * 60 * 6.5)
        draw_down, max_dd, dd_duration = create_draw_downs(pnl)
        self.equity_curve['drawdown'] = draw_down

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        self.equity_curve.to_csv('equity.csv')
        return stats
