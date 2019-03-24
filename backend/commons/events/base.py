from datetime import datetime
from backend.commons.enums import order_type_enums
from backend.commons.enums.event_type_enums import EventTypeEnum
from backend.commons.enums.order_type_enums import OrderTypeEnum
from backend.commons.enums.signal_type_enums import SignalTypeEnum


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """

    def __init__(self, event_type: EventTypeEnum):
        self.event_type = event_type


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        super().__init__(EventTypeEnum.MARKET)


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, strategy_id: int, symbol: str, date_time: datetime, signal_type: SignalTypeEnum, strength):
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
        super().__init__(EventTypeEnum.SIGNAL)
        self.strategy_id: int = strategy_id
        self.symbol: str = symbol
        self.date_time: datetime = date_time
        self.signal_type: SignalTypeEnum = signal_type
        self.strength = strength


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol: str, order_type: OrderTypeEnum, quantity: int,
                 direction: order_type_enums.DirectionTypeEnum):
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
        super().__init__(EventTypeEnum.ORDER)
        self.symbol: str = symbol
        self.order_type: OrderTypeEnum = order_type
        self.quantity: int = quantity
        self.direction: order_type_enums.DirectionTypeEnum = direction

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
            (self.symbol, self.order_type, self.quantity, self.direction)
        )


class FillEvent(Event):
    """
    下单事件
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """

    def __init__(self, time_index: datetime, symbol: str, exchange: str, quantity,
                 direction: order_type_enums.DirectionTypeEnum, fill_cost: float):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        :param time_index: - The bar-resolution when the order was filled.
        :param symbol - The instrument which was filled.
        :param exchange - The exchange where the order was filled. 交易所
        :param quantity - The filled quantity. 数量
        :param direction - The direction of fill ('BUY' or 'SELL')
        :param fill_cost - The holdings value in dollars. 消费金额
        """
        super().__init__(EventTypeEnum.FILL)
        self.time_index: datetime = time_index
        self.symbol: str = symbol
        self.exchange: str = exchange
        self.quantity: int = quantity
        self.direction: order_type_enums.DirectionTypeEnum = direction
        self.fill_cost: float = fill_cost