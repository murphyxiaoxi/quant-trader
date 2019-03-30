#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue
import time
from datetime import datetime
from typing import List, Dict, Optional

from pandas import DataFrame

from backend.commons.abstract_strategy import AbstractStrategy
from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums.date_format_enums import DateFormatStrEnum
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.symbol_type import SymbolTypeEnum
from backend.commons.events.base import AbstractEvent, MarketEvent, SignalEvent, OrderEvent, FillEvent
from backend.commons.order_execution.order_execute_handler import SimulatedOrderExecuteHandler
from backend.commons.portfolios.base import Portfolio


class BackTestEngine(object):
    """
    事件驱动型回测框架
    process_pipeline:
    EventEngine:MarketEvent => DataHandler:Data =>
    Strategy:SignalEvent => Portfolio:OrderEvent =>
    OrderExecuteHandler:FillEvent => Portfolio
    """

    def __init__(self,
                 portfolio_id: int,
                 back_test_name,
                 description: str,
                 symbol_type: SymbolTypeEnum,
                 symbol_list: List[str],
                 initial_capital: float,
                 start_date_str: str,
                 date_format_enum: DateFormatStrEnum,
                 data_handler: CommonDataHandler,
                 strategy: AbstractStrategy):
        """
        :param back_test_name
        :param symbol_type
        :param symbol_list:
        :param initial_capital: 
        :param start_date_str:
        :param data_handler: 
        :param strategy: 
        """
        self._portfolio_id = portfolio_id
        self._name = back_test_name
        self._description = description
        self._back_test_name = back_test_name
        self._symbol_type: SymbolTypeEnum = symbol_type
        self._symbol_list: List[str] = symbol_list
        self._initial_capital: float = initial_capital
        self._start_date_str: str = start_date_str
        self._date_format_enum = date_format_enum
        self._data_handler: CommonDataHandler = data_handler
        self._strategy: AbstractStrategy = strategy

        """
        
        """
        self._portfolio: Portfolio = Portfolio(self._portfolio_id,
                                               self._name,
                                               self._description,
                                               self._start_date_str,
                                               self._date_format_enum,
                                               self._symbol_list,
                                               self._initial_capital,
                                               is_back_test=True)
        self._execution_handler: SimulatedOrderExecuteHandler = SimulatedOrderExecuteHandler()

        self._global_events_que = queue.Queue()

        self._signals = 0
        self._orders = 0
        self._fills = 0
        self._num_strategies = 1
        self._heartbeat_time = 0.5  # 0.5s

        # map(symbol_code -> previous_processed_date_index)
        # 前一次处理的历史交易日期Index
        self._previous_trade_date_index: Dict[str, int] = {}

        self._whole_history_trade_dates: Dict[str, List[str]] = self._init_whole_history_trade_dates()

    def _init_whole_history_trade_dates(self) -> Dict[str, List[str]]:
        whole_history_trade_dates = dict([
            (symbol_code,
             sorted(self._data_handler.get_history_trade_date(symbol_code, self._start_date_str), reverse=False))
            for symbol_code in self._symbol_list
        ])

        return whole_history_trade_dates

    def _init_first_market_events(self):
        init_index = 0
        for symbol_code in self._whole_history_trade_dates.keys():
            bill_date_list = self._whole_history_trade_dates[symbol_code]
            previous_date = self._data_handler.get_previous_date(symbol_code, bill_date_list[init_index])

            self._previous_trade_date_index[symbol_code] = init_index

            self._global_events_que.put(MarketEvent(symbol_code, bill_date_list[init_index], previous_date))

    def _run_back_test(self):
        """
        Executes the backtest.
        """

        heartbeats = 0
        while True:
            """
            外层:心跳
            """
            heartbeats += 1
            print("heartbeats: %s", heartbeats)
            """
            内层:循环处理事件
            """
            # Handle the events
            while True:
                try:
                    current_event: AbstractEvent = self._global_events_que.get(False)
                except queue.Empty:
                    break
                else:
                    if current_event is None:
                        continue
                    else:
                        self._process_event(current_event)
                        # 记录前一次处理交易日Index
                        symbol_code = current_event.symbol()
                        previous_index = self._previous_trade_date_index[symbol_code]
                        # 处理完成
                        if previous_index + 1 >= len(self._whole_history_trade_dates[symbol_code]):
                            continue
                        # 发送市场信号
                        next_date = self._whole_history_trade_dates[symbol_code][previous_index + 1]
                        self._global_events_que.put(MarketEvent(symbol_code, next_date, current_event.date_str()))
                        # 更新交易日Index
                        self._previous_trade_date_index[current_event.symbol()] \
                            = self._previous_trade_date_index[current_event.symbol()] + 1

            time.sleep(self._heartbeat_time)
            self._output_performance()

    def _process_event(self, event: AbstractEvent):
        if event.event_type() == EventTypeEnum.MARKET:
            self._portfolio.update_time_index_for_market_event(event, self._data_handler)
            # 计算策略信号
            signal_event: Optional[SignalEvent] = self._strategy.calculate_signals(event)

            self._put_event_2_queue(signal_event)

        elif event.event_type() == EventTypeEnum.SIGNAL:
            self._signals += 1
            order_event: Optional[OrderEvent] = self._portfolio.generate_order_event(event)

            self._put_event_2_queue(order_event)

        elif event.event_type() == EventTypeEnum.ORDER:
            self._orders += 1
            fill_event: Optional[FillEvent] = self._execution_handler.execute_order(event)

            self._put_event_2_queue(fill_event)

        elif event.event_type() == EventTypeEnum.FILL:
            self._fills += 1
            self._portfolio.update_fill(event, self._data_handler)

    def _put_event_2_queue(self, event: AbstractEvent):
        if event is not None:
            self._global_events_que.put(event)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        statistic_summary, equity_curve = self._portfolio.statistic_summary(self._symbol_type)

        print("Creating summary stats...")
        print(statistic_summary)

        print("Creating equity curve...")
        print(equity_curve.data.tail(10))

        print("Signals: %s" % self._signals)
        print("Orders: %s" % self._orders)
        print("Fills: %s" % self._fills)

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolios performance.
        """
        self._init_first_market_events()
        self._run_back_test()
