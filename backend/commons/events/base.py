from abc import ABCMeta
from datetime import datetime

from backend.commons.enums import order_type_enums
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.order_type_enums import OrderTypeEnum, DirectionTypeEnum
from backend.commons.enums.signal_type_enums import SignalTypeEnum


class AbstractEvent(metaclass=ABCMeta):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """

    def __init__(self, symbol_code: str, date_time: datetime, event_type: EventTypeEnum):
        self._symbol_code = symbol_code
        self._date_time = date_time
        self._event_type = event_type

    def symbol_code(self):
        return self._symbol_code

    def event_type(self):
        return self._event_type

    def date_time(self):
        return self._date_time

    def __str__(self) -> str:
        return "AbstractEvent(symbol_code=%s, date_time=%s, event_type=%s)" \
               % (self.symbol_code(), self.date_time(), self.event_type())


class MarketEvent(AbstractEvent):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self, symbol_code: str, date_time: datetime, previous_date_time: datetime):
        """
        Initialises the MarketEvent.
        """
        super().__init__(symbol_code, date_time, EventTypeEnum.MARKET)
        self.previous_date_time = previous_date_time

    def __str__(self) -> str:
        return "MarketEvent(symbol_code=%s, date_time=%s, event_type=%s, previous_date_time=%s)" \
               % (self.symbol_code(), self.date_time(), self.event_type(), self.previous_date_time)


class SignalEvent(AbstractEvent):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, symbol_code: str, date_time: datetime, signal_type: SignalTypeEnum, strategy_id: int, strength):
        """
        Initialises the SignalEvent.

        Parameters:
        strategy_id - The unique ID of the strategy sending the signal.
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT'.
        strength - An adjustment factor "suggestion" used to scale
            quantity at the portfolios level. Useful for pairs strategies.
        """
        super().__init__(symbol_code, date_time, EventTypeEnum.MARKET)
        self.strategy_id: int = strategy_id
        self.signal_type: SignalTypeEnum = signal_type
        self.strength = strength

    def __str__(self) -> str:
        return "SignalEvent(symbol_code=%s, date_time=%s, event_type=%s, signal_type=%s, strategy_id=%s,strength=%s)" \
               % (self.symbol_code(), self.date_time(), self.event_type(), self.signal_type, self.strategy_id,
                  self.strength)


class OrderEvent(AbstractEvent):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol_code: str, date_time: datetime, order_type: OrderTypeEnum, quantity: int,
                 direction_type: DirectionTypeEnum):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        TODO: Must handle error checking here to obtain
        rational orders (i.e. no negative quantities etc).

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        super().__init__(symbol_code, date_time, EventTypeEnum.MARKET)
        self.order_type: OrderTypeEnum = order_type
        self.quantity: int = quantity
        self.direction_type: order_type_enums.DirectionTypeEnum = direction_type

    def __str__(self) -> str:
        return "SignalEvent(symbol_code=%s, date_time=%s, event_type=%s, order_type=%s, quantity=%s" \
               ",direction_type=%s)" \
               % (self.symbol_code(), self.date_time(), self.event_type(), self.order_type, self.quantity,
                  self.direction_type)


class FillEvent(AbstractEvent):
    """
    填充事件
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """

    def __init__(self,
                 symbol_code: str,
                 date_time: datetime,
                 quantity: int,
                 direction_type: order_type_enums.DirectionTypeEnum,
                 fill_cost: float,
                 commission: float,
                 exchanger: str):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        :param date_time: - The bar-resolution when the order was filled.
        :param symbol_code - The instrument which was filled.
        :param quantity - The filled quantity. 数量
        :param direction_type - The direction of fill ('BUY' or 'SELL')
        :param fill_cost - The holdings value in dollars. 消费金额
        :param commission 佣金
        :param exchanger - The exchange where the order was filled. 交易所名称
        """
        super().__init__(symbol_code, date_time, EventTypeEnum.FILL)
        self.quantity: int = quantity
        self.direction_type: order_type_enums.DirectionTypeEnum = direction_type
        self.fill_cost: float = fill_cost
        self.commission: float = commission
        self.exchanger: str = exchanger

    def __str__(self) -> str:
        return "SignalEvent(symbol_code=%s, date_time=%s, event_type=%s, quantity=%s, direction_type=%s" \
               ",fill_cost=%s, commission=%s, exchanger=%s)" \
               % (self.symbol_code(), self.date_time(), self.event_type(), self.quantity, self.direction_type,
                  self.fill_cost, self.commission, self.exchanger)
