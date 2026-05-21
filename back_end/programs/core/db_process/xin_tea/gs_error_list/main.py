from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_gs_error_list() -> list:
    """
    GS觸發失敗查詢
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * 
                  FROM gs_sheet_fail_list"""
    return msq.s_qry(cmd)