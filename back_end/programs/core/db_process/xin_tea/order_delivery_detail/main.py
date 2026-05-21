from programs.core.db_process.all_db_connect.main import XinTeaSql

def qry_order_delivery_detail(**kwargs) -> list:
    """查詢訂單配送明細"""
    where_sql: str = 'WHERE 1=1'
    param: list = []
    if kwargs.get('to_order_generate_date_start') != '' and kwargs.get('to_order_generate_date_end') != '':
        where_sql += " AND om.to_order_generate_date BETWEEN ? AND ?"
        param.append(kwargs.get('to_order_generate_date_start'))
        param.append(kwargs.get('to_order_generate_date_end'))
    if kwargs.get('latest_arrival_date_start') != '' and kwargs.get('latest_arrival_date_end') != '':
        where_sql += " AND om.latest_arrival_date BETWEEN ? AND ?"
        param.append(kwargs.get('latest_arrival_date_start'))
        param.append(kwargs.get('latest_arrival_date_end'))
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?' for _ in range(len(item_list))])
        where_sql += f' AND om.item IN ({placeholders})'
        param.extend(item_list)
    if kwargs.get('vendor_check') != '':
        vendor_check_list = kwargs.get('vendor_check').split(',')
        placeholders = ','.join(['?' for _ in range(len(vendor_check_list))])
        where_sql += f' AND om.vendor_check IN ({placeholders})'
        param.extend(vendor_check_list)
    if kwargs.get('vendor_order_status') != '':
        vendor_order_status_list = kwargs.get('vendor_order_status').split(',')
        placeholders = ','.join(['?' for _ in range(len(vendor_order_status_list))])
        where_sql += f' AND om.vendor_order_status IN ({placeholders})'
        param.extend(vendor_order_status_list)
    if kwargs.get('e_commerce_platform_order_no') != '':
        where_sql += " AND om.e_commerce_platform_order_no LIKE ?"
        param.append(f"%{kwargs.get('e_commerce_platform_order_no')}%")
    msq = XinTeaSql()
    cmd = f"""SELECT om.auto_number, om.already_order_order_status, so.step AS b2c_order_is_can_sign, so.status AS b2c_order_status, om.b2c_bpm_form_id,
                om.estimate_num_and_check, om.eip_import_label, om.package_factory_import_label, om.split_berfore_order_no,
                om.common_order_no_different_vendor, CONVERT(varchar, om.common_order_no_different_shipping_date, 23) AS common_order_no_different_shipping_date, 
                CONVERT(varchar, om.latest_arrival_date, 23) AS latest_arrival_date,
                om.white_list_process, om.is_check_remark_message, 
                CONVERT(varchar, om.to_order_generate_date, 23) AS to_order_generate_date,
                CONVERT(varchar, om.earliest_arrival_date, 23) AS earliest_arrival_date,
                om.generate_vendor, om.shipping_out_warehouse, om.e_commerce_platform_order_no, om.e_commerce_platform,
                CONVERT(varchar, om.e_commerce_platform_order_date, 111) as e_commerce_platform_order_date,
                om.new_order_order_status, om.new_order_payment_status, om.logistics_method,
                om.order_remark_or_shipping_remark, om.item, om.product_name, om.item_category, om.bom_bpm_form_id, om.platform_product_name,
                om.platform_specific, om.quantity, om.recipient, om.recipient_phone, om.recipient_address, om.recipient_email, om.payment_term,
                om.order_money, om.invoice_title, om.uniform_invoice_no, om.sender, om.sender_phone, om.order_key, om.arrival_area, 
                om.importer, CONVERT(varchar, om.import_date, 120) AS import_date, om.google_sheet_url, om.google_sheet_name,
                om.xin_tea_remark, CASE WHEN om.to_vendor = 1 THEN '1' ELSE '0' END AS to_vendor,
                CASE WHEN om.vendor_check = 1 THEN '1' ELSE '0' END AS vendor_check,
                om.status, om.vendor_order_status, om.check_message, om.xin_tea_remark,
                om.delivery_vendor
                FROM vendor_order_b_to_c as om
                LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id 
                {where_sql}
                order by order_key"""
    return msq.s_qry(cmd, param)


def qry_item_by_qry() -> list:
    """
    查詢料號(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = f"""SELECT DISTINCT om.item, om.product_name
             FROM vendor_order_b_to_c as om
             LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id
             """
    return msq.s_qry(cmd)


def qry_vendor_check() -> list:
    """
    查詢廠商確認(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = f"""SELECT DISTINCT om.vendor_check AS value,
             CASE 
                WHEN om.vendor_check = '1' THEN '已確認' 
                WHEN om.vendor_check = '0' THEN '待確認' 
             END AS vendor_check
             FROM vendor_order_b_to_c as om
             LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id
             WHERE om.vendor_check IS NOT NULL"""
    return msq.s_qry(cmd)


def qry_vendor_order_status() -> list:
    """
    查詢廠商訂單狀態(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = f"""SELECT DISTINCT om.vendor_order_status
             FROM vendor_order_b_to_c as om
             LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id
             WHERE om.vendor_order_status IS NOT NULL"""
    return msq.s_qry(cmd)


def qry_vendor_order_check_by_dashboard(vendor_check_status: str) -> list:
    """
    查詢廠商訂單狀態(儀表板)
    :param vendor_check_status: 廠商確認狀態
    :param generate_vendor: 生產廠商
    """
    where_sql: str = 'WHERE vendor_check = ?'
    param: list = [vendor_check_status]
    msq = XinTeaSql()
    cmd: str = f"""SELECT COUNT(*) AS count
             FROM vendor_order_b_to_c
              {where_sql}"""
    return msq.s_qry(cmd, param)


def qry_delivery_vendor() -> list:
    """
    查詢配送廠商(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT om.delivery_vendor
             FROM vendor_order_b_to_c as om
             LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id
             WHERE om.vendor_check IS NOT NULL"""
    return msq.s_qry(cmd)