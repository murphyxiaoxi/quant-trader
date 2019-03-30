from backend.commons.data_handlers.backtest_data_handler import BackTestDataHandler
from backend.commons.enums.date_format_enums import DateFormatStrEnum
from backend.commons.enums.symbol_type import SymbolTypeEnum
from backend.event_engine.back_test_engine import BackTestEngine
from backend.strategy_library.MovingAverageCrossStrategy import MovingAverageCrossAbstractStrategy

if __name__ == '__main__':
    print("start...")

    portfolio_id = 1
    back_test_name = "test"
    description = "description"
    symbol_type = SymbolTypeEnum.CHINA_STOCK
    symbol_list = ['SH510300']
    initial_capital = 1000.0
    start_date_str = '2015-10-10'
    date_format_enum = DateFormatStrEnum.DAY_BASE
    data_handler = BackTestDataHandler(SymbolTypeEnum.CHINA_STOCK, [])
    strategy = MovingAverageCrossAbstractStrategy(1, data_handler, short_window=5, long_window=10)

    back_test_engine = BackTestEngine(
        portfolio_id,
        back_test_name,
        description,
        symbol_type,
        symbol_list,
        initial_capital,
        start_date_str,
        date_format_enum,
        data_handler,
        strategy
    )
    back_test_engine.simulate_trading()
    print("回测已完成, 干巴爹!")
