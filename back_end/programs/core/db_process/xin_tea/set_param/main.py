from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_vendor_condition() -> list:
    """查詢廠商判斷條件"""
    msq = XinTeaSql()
    cmd = """SELECT row_number, vendor, CONVERT(VARCHAR(10), start_date, 120) AS start_date, 
             order_money, logistics_list, pri_seq 
             FROM vendor_condition
             ORDER BY pri_seq"""
    return msq.s_qry(cmd)


def qry_vendor_condition_to_c() -> list:
    """查詢廠商判斷條件(B2C用)"""
    msq = XinTeaSql()
    cmd = """SELECT row_number, vendor, CONVERT(VARCHAR(10), start_date, 120) AS start_date, 
             order_money, logistics_list, pri_seq 
             FROM vendor_condition_b_to_c
             ORDER BY pri_seq"""
    return msq.s_qry(cmd)




def qry_vendor_condition_by_row_number(row_number: int, modify_vendor_condition_table: str) -> list:
    """
    查詢廠商判斷條件 by row_number
    :param row_number: 編號
    :param modify_vendor_condition_table: table名稱
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM {modify_vendor_condition_table} WHERE row_number = ?"""
    return msq.s_qry(cmd, row_number)

def qry_logistics() -> list:
    """查詢物流名單"""
    msq = XinTeaSql()
    cmd = """SELECT * FROM logistics"""
    return msq.s_qry(cmd)


def crt_logistics_method(add_param: list) -> int:
    """
    新增物流方式
    :param add_param: 新增物流方式參數
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO logistics (row_number, logistics_method) VALUES (?, ?)"""
    cmds_param: list = [
        (cmd, add_param)
    ]
    return msq.transaction_v2(cmds_param)


def qry_logistics_method_exist(logistics_method: str) -> list:
    """
    查詢物流方式是否存在
    :param logistics_method: 物流方式
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM logistics WHERE logistics_method = ?"""
    return msq.s_qry(cmd, logistics_method)

def modify_logisticd_method(row_number: int, logistics_methods: str) -> int:
    """
    修改物流方式
    :param row_number: 編號
    :param logistics_methods: 物流方式
    """
    msq = XinTeaSql()
    cmd = """UPDATE logistics SET logistics_method = ? WHERE row_number = ?"""
    return msq.s_do(cmd, logistics_methods, row_number)


def delete_logistics_method(row_number: int) -> int:
    """
    刪除物流方式
    :param row_number: 編號
    """
    msq = XinTeaSql()
    cmd = """DELETE FROM logistics WHERE row_number = ?"""
    return msq.s_do(cmd, row_number)


def qry_vendor_condition_exist(vendor: str) -> list:
    """
    查詢廠商條件是否存在
    :param vendor: 廠商
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM vendor_condition WHERE vendor = ?"""
    return msq.s_qry(cmd, vendor)


def qry_vendor_condition_pri_seq_exist(pri_seq: str, modify_vendor_condition_table: str) -> list:
    """
    查詢廠商條件的優先權是否存在
    :param pri_seq: 優先權
    :param modify_vendor_condition_table: table名稱
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM {modify_vendor_condition_table} WHERE pri_seq = ?"""
    return msq.s_qry(cmd, pri_seq)



def crt_vendor_condition(vendor_condition: list, add_vendor_condition_table: str) -> bool:
    """
    新增廠商條件
    :param vendor_condition: 廠商條件
    :param add_vendor_condition_table: 新增廠商條件table名稱
    """
    msq = XinTeaSql()
    cmd = f"""INSERT INTO {add_vendor_condition_table} (vendor, start_date, order_money, logistics_list, logistics_list_ch, pri_seq)
             VALUES (?, ?, ?, ?, ?, ?)"""
    cmds_param: list = [
        (cmd, vendor_condition)
    ]
    return msq.transaction_v2(cmds_param)


