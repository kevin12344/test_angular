import datetime


def eip_employee(eip_emp: str) -> str:
    """
    員工資料格式處理
    :param eip_emp: str 員工資料
    """
    if len(eip_emp) == 0:
        return ''
    return eip_emp.replace('[', '').split('(')[0]


def timestamp_to_neo(ts: str):
    """
    EIP時間戳記轉成NEO日期格式
    :param ts: 時間戳記
    """
    if len(ts) == 0:
        return ''
    ts = int(ts)
    try:
        time_array = datetime.datetime.fromtimestamp(ts)
    except (OSError, ValueError):
        ts = ts / 1000
        time_array = datetime.datetime.fromtimestamp(ts)
    return time_array.strftime('%Y%m%d')


def date_format_to_neo(date_str: str, symbol: str) -> str:
    """
    將標準日期格式轉換為NEO需求
    :param date_str: str 日期字串
    :param symbol: str 符號
    """
    if len(date_str) == 0 or len(symbol) == 0:
        return ''
    date_cut = date_str.split(symbol)
    year = ''
    month = ''
    day = ''
    if len(date_cut) > 2:
        # 年
        if int(date_cut[0]) < 1900:
            year = str(int(date_cut[0]) + 1911)
        else:
            year = str(date_cut[0])
        # 月
        month = str('0' + str(date_cut[1]))[-2:]
        # 日
        day = str('0' + str(date_cut[2]))[-2:]
    return year + month + day


def date_format_from_neo(neo_date: str, symbol='-') -> str:
    """
    NEO日期格式，依需求轉換
    :param neo_date: str NEO格式日期
    :param symbol: str 符號
    """
    if len(neo_date) > 0:
        year = neo_date[0:4]
        month = neo_date[4:6]
        day = neo_date[6:8]
        date_str = symbol.join([year, month, day])
        return date_str
    return ''


def string_too_long(string: str, num: int, symbol='\n') -> str:
    """
    字串過長處理
    :param string: str 處理字串
    :param num: str 字串每行最大長度
    :param symbol: str 區隔符號
    """
    string_list: list = []
    if len(string) > num:
        for i in range(0, int(len(string) / num)+1):
            if len(string) > num:
                string_list.append(string[0:num])
                string = string.replace(string[0:num], ' ', 1)
            else:
                string_list.append(string[0: len(string)])
        return symbol.join(string_list)
    return string


def string_int_to_formatted(math: int) -> str:
    """
    數字轉換為格式化字串
    :param math: int 數字
    """
    if len(str(math)) == 0:
        return ''
    return '{:,}'.format(math)

def is_un_jquery_format(is_download: str, un_download: str) -> dict:
    """
    處理是否jquery(用於下載功能)
    :param is_download: 是否值
    :param un_download: 否值
    """
    if is_download == 'true':
        is_download = '1'
    else:
        is_download = '0'
    if un_download == 'true':
        un_download = '1'
    else:
        un_download = '0'
    return {'is_download': is_download, 'un_download': un_download}


def convert_to_minguo(date_str, symbol='/'):
    if date_str:
        # 嘗試不同的日期格式
        for fmt in [f"%Y{symbol}%m{symbol}%d", "%Y-%m-%d"]:
            try:
                date_obj = datetime.datetime.strptime(date_str, fmt)
                minguo_year = date_obj.year - 1911
                return f"{minguo_year:03d}{date_obj.strftime('%m%d')}"
            except ValueError:
                continue
        # 如果所有格式都不匹配，拋出異常
        raise ValueError(f"日期格式不匹配: {date_str}")
    return ''


def date_time_to_timestamp(date_str: str) -> int:
    """
    日期時間轉時間戳記（13碼毫秒）
    :param date_str: str 日期時間字串，格式：'YYYY-MM-DD'
    """
    if not date_str:
        return 0
    try:
        time_array = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        timestamp = int(time_array.timestamp() * 1000)
        return timestamp
    except ValueError:
        return 0


if __name__ == '__main__':
    print(date_format_to_neo('2023-03-24', '-'))