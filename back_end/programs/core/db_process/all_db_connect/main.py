import os
from programs.core.sql_connect import mssql
from dotenv import load_dotenv

load_dotenv()


# XINTEA DB
class XinTeaSql(mssql.MsSqlConnect):
    def __init__(self):
        super(XinTeaSql, self).__init__(server=os.getenv('DB_HOST'), user=os.getenv('DB_ACCOUNT'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'))
"""
#測試用 DB
class XinTeaSql(mssql.MsSqlConnect):
    def __init__(self):
        super(XinTeaSql, self).__init__(server=os.getenv('DB_HOST'), user=os.getenv('DB_ACCOUNT'), password=os.getenv('DB_PASSWORD'), database=os.getenv('TEST_DB_NAME'))
"""

# JWCOMMON DB
class JwCommonSql(mssql.MsSqlConnect):
    def __init__(self):
        super(JwCommonSql, self).__init__(server=os.getenv('DB_HOST'), user=os.getenv('DB_ACCOUNT'), password=os.getenv('DB_PASSWORD'), database=os.getenv('COMMON_DB'))