def modify_vendor_condition(modify: list, modify_vendor_condition_table: str) -> bool:
    """
    修改廠商條件
    :param modify: 廠商條件
    :param modify_vendor_condition_table: 修改廠商條件table名稱
    """
    msq = XinTeaSql()
    cmd = f"""UPDATE {modify_vendor_condition_table} SET vendor=?, start_date=?, order_money=?, logistics_list=?, logistics_list_ch=?, pri_seq=?
             WHERE row_number = ?"""
    cmds_param: list = [
        (cmd, modify)
    ]
    return msq.transaction_v2(cmds_param)


def delete_vendor_condition(row_number: int, delete_vendor_condition_table: str) -> int:
    """
    刪除廠商條件
    :param row_number: 編號
    :param delete_vendor_condition_table: table名稱
    """
    msq = XinTeaSql()
    cmd = f"""DELETE FROM {delete_vendor_condition_table} WHERE row_number = ?"""
    return msq.s_do(cmd, row_number)


def qry_arrival_area() -> list:
    """
    查詢到貨區間
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM arrival_area"""
    return msq.s_qry(cmd)


def qry_vendor_arrival_area() -> list:
    """
    查詢廠商到貨區間
    """
    msq = XinTeaSql()
    cmd = """SELECT generate_vendor
            ,arrival_area_key
            ,FORMAT(to_order_generate_date, 'yyyy/MM/dd') AS to_order_generate_date
            ,FORMAT(earliest_arrival_date, 'yyyy/MM/dd') AS earliest_arrival_date
            ,to_generate_vendor
            ,logistics_list
            ,logistics_list_ch
            ,FORMAT(earliest_factory_date, 'yyyy/MM/dd') AS earliest_factory_date
            ,FORMAT(set_time, 'yyyy-MM-dd HH:mm:ss') AS set_time
        FROM vendor_arrival_area
        order by earliest_arrival_date desc"""
    return msq.s_qry(cmd)


def qry_vendor_arrival_area_to_c() -> list:
    """
    查詢廠商到貨區間(B2C用)
    """
    msq = XinTeaSql()
    cmd = """SELECT generate_vendor
            ,arrival_area_key
            ,FORMAT(to_order_generate_date, 'yyyy/MM/dd') AS to_order_generate_date
            ,FORMAT(earliest_arrival_date, 'yyyy/MM/dd') AS earliest_arrival_date
            ,to_generate_vendor
            ,logistics_list
            ,logistics_list_ch
            ,FORMAT(earliest_factory_date, 'yyyy/MM/dd') AS earliest_factory_date
            ,FORMAT(set_time, 'yyyy-MM-dd HH:mm:ss') AS set_time
        FROM vendor_arrival_area_b_to_c
        order by earliest_arrival_date desc"""
    return msq.s_qry(cmd)



def qry_arrival_area_exist(arrival_area_key: str, earliest_date: str) -> list:
    """
    查詢到貨區間是否存在
    :param arrival_area_key: 到貨區間
    :param earliest_date: 最早到貨日期
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM arrival_area
          WHERE arrival_area_key = ? AND earliest_date = ?"""
    return msq.s_qry(cmd, arrival_area_key, earliest_date)


def crt_arrival_area(new_arrival_area: list) -> bool:
    """
    新增到貨區間
    :param new_arrival_area: 到貨區間
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO arrival_area(arrival_area_key, earliest_date, to_generate_vendor)
             VALUES (?, ?, ?)"""
    cmds_param: list = [
        (cmd, new_arrival_area)
    ]
    return msq.transaction_v2(cmds_param)


def modify_arrival_area(arrival_area: list) -> bool:
    """
    修改到貨區間
    :param arrival_area: 到貨區間
    """
    msq = XinTeaSql()
    cmd = """UPDATE arrival_area SET arrival_area_key=?, earliest_date=?, to_generate_vendor=?
             WHERE arrival_area_key = ? AND earliest_date = ?"""
    cmds_param: list = [
        (
            cmd, arrival_area
        )
    ]
    print(cmds_param)
    return msq.transaction_v2(cmds_param)


