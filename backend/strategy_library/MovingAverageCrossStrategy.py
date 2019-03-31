from backend.commons.abstract_strategy import AbstractStrategy
from backend.commons.data_handlers.abstract_handler import CommonDataHandler
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.signal_type_enums import SignalTypeEnum
from backend.commons.events.base import SignalEvent, MarketEvent


class MovingAverageCrossAbstractStrategy(AbstractStrategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    def __init__(self, strategy_id: int, data_handler: CommonDataHandler, short_window=10, long_window=20):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        """
        super(MovingAverageCrossAbstractStrategy, self).__init__(data_handler)
        self.strategy_id = strategy_id
        self.short_window = short_window
        self.long_window = long_window

        # Set to True if a symbol is in the market
        # self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, market_event: MarketEvent) -> SignalEvent:
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.

        Parameters
        event - A MarketEvent object.
        """
        if market_event.event_type() != EventTypeEnum.MARKET:
            return None

        date: str = market_event.previous_date
        short_df = self.data_handler.get_k_data_previous(market_event.symbol(), date, self.short_window)
        long_df = self.data_handler.get_k_data_previous(market_event.symbol(), date, self.long_window)

        short_mav = short_df['close'].mean()
        long_mav = long_df['close'].mean()
        if short_mav > long_mav:
            return SignalEvent(
                market_event.symbol(),
                market_event.date_str(),
                SignalTypeEnum.UP,
                self.strategy_id,
                None
            )

        elif short_mav == long_mav:
            return SignalEvent(
                market_event.symbol(),
                market_event.date_str(),
                SignalTypeEnum.HOLD,
                self.strategy_id,
                None
            )
        else:
            return SignalEvent(
                market_event.symbol(),
                market_event.date_str(),
                SignalTypeEnum.DOWN,
                self.strategy_id,
                None
            )
