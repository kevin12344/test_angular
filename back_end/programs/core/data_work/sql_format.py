

def is_un_format(field: str, is_value: str, un_value: str) -> str:
    """
    處理是否sql(用於下載功能)
    :param field: 欄位名稱
    :param is_value: 是否值
    :param un_value: 否值
    """
    param_sql: str = ''
    if is_value == '1' and un_value == '1':
        param_sql = f"and ({field} = '{is_value}' or {field} is NULL)"
    if is_value == '1' and un_value == '0':
        param_sql = f"and {field} = '{is_value}'"
    if is_value == '0' and un_value == '1':
        param_sql = f"and {field} is NULL"
    if is_value == '0' and un_value == '0':
        param_sql = f"and {field} = '0'"
    return param_sql

def is_un_format_for_subsidy(field: str, is_value: str, un_value: str) -> str:
    """
    處理是否sql(用於補助查詢功能)
    :param field: 欄位名稱
    :param is_value: 是否值
    :param un_value: 否值
    """
    param_sql: str = ''
    if is_value == '1' and un_value == '1':
        param_sql = f"and ({field} = '{is_value}' or {field} = '0')"
    if is_value == '1' and un_value == '0':
        param_sql = f"and {field} = '{is_value}'"
    if is_value == '0' and un_value == '1':
        param_sql = f"and {field} = '0'"
    if is_value == '0' and un_value == '0':
        param_sql = f"and {field} = '0'"
    return param_sql