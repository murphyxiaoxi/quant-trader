import json
import time
from datetime import datetime as datetime_type
from datetime import timedelta
from typing import List

import pandas
import requests

from data_crawler.xueqiu import get_cookies


class StockApiXueqiu(object):
    """
    雪球股票数据
    """

    def __init__(self):
        self._init_cookies_jar = get_cookies()
        self._default_indicator = ['kline']
        self._default_column = ['symbol', 'date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent']

    def get_his_k_data(
            self,
            symbol: str,
            start_date_str: str,
            end_date_str: str,
            period: str = 'day',
            return_column: List[str] = None
    ) -> pandas.DataFrame:
        """
        default kline
        all [kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance]
        :param symbol: 代码
        :param start_date_str: 起始时间 2019-03-10
        :param end_date_str: 结束时间 2019-03-20
        :param period: day week month quarter year

        :param return_column: 需要返回的列
        :return: 返回列数据
                 symbol:标的物
                 timestamp:时间戳,
                 volume:成交量(手),
                 open:开盘价
                 high:最高价
                 low:最低价
                 close:收盘价
                 chg:涨跌额
                 percent:涨跌幅度 25.0%
        """
        if return_column is None:
            return_column = ['symbol', 'date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent']
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://xueqiu.com",
            "Accept-Encoding": "br, gzip, deflate",
            "Host": "stock.xueqiu.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
            "Accept-Language": "en-us",
            "Referer": "https://xueqiu.com/S/SH510300",
            "Connection": "keep-alive"
        }

        start_of_today = datetime_type.strptime(start_date_str, "%Y-%m-%d") + timedelta(minutes=1)
        end_of_today = datetime_type.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(minutes=1)

        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?" \
              "symbol=" + symbol + \
              "&begin=" + str(int(start_of_today.timestamp() * 1000)) + \
              "&end=" + str(int(end_of_today.timestamp() * 1000)) + \
              "&period=" + period + \
              "&type=before" + \
              "&indicator=kline"

        print("request url:%s", url)
        r = requests.get(url, headers=headers, cookies=self._init_cookies_jar, timeout=30)
        result = json.loads(r.text)

        print(result)
        if result['error_code'] == 1:
            raise BaseException(result['error_description'])

        data = result['data']

        if data['symbol'] != symbol:
            raise BaseException("返回symbol与目标symbol不一致")
        column = data['column']
        df = pandas.DataFrame(data=data['item'], columns=column)
        df['symbol'] = pandas.Series(data=[symbol for i in range(df.size)])
        df['date'] = df['timestamp'].apply(lambda ts: time.strftime("%Y-%m-%d", time.localtime(int(ts / 1000))))
        df.set_index(keys=['date'], inplace=True)
        df['date'] = df.index

        return df[return_column]

    def get_k_data(
            self,
            symbol: str,
            date_str: str,
            period: str = 'day',
            return_column: List[str] = None
    ) -> pandas.DataFrame:
        """
        :param symbol: 代码
        :param date_str: 2019-05-10
        :param period: day week month quarter year
        :param return_column: 需要返回的列
        :return: 返回列数据
                 symbol:标的物
                 timestamp:时间戳,
                 volume:成交量(手),
                 open:开盘价
                 high:最高价
                 low:最低价
                 close:收盘价
                 chg:涨跌额
                 percent:涨跌幅度 25.0%
        """
        return self.get_his_k_data(symbol, date_str, date_str, period, return_column)


if __name__ == '__main__':
    etf = StockApiXueqiu()
    print(etf.get_his_k_data("SH510300", '2019-03-10', '2019-03-15'))
