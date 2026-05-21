from urllib.parse import quote
from sqlalchemy import create_engine, text
from sqlalchemy.sql import select


def test():
    password = quote("dsc@01020314")
    engine = create_engine(f"mssql+pymssql://sa:{password}@172.16.10.1/JWEIPDB", echo=True, pool_size=10)

    conn = engine.connect()

    cmd = text('SELECT * FROM EIPTONEORESULT')

    result = conn.execute(cmd)
    print(result)
    return result



if __name__ == '__main__':
    test()