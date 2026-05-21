import pyodbc


class MsSqlConnect:
    def __init__(self, server, user, password, database, **kwargs):
        con_str = 'SERVER={server};DATABASE={database};UID={username};PWD={password}'
        con_str = 'DRIVER={ODBC Driver 17 for SQL Server};' + con_str.format(server=server, username=user, password=password, database=database)
        self.conn = pyodbc.connect(con_str)
        self.cursor = self.conn.cursor()

    def qry(self, cmd, *params) -> list:
        return_data = self.as_dict(self.cursor.execute(cmd, *params))
        return return_data

    def do(self, cmd, *params) -> int:
        self.cursor.execute(cmd, *params)
        self.conn.commit()
        return self.cursor.rowcount

    def close(self):
        self.conn.close()

    def s_qry(self, cmd, *params) -> list:
        result = self.qry(cmd, *params)
        self.close()
        return result

    def s_do(self, cmd, *params):
        count = self.do(cmd, *params)
        self.close()
        return count
    
    def transaction(self, cmd: str, params: list) -> bool:
        try:
            self.cursor.executemany(cmd, params)
            self.cursor.commit()
            return True
        except Exception as e:
            print(f"Error executing transaction: {e}")
            self.cursor.rollback()
            return False
        finally:
            self.close()
            
    def transaction_v2(self, cmds_params: list) -> bool:
        try:
            for cmd, params in cmds_params:
                print(f"Executing: {cmd} with params: {params}")
                self.cursor.executemany(cmd, params)
            self.conn.commit()
            print("Transaction committed successfully")
            return True
        except Exception as e:
            print(f"Error executing transaction: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()

    @staticmethod
    def as_dict(output_data) -> list:
        result_data = []
        columns = [column[0] for column in output_data.description]
        for row in output_data.fetchall():
            result_data.append(dict(zip(columns, row)))
        for row in result_data:
            row: dict
            for key in row.keys():
                if type(row[key]) is str:
                    row[key] = str(row[key]).strip()
        return result_data