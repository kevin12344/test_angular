import sqlite3


class Sqlite3Connect(object):
    def __init__(self, db_dir):
        self.conn = sqlite3.connect(db_dir)
        self.conn.row_factory = self._dict_factory
        self.cursor = self.conn.cursor()

    def qry(self, cmd) -> list:
        cursor = self.conn.cursor()
        data = cursor.execute(cmd)
        data = data.fetchall()
        data = self._strip_all_value(data)
        return data

    def do(self, cmd):
        cur = self.conn.cursor()
        sql = self.cursor.execute(cmd)
        self.conn.commit()

    # 靜態方法：將回傳轉換為dict模式
    @staticmethod
    def _dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @staticmethod
    def _strip_all_value(data: list) -> list:
        for dic in data:
            dic: dict
            for key in dic.keys():
                if type(dic[key]) is str:
                    dic[key] = dic[key].strip()
        return data
