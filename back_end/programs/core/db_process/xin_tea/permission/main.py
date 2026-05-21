from programs.core.db_process.all_db_connect.main import XinTeaSql
from programs.core.data_work import eip_format


def qry_dept_permission(dept: str) -> list:
    """
    查詢部門資料權限
    :param dept 部門
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM dept_permission WHERE dept = ?"""
    return msq.s_qry(cmd, dept)


def qry_role_permission(role: str) -> list:
    """
    查詢角色資料權限
    :param role 角色
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM role_permission WHERE role = ?"""
    return msq.s_qry(cmd, role)


def crt_role_permission(**kwargs) -> int:
    """
    新增角色權限
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO role_permission (role, permission) VALUES (?, ?)"""
    return msq.s_do(cmd, kwargs['role'], kwargs['permission'])



def qry_account_permission(account: str) -> list:
    """
    查詢帳號資料權限
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM account_permission WHERE account=?"""
    return msq.s_qry(cmd, account)


def crt_account_permission(**kwargs) -> int:
    """
    新增帳號權限
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO account_permission (account, dept, name, permission, item, customer, vendor, sales_order_b_to_c_qry, item_reference,
             order_import, order_manage_summary_b_to_c, spread_calculate, use_item_detail, foundry, item_detail_in_out, set_param, vendor_order_check) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    return msq.s_do(cmd, kwargs['account'], kwargs['dept'], kwargs['name'], kwargs['permission'], kwargs['item'],
                    kwargs['customer'], kwargs['vendor'], kwargs['sales_order_b_to_c_qry'], kwargs['item_reference'],
                    kwargs['order_import'], kwargs['order_manage_summary_b_to_c'], kwargs['spread_calculate'],
                    kwargs['use_item_detail'], kwargs['foundry'], kwargs['item_detail_in_out'], kwargs['set_param'],
                    kwargs['vendor_order_check'])


def upd_account_permission(**kwargs) -> int:
    """
    修改帳號權限
    """
    msq = XinTeaSql()
    cmd = """UPDATE account_permission 
             SET dept=?, name=?, permission=?, item=?, customer=?, vendor=?,
             sales_order_b_to_c_qry=?, item_reference=?, order_import=?,
             order_manage_summary_b_to_c=?, spread_calculate=?, use_item_detail=?,
             foundry=?, item_detail_in_out=?, set_param=?, vendor_order_check=?
             WHERE account=?"""
    return msq.s_do(cmd, kwargs['dept'], kwargs['name'], kwargs['permission'],
                    kwargs['item'], kwargs['customer'], kwargs['vendor'], kwargs['sales_order_b_to_c_qry'],
                    kwargs['item_reference'], kwargs['order_import'], kwargs['order_manage_summary_b_to_c'],
                    kwargs['spread_calculate'], kwargs['use_item_detail'], kwargs['foundry'],
                    kwargs['item_detail_in_out'], kwargs['set_param'], kwargs['vendor_order_check'],
                    kwargs['account'])


def qry_permission_nav_param() -> list:
    """
    查詢權限控管nav參數
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM permission_nav_param"""
    return msq.s_qry(cmd)

def qry_permission(table_name: str) -> list:
    """
    權限角度查詢(權限控管)
    :param table_name: str 表名
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM {table_name}"""
    return msq.s_qry(cmd)


def upd_permission(**kwargs) -> int:
    """
    修改權限(權限控管)
    """
    msq = XinTeaSql()
    cmd = f"""UPDATE {kwargs['permission_type']} 
              SET permission=?, item=?, customer=?, vendor=?, sales_order_b_to_c_qry=?, item_reference=?,
              order_import=?, order_manage_summary_b_to_c=?, spread_calculate=?, use_item_detail=?,
              foundry=?, item_detail_in_out=?, set_param=?, vendor_order_check=?, bom=?, b_to_c_save=?,
              order_delivery_detail=?, inventory=?, b_to_b=?
              WHERE {kwargs['permission_type_title']}=?"""
    return msq.s_do(cmd, kwargs['permission'], kwargs['item'], kwargs['customer'], kwargs['vendor'],
                    kwargs['sales_order_b_to_c_qry'], kwargs['item_reference'], kwargs['order_import'], 
                    kwargs['order_manage_summary_b_to_c'], kwargs['spread_calculate'], kwargs['use_item_detail'],
                    kwargs['foundry'], kwargs['item_detail_in_out'], kwargs['set_param'], kwargs['vendor_order_check'],
                    kwargs['bom'], kwargs['b_to_c_save'], kwargs['order_delivery_detail'], kwargs['inventory'],
                    kwargs['b_to_b'], kwargs['id'])
    

def crt_or_upd_account_info_dept(crt_data: list , upd_data: list, dept_crt: list) -> bool:
    """
    新增或修改帳號、部門資料
    :param crt_data: list 新增資料
    :param upd_data: list 修改資料
    :param dept_crt: list 部門新增
    """
    msq = XinTeaSql()
    crt_cmd: str = """INSERT INTO account_permission(account, dept, name) VALUES(?, ?, ?)"""
    upd_cmd: str = """UPDATE account_permission SET dept=? WHERE account=?"""
    dept_crt_cmd: str = """INSERT INTO dept_permission(dept) VALUES(?)"""
    cmds_param: list = []
    if crt_data:
        cmds_param.append(
            (
                crt_cmd, crt_data
            )
        )
    if upd_data:
        cmds_param.append(
            (
                upd_cmd, upd_data
            )
        )
    if dept_crt:
        cmds_param.append(
            (
                dept_crt_cmd, dept_crt
            )
        )
    return msq.transaction_v2(cmds_param)


def qry_account_info_file_column() -> list:
    """查詢人員帳號匯入資料必要欄位"""
    msq = XinTeaSql()
    cmd = """SELECT * FROM account_info_column"""
    return msq.s_qry(cmd)


if __name__ == '__main__':
    print(qry_role_permission('[財務主管(cfo#unknown)]/n[特助(SA#unknown)]/n'))