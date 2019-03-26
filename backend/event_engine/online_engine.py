#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import queue
import time
from typing import List, Dict, Optional, Set

import pandas

from backend.commons.abstract_strategy import AbstractStrategy
from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.symbol_type import SymbolTypeEnum
from backend.commons.events.base import MarketEvent, AbstractEvent, OrderEvent, SignalEvent, FillEvent
from backend.commons.order_execution.order_execute_handler import SimulatedOrderExecuteHandler
from backend.commons.portfolios.base import Portfolio


class OnlineEngine(object):
    """
    事件驱动型交易系统
    process_pipeline:
    EventEngine:MarketEvent => DataHandler:Data =>
    Strategy:SignalEvent => Portfolio:OrderEvent =>
    OrderExecuteHandler:FillEvent => Portfolio
    """

    def __init__(self, back_test_name, symbol_type: SymbolTypeEnum, symbol_code_list: List[str], initial_capital: float,
                 start_date: datetime.datetime, data_handler: CommonDataHandler, strategy: AbstractStrategy):
        """
        :param back_test_name
        :param symbol_type
        :param symbol_code_list:
        :param initial_capital:
        :param start_date:
        :param data_handler:
        :param strategy:
        """
        self._back_test_name = back_test_name
        self._symbol_type: SymbolTypeEnum = symbol_type
        self._symbol_code_list: List[str] = symbol_code_list
        self._initial_capital: float = initial_capital
        self._start_date: datetime = start_date
        self._data_handler: CommonDataHandler = data_handler
        self._strategy: AbstractStrategy = strategy

        """

        """
        self._portfolio: Portfolio = Portfolio(self._start_date, self._symbol_code_list,
                                               self._initial_capital)
        self._execution_handler: SimulatedOrderExecuteHandler = SimulatedOrderExecuteHandler()

        self._global_events_que = queue.Queue()

        self._signals = 0
        self._orders = 0
        self._fills = 0
        self._num_strategies = 1
        self._heartbeat_time = 60 * 60  # 1h

        # map(symbol_code -> previous_processed_date_index)
        # 前一次处理的历史交易日期Index
        self._processed_trade_date_time: Dict[str, Set[datetime]] = dict(
            [(symbol_code, set())
             for symbol_code in self._symbol_code_list]
        )

        self._previous_trade_date_time: Dict[str, datetime] = dict(
            [(symbol_code, None)
             for symbol_code in self._symbol_code_list]
        )

    @staticmethod
    def _convert_to_seventeen_clock(current_date_time: datetime.datetime) -> datetime.datetime:
        """
        把时间转化为当天17点整
        :param current_date_time:
        :return: datetime
        """
        date_str = current_date_time.strftime("%Y-%m-%d")
        return datetime.datetime.strptime("%s %s" % (date_str.strip(), "17:00:00"), "%Y-%m-%d %H:%M:%S")

    def _run_back_test(self):
        """
        Executes the backtest.
        """

        heartbeats = 0
        while True:
            """
            外层:心跳
            """
            # 生成市场事件
            for symbol_code in self._symbol_code_list:
                now = datetime.datetime.now()
                current_date_time = self._convert_to_seventeen_clock(now)
                if current_date_time not in self._processed_trade_date_time[symbol_code]:
                    continue
                self._put_event_2_queue(
                    MarketEvent(symbol_code, current_date_time, self._previous_trade_date_time[symbol_code])
                )
                self._previous_trade_date_time[symbol_code] = current_date_time
                self._processed_trade_date_time[symbol_code].add(current_date_time)

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

            time.sleep(self._heartbeat_time)
            self._output_performance()

    def _process_event(self, event: AbstractEvent):
        if event.event_type() == EventTypeEnum.MARKET:
            self._portfolio.update_time_index_for_market_event(event, self._data_handler)
            # 计算策略信号
            features: pandas.DataFrame = self._data_handler.get_features(event.symbol_code(), event.date_time())
            signal_event: Optional[SignalEvent] = self._strategy.calculate_signals(features, event)

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
        self._run_back_test()
