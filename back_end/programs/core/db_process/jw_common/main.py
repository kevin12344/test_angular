from programs.core.db_process.all_db_connect.main import JwCommonSql
from datetime import datetime


def qry_employee(employee_id: str) -> dict | None:
    try:
        db = JwCommonSql()
        result = db.s_qry("SELECT employee_id, employee_name, id FROM employee WHERE employee_id = ?", employee_id)
        return result[0] if result else None
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return None

def qry_currency(currency: str) -> list:
    """
    查詢匯率(現在日期)
    :param currency: 匯率代碼
    """
    msq = JwCommonSql()
    cmd: str = """SELECT * FROM historical_exchange_rate_closing_price
                  WHERE currency = ? and update_date = ?"""
    return msq.s_qry(cmd, currency, datetime.now().strftime('%Y-%m-%d'))


def qry_is_holiday(date: str) -> bool:
    """
    查詢日期是否為假日
    :param date: 日期
    """
    msq = JwCommonSql()
    cmd: str = """SELECT * FROM taiwan_holiday WHERE date = ?"""
    return msq.s_qry(cmd, date)


if __name__ == '__main__':
    print(qry_currency('USD'))