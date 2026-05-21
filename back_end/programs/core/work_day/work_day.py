from datetime import datetime, timedelta

def next_working_day(date: datetime, day: int = 1) -> datetime:
    """
    取得指定日期的1~N天工作日，回傳 datetime 物件
    :param date: 指定日期
    :param day: 工作日數
    """
    next_day = date + timedelta(days=day)
    while next_day.weekday() in [5, 6]:
        next_day += timedelta(days=1)
    return next_day

if __name__ == "__main__":
    test_date_str = "2025/02/21"
    test_date = datetime.strptime(test_date_str, "%Y/%m/%d")

    # 計算下一個工作日
    next_workday = next_working_day(test_date)
    
    # 格式化輸出
    print("今天:", test_date.strftime("%Y/%m/%d"))
    print("下一個工作日:", next_workday.strftime("%Y/%m/%d"))