def delete_arriva_area(arrival_area: list) -> bool:
    """
    刪除到貨區間
    :param arrival_area: 到貨區間
    """
    msq = XinTeaSql()
    cmd = """DELETE FROM arrival_area WHERE arrival_area_key = ? AND earliest_date = ?"""
    cmds_param: list = [
        (cmd, arrival_area)
    ]
    return msq.transaction_v2(cmds_param)


def crt_vendor_arrival_area(vendor_arrival_area: list, add_vendor_arrival_area_table: str) -> bool:
    """
    新增廠商到貨區間
    :param vendor_arrival_area: 廠商到貨區間
    :param add_vendor_arrival_area_table: table名稱
    """
    msq = XinTeaSql()
    cmd = f"""INSERT INTO {add_vendor_arrival_area_table}(generate_vendor, arrival_area_key, to_order_generate_date,
             earliest_arrival_date, to_generate_vendor, logistics_list, logistics_list_ch, earliest_factory_date)
             VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
    cmds_param: list = [
        (cmd, vendor_arrival_area)
    ]
    return msq.transaction_v2(cmds_param)


def modify_vendor_arrival_area(modify_data: list, modify_vendor_arrival_area_table: str) -> bool:
    """
    修改廠商到或區間
    :param modify_data: 修改資料
    :param modify_vendor_arrival_area_table: table名稱
    """
    msq = XinTeaSql()
    cmd = f"""UPDATE {modify_vendor_arrival_area_table} SET generate_vendor=?, arrival_area_key=?, to_order_generate_date=?,
             earliest_arrival_date=?, to_generate_vendor=?, logistics_list=?, logistics_list_ch=?, earliest_factory_date=?,
             set_time=?
             WHERE generate_vendor = ? and arrival_area_key = ? and logistics_list = ?"""
    cmds_param: list = [
        (cmd, modify_data)
    ]
    return msq.transaction_v2(cmds_param)


def delete_vendor_arrival_area(delete_data: list, delete_vendor_arrival_area_table: list) -> bool:
    """
    刪除廠商到貨區間
    :param delete_data: 刪除資料
    :param delete_vendor_arrival_area_table: table名稱
    """
    msq = XinTeaSql()
    cmd = f"""DELETE FROM {delete_vendor_arrival_area_table} WHERE generate_vendor = ? and arrival_area_key = ? and logistics_list = ?"""
    cmds_param: list = [
        (cmd, delete_data)
    ]
    return msq.transaction_v2(cmds_param)


def qry_vendor() -> list:
    """
    查詢廠商
    """
    msq = XinTeaSql()
    cmd = """SELECT v.vendor_name 
             FROM vendor as v
          """
    return msq.s_qry(cmd)


def qry_vendor_condition_vendor() -> list:
    """
    查詢廠商條件設定的廠商
    """
    msq = XinTeaSql()
    cmd = """SELECT vendor FROM vendor_condition"""
    return msq.s_qry(cmd)


def qry_item_category() -> list:
    """
    查詢料件類別
    """
    msq = XinTeaSql()
    cmd = """SELECT auto_number, item_category,
             CASE WHEN is_spread_calculate = 1 THEN '1' ELSE '0' END AS is_spread_calculate,
             CASE WHEN is_bom = 1 THEN '1' ELSE '0' END AS is_bom
             FROM item_category
             order by auto_number"""
    return msq.s_qry(cmd)


def qry_bom_spread_rule() -> list:
    """
    查詢BOM展算規則
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM bom_spread_rule"""
    return msq.s_qry(cmd)


def qry_item_category_exist(item_category: str) -> list:
    """
    查詢料件類別是否存在
    :param item_category: 料件類別
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_category WHERE item_category = ?"""
    return msq.s_qry(cmd, item_category)


def crt_item_category(item_category: str, is_spread_calculate: str, is_bom: str) -> bool:
    """
    新增料件類別
    :param item_category: 料件類別
    """
    item_category_param: list = [(
        item_category, is_spread_calculate, is_bom
    )]
    msq = XinTeaSql()
    cmd = """INSERT INTO item_category (item_category, is_spread_calculate, is_bom) VALUES (?,?,?)"""
    cmds_param: list = [
        (cmd, item_category_param)
    ]
    return msq.transaction_v2(cmds_param)


def delete_item_category(item_category_id: str) -> bool:
    """
    刪除料件類別
    :param item_category_id: 料件類別ID
    """
    msq = XinTeaSql()
    cmd = """DELETE FROM item_category WHERE auto_number = ?"""
    item_category_id_param: list = [(
        item_category_id,
    )]
    cmds_param: list = [
        (cmd, item_category_id_param)
    ]
    return msq.transaction_v2(cmds_param)


def modify_bom_spread_rule(modify: list) -> bool:
    """
    修改BOM展算規則
    :param modify: 修改資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE bom_spread_rule SET set_item_category = ? WHERE auto_number = ?"""
    cmds_param: list = [
        (cmd, modify)
    ]
    return msq.transaction_v2(cmds_param)


def modify_item_category(modify: list) -> bool:
    """
    修改料件類別
    :param modify: 修改資料
    """
    msq = XinTeaSql()
    cmd: str = """UPDATE item_category SET item_category=?, is_spread_calculate=?, is_bom=?
                  WHERE auto_number = ?"""
    cmds_param: list = [
        (cmd, modify)
    ]
    return msq.transaction_v2(cmds_param)


def qry_is_remark_check_condition() -> list:
    """
    查詢查詢是否備註欄確認判定
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM is_remark_check_condition"""
    return msq.s_qry(cmd)


def delete_is_remark_check_condition(row_number: int) -> bool:
    """
    刪除是否備註欄確認判定
    :param row_number: 編號
    """
    msq = XinTeaSql()
    cmd: str = """DELETE FROM is_remark_check_condition WHERE auto_number = ?"""
    return msq.s_do(cmd, row_number)


def qry_is_remark_check_condition_exist(is_remark_check_condition: str) -> list:
    """
    查詢是否備註欄確認判定是否存在
    :param is_remark_check_condition: 是否備註欄確認判定
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM is_remark_check_condition WHERE text = ?"""
    return msq.s_qry(cmd, is_remark_check_condition)


def crt_is_remark_check_condition(is_remark_check_condition: str) -> bool:
    """
    新增是否備註欄確認判定
    :param is_remark_check_condition: 是否備註欄確認判定
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO is_remark_check_condition (text) VALUES (?)"""
    return msq.s_do(cmd, is_remark_check_condition)


def qry_logistics_method() -> list:
    """
    查詢物流方式
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM logistics"""
    return msq.s_qry(cmd)


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


def qry_item_in_customize_replace(item: str, replace_id: str) -> list:
    """
    查詢料件是否存在於客製料件替換
    :param item: 料件
    :param replace_id: 需扣掉料號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM customize_replace WHERE customize_item = ? and replace_item = ?"""
    return msq.s_qry(cmd, item, replace_id)



def crt_upd_customize_replace(crt: list, upd: list) -> bool:
    """
    新增&修改客製料件替換
    :param crt : list 新增資料
    :param upd : list 修改資料
    """
    msq = XinTeaSql()
    crt_cmd: str =  """INSERT INTO customize_replace(customize_item, replace_item) VALUES(?,?)"""
    #upd_cmd: str = """UPDATE customize_replace SET replace_item = ? WHERE customize_item = ?"""
    delete_cmd: str = """DELETE FROM customize_replace"""
    cmds_param: list = [
        (
            delete_cmd, [()]
        )
    ]
    if crt:
        cmds_param.append((crt_cmd, crt))
    #if upd:
    #    cmds_param.append((upd_cmd, upd))
    return msq.transaction_v2(cmds_param)


def qry_customize_replace() -> list:
    """
    查詢客製料件替換
    """
    msq = XinTeaSql()
    cmd: str = """select cb.customize_item, iad.category as customize_category, iad.item_name as customize_item_name, 
                  iad.bom as customize_bom, cb.replace_item, iadd.category as replace_category, iadd.item_name as replace_item_name, 
                  iadd.bom as replace_bom
                  FROM customize_replace as cb
                  INNER JOIN item_application_detail as iad on cb.customize_item = iad.item
                  LEFT JOIN item_application_detail as iadd on cb.replace_item = iadd.item"""
    return msq.s_qry(cmd)


def crt_customize_item(crt: list) -> bool:
    """
    新增可客製料件
    :param crt : list 新增資料
    """
    msq = XinTeaSql()
    crt_cmd: str =  """INSERT INTO customize_item(item) VALUES(?)"""
    delete_cmd: str = """DELETE FROM customize_item"""
    cmds_param: list = [
        (
            delete_cmd, [()]
        )
    ]
    if crt:
        cmds_param.append((crt_cmd, crt))
    return msq.transaction_v2(cmds_param)


def qry_item_in_customize_item(item: str) -> list:
    """
    查詢料件是否存在於可客製料件
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM customize_item WHERE item = ?"""
    return msq.s_qry(cmd, item)


def qry_customize_item() -> list:
    """查詢可客製料件"""
    msq = XinTeaSql()
    cmd: str = """select ci.item, ia.category, ia.item_name, ia.bom
                  FROM customize_item as ci
                  INNER JOIN item_application_detail as ia on ci.item=ia.item"""
    return msq.s_qry(cmd)


def qry_spare_item_exist(item: str, customize_or_standard: str) -> list:
    """
    查詢備用料件是否存在
    :param item: 料件
    :param customize_or_standard: 客製化 or 標準品
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM spare_item WHERE item = ? AND customize_or_standard = ?"""
    return msq.s_qry(cmd, item, customize_or_standard)



def crt_or_upd_spare_item(crt: list, upd: list) -> bool:
    """
    新增&修改備用料件
    :param crt : list 新增資料
    :param upd : list 修改資料
    """
    msq = XinTeaSql()
    crt_cmd: str = """INSERT INTO spare_item(item, customize_or_standard, spare_item, full_num_additional_add) VALUES(?,?,?,?)"""
    #upd_cmd: str = """UPDATE spare_item SET spare_item = ?, full_num_additional_add = ? WHERE item = ? AND customize_or_standard = ?"""
    delete_cmd: str = """DELETE FROM spare_item"""
    cmds_param: list = [
        (
            delete_cmd, [()]
        )
    ]
    if crt:
        cmds_param.append((crt_cmd, crt))
    #if upd:
    #    cmds_param.append((upd_cmd, upd))
    return msq.transaction_v2(cmds_param)


def qry_spare_item() -> list:
    """查詢備用料件設定"""
    msq = XinTeaSql()
    cmd: str = """select  si.item, iad.product_package, iad.item_name, si.customize_or_standard, si.spare_item, iad2.item_name as spare_item_name, si.full_num_additional_add
                  FROM spare_item as si
                  INNER JOIN item_application_detail as iad on si.item = iad.item
                  INNER JOIN item_application_detail as iad2 on si.spare_item = iad2.item"""
    return msq.s_qry(cmd)


def qry_other_param() -> list:
    """查詢其他參數"""
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM param
                  WHERE exist='1'
                  ORDER BY param_id"""
    return msq.s_qry(cmd)


def upd_other_param(modify: list) -> bool:
    """
    修改其他參數
    :param modify: 修改資料
    """
    msq = XinTeaSql()
    cmd: str = """UPDATE param SET value = ? WHERE param_id = ?"""
    cmds_param: list = [
        (cmd, modify)
    ]
    return msq.transaction_v2(cmds_param)



if __name__ == '__main__':
    pass