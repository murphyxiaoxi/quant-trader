#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue
import time
from typing import List

from backend.backtest.datahandler import DataHandler
from backend.backtest.execution import ExecutionHandler
from backend.backtest.portfolio import Portfolio
from backend.backtest.strategy import Strategy


class BackTest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
            self,
            symbol_list: List[str],
            initial_capital: float,
            heartbeat: int,
            start_date: str,
            data_handler_cls: DataHandler.__class__,
            execution_handler_cls: ExecutionHandler.__class__,
            portfolio_cls: Portfolio.__class__,
            strategy_cls: Strategy.__class__
    ):
        """
        Initialises the backtest.

        Parameters:
        csv_dir - The hard root to the CSV data directory.
        symbol_list - The list of symbol strings.
        intial_capital - The starting capital for the portfolio.
        heartbeat - Backtest "heartbeat" in seconds
        start_date - The start datetime of the strategy.
        data_handler - (Class) Handles the market data feed.
        execution_handler - (Class) Handles the orders/fills for trades.
        portfolio - (Class) Keeps track of portfolio current and prior positions.
        strategy - (Class) Generates signals based on market data.
        """
        self.symbol_list: List[str] = symbol_list
        self.initial_capital: float = initial_capital
        self.heartbeat: int = heartbeat
        self.start_date: str = start_date

        self.data_handler_cls: DataHandler.__class__ = data_handler_cls
        self.execution_handler_cls: ExecutionHandler.__class__ = execution_handler_cls
        self.portfolio_cls: Portfolio.__class__ = portfolio_cls
        self.strategy_cls: Strategy.__class__ = strategy_cls

        self.events_que = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from
        their class types.
        """
        print(
            "Creating DataHandler, Strategy, Portfolio and ExecutionHandler"
        )
        self.data_handler = self.data_handler_cls(self.events_que, self.symbol_list)
        self.strategy = self.strategy_cls(self.data_handler, self.events_que)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events_que, self.start_date,
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events_que)

    def _run_backtest(self):
        """
        Executes the backtest.
        """
        i = 0
        while True:
            i += 1
            print(i)
            # Update the market bars
            if self.data_handler.continue_backtest == True:
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
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_time_index(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == 'FILL':
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
        self._run_backtest()
        self._output_performance()
