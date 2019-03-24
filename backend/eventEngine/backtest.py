#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue
import time
from typing import List

from backend.backtest.datahandler import DataHandler
from backend.enums import EventTypeEnum
from backend.backtest.event import Event
from backend.backtest.execution import ExecutionHandler
from backend.backtest.portfolio import Portfolio
from backend.backtest.strategies.strategy import Strategy


class BackTestEngine(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
            self,
            event_queue: queue.Queue[Event],
            symbol_list: List[str],
            initial_capital: float,
            start_date: str,
            data_handler: DataHandler,
            execution_handler: ExecutionHandler,
            portfolio: Portfolio,
            strategy: Strategy,
            heartbeat: int = 1,
    ):
        """

        :param event_queue:
        :param symbol_list:
        :param initial_capital:
        :param start_date: 2019-10-23
        :param data_handler:
        :param execution_handler:
        :param portfolio:
        :param strategy:
        :param heartbeat:
        """
        self.events_que = event_queue
        self.symbol_list: List[str] = symbol_list
        self.initial_capital: float = initial_capital
        self.heartbeat: int = heartbeat
        self.start_date: str = start_date

        self.data_handler: DataHandler = data_handler
        self.execution_handler: ExecutionHandler = execution_handler
        self.portfolio: Portfolio = portfolio
        self.strategy: Strategy = strategy

        self.events_que = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strategies = 1

    def _run_back_test(self):
        """
        Executes the backtest.
        """
        i = 0
        while True:
            i += 1
            print(i)
            # Update the market bars
            if self.data_handler.continue_back_test():
                self.data_handler.update_bars()
            else:
                break

            # Handle the events
            while True:
                try:
                    event = self.events_que.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == EventTypeEnum.MARKET:
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_time_index(event)

                        elif event.type == EventTypeEnum.SIGNAL:
                            self.signals += 1
                            self.portfolio.update_signal(event)

                        elif event.type == EventTypeEnum.ORDER:
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == EventTypeEnum.FILL:
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

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
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_back_test()
        self._output_performance()
