from programs.core.db_process.all_db_connect.main import XinTeaSql

def qry_sales_order_b_to_c(**kwargs) -> list:
    """查詢銷售訂單B2C執行結果"""
    where_sql: str = 'WHERE 1=1'
    param: list = []
    conditions: list = []
    if kwargs.get('middle_exe_date_start') != '' and kwargs.get('middle_exe_date_end') != '':
        where_sql += ' AND save_time BETWEEN ? AND ?'
        param.append(kwargs.get('middle_exe_date_start'))
        param.append(kwargs.get('middle_exe_date_end'))
    if kwargs.get('yes') == '1':
        conditions.append("is_full_execute = '1'")
    if kwargs.get('no') == '1':
        conditions.append("is_full_execute = '-1'")
    if kwargs.get('wait_for_exe') == '1':
        conditions.append("is_full_execute = '0'")
    if conditions:
        where_sql += " AND (" + " OR ".join(conditions) + ")"
    
    msq = XinTeaSql()
    cmd = f"""SELECT bpm_form_id, 
                 CASE 
                     WHEN is_full_execute = 1 THEN '成功'
                     WHEN is_full_execute = -1 THEN '失敗'
                     WHEN is_full_execute = 0 THEN '等待執行中'
                     ELSE '未知狀態'
                 END as is_full_execute,
                 CONVERT(varchar, save_time, 120) as save_time
          FROM eip_api_result_special
          {where_sql}
          ORDER BY auto_number"""
    return msq.s_qry(cmd, param)