from pymongo import MongoClient


class MongoBase:
    def __init__(self, db_name, table_name):
        self._db_name = db_name
        self._table_name = table_name
        self._open_table()

    def _open_table(self, ):
        user_name = ''
        pass_word = ''
        host = '127.0.0.1'
        port = '27017'

        # uri = "mongodb://" + user_name + ":" + pass_word + "@" + host + ":" + port + "/" + self._db_name
        uri = "mongodb://" + host + ":" + port + "/" + self._db_name
        self._con = MongoClient(uri, connect=True)
        self._db = self._con[self._db_name]
        self.table = self._db[self._table_name]

    def close(self):
        self._con.close()


