from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_customer(**kwargs) -> list:
    """
    查詢客戶
    """
    where_sql: str = "WHERE 1=1"
    param: list = []
    
    if kwargs.get('customer_uniform_invoice_no') != '':
        where_sql += " AND customer_uniform_invoice_no like ?"
        param.append(f"%{kwargs.get('customer_uniform_invoice_no')}%")
    if kwargs.get('customer_name') != '':
        where_sql += " AND customer_name like ?"
        param.append(f"%{kwargs.get('customer_name')}%")
    msq = XinTeaSql()
    
    cmd = f"""SELECT * FROM customer 
              {where_sql}"""
    return msq.s_qry(cmd, param)

def qry_customer_exist(customer_id: str) -> list:
    """
    查詢客戶是否存在
    :param customer_id 客戶編號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM customer WHERE customer_id=?"""
    return msq.s_qry(cmd, customer_id)


def customer_sync(customer_add: list, customer_upd: list) -> bool:
    """
    客戶基本資料同步
    :param customer_add 新增客戶
    :param customer_upd 更新客戶
    """
    msq = XinTeaSql()
    
    customer_add_sql: str = """INSERT INTO customer(sys_id, customer_id, customer_name, customer_title, customer_uniform_invoice_no,
      customer_address, customer_window, customer_phone, customer_email, payment_term, payment_type,
      bank, bank_branch, bank_account, currency_type, freight_type, freight, bpm_form_id) 
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
      
    customer_upd_sql: str = """UPDATE customer SET customer_name=?, customer_title=?, customer_uniform_invoice_no=?,
      customer_address=?, customer_window=?, customer_phone=?, customer_email=?, payment_term=?, payment_type=?,
      bank=?, bank_branch=?, bank_account=?, currency_type=?, freight_type=?, freight=?, bpm_form_id=?
      WHERE customer_id=?"""
      
    cmds_param: list = []
    if customer_add:
        cmds_param.append((customer_add_sql, customer_add))
    if customer_upd:
        cmds_param.append((customer_upd_sql, customer_upd))
    return msq.transaction_v2(cmds_param)