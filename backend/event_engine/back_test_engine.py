#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue
import time
from typing import List

from backend.commons.abstract_strategy import AbstractStrategy
from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.events.base import AbstractEvent
from backend.commons.order_execution.order_execute_handler import AbstractOrderExecuteHandler, \
    SimulatedOrderExecuteHandler
from backend.commons.portfolios.base import Portfolio


class BackTestEngine(object):
    # todo 完善
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(self, symbol_list: List[str], initial_capital: float, start_date: str,
                 data_handler: CommonDataHandler, strategy: AbstractStrategy):
        self.symbol_list: List[str] = symbol_list
        self.initial_capital: float = initial_capital
        self.start_date: str = start_date
        self.data_handler: CommonDataHandler = data_handler
        self.strategy: AbstractStrategy = strategy

        # self init property
        self.portfolio: Portfolio = Portfolio()
        self.execution_handler: SimulatedOrderExecuteHandler = SimulatedOrderExecuteHandler()

        self.global_events_que = queue.Queue()
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strategies = 1
        self.processed_date_set = set()
        self._heartbeat_time = 0.05  # 0.05s

    def _run_back_test(self):
        """
        Executes the backtest.
        """
        heartbeats = 0
        while True:
            heartbeats += 1
            print("heartbeats: %s", heartbeats)
            # Update the market bars
            if self.data_handler.continue_back_test():
                self.data_handler.update_bars()
            else:
                break

            # Handle the events
            while True:
                try:
                    event: AbstractEvent = self.global_events_que.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.event_type() == EventTypeEnum.MARKET:
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_time_index(event)

                        elif event.event_type() == EventTypeEnum.SIGNAL:
                            self.signals += 1
                            self.portfolio.update_signal(event)

                        elif event.event_type() == EventTypeEnum.ORDER:
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.event_type() == EventTypeEnum.FILL:
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self._heartbeat_time)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        self.portfolio.create_equity_curve_data_frame()

        print("Creating summary stats...")
        stats = self.portfolio.output_summary_stats()

        print("Creating equity curve...")
        print(self.portfolio.equity_curve.tail(10))
        print(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolios performance.
        """
        self._run_back_test()
        self._output_performance()
