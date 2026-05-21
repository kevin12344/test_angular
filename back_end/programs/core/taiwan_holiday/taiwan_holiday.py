import requests
from datetime import datetime

def get_day_is_holiday(year: str):
    """
    取得某年的假日
    :param year: 西元年
    """
    r = requests.get(f"https://cdn.jsdelivr.net/gh/ruyut/TaiwanCalendar/data/{year}.json")
    data = [
        event for event in r.json()
        if event.get('isHoliday', False) is True
        #    and datetime.strptime(event.get('date'), "%Y%m%d").weekday() != 6
    ]
    return data

if __name__ == '__main__':
    from programs.core.db_process.all_db_connect.main import JwCommonSql
    data = get_day_is_holiday("2025")
    add_param: list = []
    for per_data in data:
        add_param.append(
            (
                per_data.get('date'), per_data.get('week'), per_data.get('description')
                
            )
        )
    msq = JwCommonSql()
    cmd = """INSERT INTO taiwan_holiday (date, week, description) VALUES (?, ?, ?)"""
    cmds_param: list = [
        (cmd, add_param)
    ]
    msq.transaction_v2(cmds_param)