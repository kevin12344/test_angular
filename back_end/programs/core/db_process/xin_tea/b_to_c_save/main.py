import time
from programs.core.db_process.all_db_connect.main import XinTeaSql
from programs.core.data_work import eip_format

def qry_already_exe_b_to_c(bpm_form_id: str) -> list:
    """
    查詢是否已經執行手動觸發過B2C(出入明細)
    :param bpm_form_id: str BPM表單ID
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM eip_api_result WHERE bpm_form_id = ? and eip_service='XinTeaSalesOrderForBtoC'"""
    return msq.s_qry(cmd, bpm_form_id)


def insert_eip_content_V2(env_id: str, eip_param: dict, eip_service: str, api_key: str):
    """
    EIP & NEO 相關資訊寫入至eip_api_result
    :param env_id: str 承租戶代號
    :param eip_param: str BPM基本參數(subject_id、sender、result)
    :param eip_service: str 執行函式名稱
    :param api_key: str BPM金鑰
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO eip_api_result (tenant_id, bpm_form_id, form_sender, eip_service,
             save_time, is_full_execute, is_holding, api_key) 
             VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
    msq.s_do(cmd, env_id, eip_param['subject_id'], eip_format.eip_option_to_str_name(eip_param['sender']), eip_service, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '0', '0', api_key)