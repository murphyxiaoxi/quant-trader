import datetime

from backend.commons.data_handlers.backtest_data_handler import BackTestDataHandler
from backend.commons.enums.symbol_type import SymbolTypeEnum
from backend.event_engine.back_test_engine import BackTestEngine

if __name__ == '__main__':
    print("start...")
    back_test_name = "test_1"
    symbol_code_list = []

    back_test_engine = BackTestEngine(
        back_test_name,
        SymbolTypeEnum.CHINA_STOCK,
        symbol_code_list,
        10000,
        datetime.datetime.now() + datetime.timedelta(days=-10 * 360),
        BackTestDataHandler(data_frame=None, cols_name=[]),

    )
    back_test_engine.simulate_trading()
    print("量化平台已启动, 干巴爹!")
