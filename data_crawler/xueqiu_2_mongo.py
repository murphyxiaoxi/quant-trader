import pandas

from data_crawler.mongo import MongoBase
import requests
import pandas as pd
import json
from data_crawler.xueqiu.online_api import StockApiXueqiu


class XueqiuStockData:
    def __init__(self):
        self._mongo = MongoBase("stock", "xueqiu")
        self._online_api = StockApiXueqiu()

    def get_his_k_data(self,
                       symbol: str,
                       start_date_str: str,
                       end_date: str) -> pandas.DataFrame:
        """
        默认从mongo里查询数据, 不存在的数据则从需求爬取然后存入mongo
        :param symbol:
        :param start_date_str:
        :param end_date:
        :param from_mongo:
        :return:
        """
        self._mongo.table.find()

# dicts = {'one': [1, 2, 3], 'two': [2, 3, 4], 'three': [3, 4, 5]}
# df = pd.DataFrame(dicts)
# mongo.table.insert(json.loads(df.to_json(orient='records')))
# print(mongo.table.find_one())
