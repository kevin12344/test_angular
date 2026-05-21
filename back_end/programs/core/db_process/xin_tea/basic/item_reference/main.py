from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_item_reference(**kwargs) -> list:
    """
    查詢料件參照表
    """
    where_sql: str = "WHERE 1=1"
    param: list = []
    
    if kwargs.get("item_id"):
        where_sql += f" AND item_id = ?"
        param.append(kwargs.get('item_id'))
    if kwargs.get('vendor_name'):
        where_sql += f" AND vendor_name = ?"
        param.append(f"{kwargs.get('vendor_name')}")
        
    msq = XinTeaSql()
    cmd = f"""SELECT ir.item_id, 
                iad.item_name, 
                iad.unit, 
                ir.vendor_name, 
                CONCAT(ir.item_id, iad.item_name) AS item_key,
                CASE WHEN ir.relationship = '1' THEN '1' ELSE '' END AS relationship
              FROM item_reference as ir
              LEFT JOIN item_application_detail as iad on ir.item_id = iad.item
              {where_sql}
           """
    return msq.s_qry(cmd, param)


def qry_item_id_in_item(item: list) -> list:
    """
    查詢料件是否存在於料件主檔
    :param item: list 料件資料
    """
    place_holders = ','.join(['?' for _ in item])
    msq = XinTeaSql()
   # 直接查詢存在的項目
    cmd = f"""SELECT item 
              FROM item_application_detail 
              WHERE item IN ({place_holders})"""
    return msq.s_qry(cmd, *item)


def qry_vendor_in_vendor_list(vendor: list) -> list:
    """
    查詢廠商是否存在於廠商主檔
    :param vendor: list 廠商資料
    """
    place_holders = ','.join(['?' for _ in vendor])
    msq = XinTeaSql()
   # 直接查詢存在的項目
    cmd = f"""SELECT vendor_name AS vendor 
              FROM vendor 
              WHERE vendor_name IN ({place_holders})"""
    return msq.s_qry(cmd, *vendor)


def qry_vendor_in_vendor(vendor: str) -> list:
    """
    查詢廠商是否存在於廠商主檔
    :param vendor: str 廠商簡稱
    """
    msq = XinTeaSql()
    cmd = f"""SELECT vendor_name AS vendor 
              FROM vendor 
              WHERE vendor_name = ?"""
    return msq.s_qry(cmd, vendor)



def qry_item_reference_exist(item_id: str, vendor_name: str) -> list:
    """
    查詢料件參照表是否存在
    :param item_id: 料件編號
    :param vendor_name: 廠商名稱
    """
    msq = XinTeaSql()
    cmd = f"""SELECT item_id, vendor_name 
              FROM item_reference 
              WHERE item_id = ? AND vendor_name = ?"""
    print(cmd, item_id, vendor_name)
    return msq.s_qry(cmd, item_id, vendor_name)


def crt_and_upd_item_reference(crt: list, upd: list, add_vendor: list) -> bool:
    """
    新增&修改料件參照表&新增生產廠商
    :param crt : list 新增資料
    :param upd : list 修改資料
    :param add_vendor: list 新增廠商資料
    """
    print('crt', crt)
    print('upd', upd)
    msq = XinTeaSql()
    crt_cmd: str = """INSERT INTO item_reference (item_id, vendor_name, item_name, unit, relationship)
                      VALUES (?, ?, ?, ?, ?)"""
    upd_cmd: str = """UPDATE item_reference SET relationship = ? WHERE item_id = ? AND vendor_name = ?"""
    add_vendor_cmd: str = """INSERT INTO generate_vendor(vendor_id, vendor_name, warehouse, exist)
                      VALUES (?, ?, ?, ?)"""
    cmds_param: list = []
    if crt:
        cmds_param.append((crt_cmd, crt))
    if upd:
        cmds_param.append((upd_cmd, upd))
    if add_vendor:
        cmds_param.append((add_vendor_cmd, add_vendor))
    return msq.transaction_v2(cmds_param)


def qry_vendor_in_generate_vendor(vendor_name: str) -> list:
    """
    廠商是否存在於廠商主檔
    :param vendor_name: 廠商名稱
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM generate_vendor WHERE vendor_name = ?"""
    return msq.s_qry(cmd, vendor_name)


def qry_vendor_data(vendor_name: str) -> list:
    """
    查詢廠商資料
    """
    msq = XinTeaSql()
    cmd: str = """SELECT vendor_id, vendor_name, consume_warehouse
                  FROM vendor
                  WHERE vendor_name = ?"""
    return msq.s_qry(cmd, vendor_name)
    


if __name__ == '__main__':
    print(qry_item_id_in_item(['1010001', '1010002']))
             