from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_login_key() -> list:
    """
    查詢登入金鑰
    :return: 登入金鑰
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM login_key"""
    return msq.s_qry(cmd)


def qry_vendor_login(account: str, password: str) -> list:
    """
    廠商登入查詢
    :param account: 帳號
    :param password: 密碼
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM vendor_login WHERE account = ? AND password = ?"""
    return msq.s_qry(cmd, account, password)


def qry_vendor_login_by_account(account: str) -> list:
    """
    根據帳號查詢廠商登入資訊
    :param account: 帳號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM vendor_login WHERE account = ?"""
    return msq.s_qry(cmd, account)