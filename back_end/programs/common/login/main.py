
from programs.core.data_work import string_format
from programs.core.db_process.xin_tea import main as xin_tea
from flask import session

def check_login(account: str) -> dict:
    """
    檢查登入帳號密碼是否正確
    :param account: 帳號
    """
    login: list = xin_tea.qry_account_password(account)
    if len(login) == 0:
        return {'msg': '帳號不存在，請聯繫負責人員設定帳號', 'login': []}
    return {'msg': '登入成功', 'login': login}
        
    