from datetime import datetime
from dateutil.parser import parse
import time

def time_mark():
    # 時間戳記
    ts = datetime.today().timestamp()
    return str(ts)


def today(symbol='/'):
    """
    今天日期
    :param symbol: str 符號
    """
    today_dt = datetime.now()
    return today_dt.strftime('%Y{0}%m{0}%d'.format(symbol))


def neo_today():
    # 今天日期 - neo格式
    today_dt = datetime.now()
    return today_dt.strftime('%Y%m%d')


def timestamp_today():
    # 現在時間轉成13位時間戳記(瑞研BPM用)
    today_dt = datetime.now()
    timestamp = int(time.mktime(today_dt.timetuple()) * 1000 + today_dt.microsecond / 1000)
    return timestamp

def date_to_timestamp(date_str):
    # 將日期字符串轉換為 datetime 對象
    dt = parse(date_str)
    # 將 datetime 對象轉換為13位的時間戳
    timestamp = int(time.mktime(dt.timetuple()) * 1000)
    return timestamp


if __name__ == '__main__':
    print(date_to_timestamp('2024/04/25'))