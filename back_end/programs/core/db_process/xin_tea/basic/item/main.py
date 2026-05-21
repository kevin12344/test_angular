from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_item_data(**kwargs) -> list:
    """
    料件主檔查詢
    """
    msq = XinTeaSql()
    where_sql: str = "WHERE 1=1"
    param: list = []
    if kwargs.get('item') != '':
        where_sql += " AND item like ?"
        param.append(f"%{kwargs.get('item')}%")
    
    cmd = f"""SELECT * FROM item_application_detail
              {where_sql}
              order by auto_number"""
    return msq.s_qry(cmd, param)


def qry_item_exist(item_id: str) -> list:
    """
    查詢料件是否存在
    :param item_id 料件編號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_application_detail WHERE item=?"""
    return msq.s_qry(cmd, item_id)


def item_sync(item_add: list, item_upd: list) -> bool:
    """
    料件基本資料同步
    :param item_add 新增料件
    :param item_upd 更新料件
    """
    msq = XinTeaSql()
    item_add_sql: str = """INSERT INTO item_application_detail 
                           (bpm_form_id, item, category, item_name, unit, 
                           unit_price, google_sheet_url, purchase_price, remark, 
                           supplier, bom, item_file_url, total_delivert_date, 
                           delivery_date, moq, full_box_num, place_order_url, 
                           safe_inventory, product_classification, product_package) 
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    item_upd_sql: str = """UPDATE item_application_detail SET bpm_form_id=?,
                           category=?, item_name=?, unit=?, unit_price=?, 
                           google_sheet_url=?, purchase_price=?, remark=?, 
                           supplier=?, bom=?, item_file_url=?, total_delivert_date=?, 
                           delivery_date=?, moq=?, full_box_num=?, place_order_url=?, 
                           safe_inventory=?, product_classification=?, product_package=? 
                           WHERE item=?"""
    cmds_param: list = []
    if item_add:
        cmds_param.append((item_add_sql, item_add))
    if item_upd:
        cmds_param.append((item_upd_sql, item_upd))
    return msq.transaction_v2(cmds_param)


def qry_upd_item_for_order_manage_summary_b_to_c() -> list:
    """
    查詢訂單管理總表會需要更新的訂單料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT oms.order_key, oms.bom_bpm_form_id, iad.bom as new_bom
                  FROM order_manage_summary_b_to_c as oms 
                  INNER JOIN item_application_detail as iad on oms.item = iad.item
                  WHERE status NOT IN ('3', '3.1', '4', '4.1', '6.1')"""
    return msq.s_qry(cmd)


def upd_order_manage_summary_b_to_c_bom(upd_order_manage_summary_b_to_c: list) -> bool:
    """
    更新訂單管理摘要表 (B to C)
    :param upd_order_manage_summary_b_to_c: 更新資料
    """
    msq = XinTeaSql()
    cmd: str = """UPDATE order_manage_summary_b_to_c
                  SET check_message = ?, bom_bpm_form_id = ?
                  WHERE order_key = ?"""
    cmds_param: list = []
    if upd_order_manage_summary_b_to_c:
        cmds_param.append((cmd, upd_order_manage_summary_b_to_c))
    return msq.transaction_v2(cmds_param)