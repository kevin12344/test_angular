from datetime import datetime

def count_day_for_google_sheet(date: str) -> int | str:
    """
    google sheet 日期格式轉換(需先在該欄位設定為日期格式，否則寫入仍為數字)
    :param date: 日期
    """
    try:
        date1 = datetime.strptime(date, "%Y-%m-%d")
        date2 = datetime.strptime('1899-12-31', "%Y-%m-%d")
        delta = date1 - date2
        return delta.days + 1
    except Exception as e:
        return ''
    

def gs_url_change(gs_url) -> str:
    """
    統一轉換Google Sheet網址格式
    :param gs_url: Google Sheet網址
    """
    gs_url_split: list = gs_url.split('/')
    gs_url_split.pop()
    return '/'.join(gs_url_split)

if __name__ == '__main__':
    print(gs_url_change('https://docs.google.com/spreadsheets/d/14kRyrny6deOfYUGbsjnLZUzXRrt2hvaF2GpgDaF0R7s/edit?gid=487771632#gid=487771632'))