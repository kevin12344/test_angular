from datetime import datetime, date

def weekly_change(goal_date: str, start_date: str) -> int:
    """
    周別轉換
    :param goal_date: str 目標日期 (格式: 'YYYY/MM/DD')
    :param start_date: str 起始日期 (格式: 'YYYY/MM/DD')
    :return: int 週數（有剩餘天數會進位）
    """
    # 將字串轉換為 date 物件
    # 分割日期字串並轉換為整數
    print(goal_date, start_date)
    try:
        year_s, month_s, day_s = map(int, start_date.split('/'))
        year_g, month_g, day_g = map(int, goal_date.split('/'))
        
        # 建立 date 物件
        start = date(year_s, month_s, day_s)
        target = date(year_g, month_g, day_g)
        
        # 計算天數差異
        days_difference = (target - start).days
        
        # 計算週數（如果有剩餘天數就進位）
        weeks = (days_difference + 6) // 7  # 加 6 是為了向上進位
        
        return weeks
    except:
        return 0
    
if __name__ == '__main__':
    pass