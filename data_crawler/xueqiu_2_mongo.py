import json
import typing
from typing import List

import pandas
import pymongo

from dao.mongo import MongoBase
from data_crawler.xueqiu.online_api import StockApiXueqiu


class StockXueqiuData:
    def __init__(self):
        self._mongo = MongoBase("stock", "xueqiu")
        self._online_api = StockApiXueqiu()
        self._default_columns = ['symbol', 'date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent']

    def get_his_k_data(
            self,
            symbol: str,
            start_date_str: str,
            end_date_str: str,
            force_update: bool = False,
            return_columns: List[str] = None
    ) -> pandas.DataFrame:
        """
        获取历史数据
        默认从mongo里查询数据, 不存在的数据则从需求爬取然后存入mongo
        :param symbol:
        :param start_date_str:
        :param end_date_str:
        :param force_update: 强制更新 默认False
        :param return_columns: default ['symbol', 'date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent']
        :return:

        """
        if return_columns is None:
            return_columns = self._default_columns

        if force_update:
            tmp_df = self._online_api.get_his_k_data(symbol, start_date_str, end_date_str)
            data_list = json.loads(tmp_df.to_json(orient='records'))
            for record in data_list:
                self._mongo.table.update({"symbol": record['symbol'], "date": record['date']}, {"$set": record},
                                         upsert=True)
            return tmp_df

        if start_date_str is None:
            start_date_str = ""
        if end_date_str is None:
            end_date_str = ""

        cursor = self._mongo.table.find(filter={
            "symbol": symbol,
            "date": {"$gte": start_date_str, "$lte": end_date_str}
        }, projection={"_id": False}).sort('date', pymongo.ASCENDING)

        records = [item for item in cursor]

        parsed_data = [self._parse(record, return_columns) for record in records]
        result_df = pandas.DataFrame(data=parsed_data, columns=return_columns)
        result_df.set_index(['date'], inplace=True)
        return result_df.sort_index(ascending=True)

    @staticmethod
    def _parse(
            dict_obj: typing.Dict,
            return_column: List[str]
    ) -> List[typing.Any]:

        def get(dict_job, k):
            if k in dict_job:
                return dict_obj[k]
            else:
                return None

        return [get(dict_obj, k) for k in return_column]


# dicts = {'one': [1, 2, 3], 'two': [2, 3, 4], 'three': [3, 4, 5]}
# df = pd.DataFrame(dicts)
# mongo.table.insert(json.loads(df.to_json(orient='records')))
if __name__ == '__main__':
    stock = StockXueqiuData()
    df = stock.get_his_k_data("SH510300", '2000-01-01', '2019-03-15', force_update=False)
    print(df)
