from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_vendor(**kwargs) -> list:
    """
    查詢廠商
    """
    where_sql: str = "WHERE 1=1"
    param: list = []
    
    if kwargs.get('vendor_uniform_invoice_no') != '':
        where_sql += " AND vendor_uniform_invoice_no like ?"
        param.append(f"%{kwargs.get('vendor_uniform_invoice_no')}%")
    if kwargs.get('vendor_name') != '':
        where_sql += " AND vendor_name like ?"
        param.append(f"%{kwargs.get('vendor_name')}%")
    
    msq = XinTeaSql()
    
    cmd = f"""SELECT * FROM vendor
             {where_sql}"""
    return msq.s_qry(cmd, param)


def qry_vendor_exist(vendor_id: str) -> list:
    """
    查詢廠商是否存在
    :param vendor_id 廠商編號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM vendor WHERE vendor_id=?"""
    return msq.s_qry(cmd, vendor_id)


def vendor_sync(vendor_add: list, vendor_upd: list) -> bool:
    """
    廠商基本資料同步
    :param vendor_add 新增廠商
    :param vendor_upd 更新廠商
    """
    msq = XinTeaSql()
    
    vendor_add_cmd: str = """INSERT INTO vendor (sys_id, vendor_id, vendor_name, vendor_title, 
    consume_warehouse, inventory_in_warehouse, vendor_window, vendor_phone, vendor_address, 
    vendor_email, invoice_send, payment_type, payment_time, freight_rule, client, client_phone, 
    client_address, crt_form, invoice_recipient, invoice_receipt_phone, invoice_receipt_information, 
    currency_type, tax_type, additional_tax, moq, vendor_uniform_invoice_no, delivery_date, 
    payment_date, bank, bank_account, bpm_form_id, create_form_type, oem_file_url, note, 
    vendor_passbook, upd_date, audit_supervisior, application) 
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    
    vendor_upd_cmd: str = """UPDATE vendor SET vendor_name=?, vendor_title=?, consume_warehouse=?,
    inventory_in_warehouse=?, vendor_window=?, vendor_phone=?, vendor_address=?, vendor_email=?,
    invoice_send=?, payment_type=?, payment_time=?, freight_rule=?, client=?, client_phone=?,
    client_address=?, crt_form=?, invoice_recipient=?, invoice_receipt_phone=?, invoice_receipt_information=?,
    currency_type=?, tax_type=?, additional_tax=?, moq=?, vendor_uniform_invoice_no=?, delivery_date=?,
    payment_date=?, bank=?, bank_account=?, bpm_form_id=?, create_form_type=?, oem_file_url=?, note=?,
    vendor_passbook=?, upd_date=?, audit_supervisior=?, application=? WHERE vendor_id=?"""
    
    cmds_param: list = []
    
    if vendor_add:
        cmds_param.append((vendor_add_cmd, vendor_add))
    if vendor_upd:
        cmds_param.append((vendor_upd_cmd, vendor_upd))
    return msq.transaction_v2(cmds_param)
    