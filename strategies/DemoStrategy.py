from core.common.event import MarketEvent, OrderEvent, OrderTypeEnum
from core.common.strategyTemplate import StrategyTemplate
from core.engine.main_engine import MainEngine


class DemoStrategy(StrategyTemplate):
    def __init__(self):
        super(DemoStrategy, self).__init__(['510030'], 10000.0, back_test=True, start_date='20190101',
                                           end_date='20190404')

    def init(self):
        pass

    def id(self):
        return "1"

    def name(self):
        return "demo1"

    def description(self):
        return "调试用"

    def market_data_func(self, current_date: str):
        # self.stock_api.get_his_k_data()
        data = {'510030': 1}
        return data

    def strategy(self, event: MarketEvent) -> OrderEvent:
        print("市场信号:", event)

        price = event.data['510030']

        if self.portfolio.latest_holding() is None:
            cash = self.portfolio.init_capital
        else:
            cash = self.portfolio.latest_holding()['cash']

        quantity = int(cash / price)

        direction = {'510030': OrderTypeEnum.BUY}
        quantity = {'510030': quantity}
        price = {'510030': price}

        return OrderEvent(event.current_date, direction, quantity, price, 0.0)


if __name__ == '__main__':
    main_engine = MainEngine(DemoStrategy())
    main_engine.start()
