from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_use_item_detail(**kwargs) -> list:
    """
    用料明細查詢
    """
    where_sql: str = 'WHERE 1=1'
    param: list = []
    if kwargs.get('order_key') != '':
        order_key_list = kwargs.get('order_key').split(',')
        placeholders = ','.join(['?' for _ in range(len(order_key_list))])
        where_sql += f' AND order_key IN ({placeholders})'
        param.extend(order_key_list)
    if kwargs.get('m_item') != '':
        m_item_list = kwargs.get('m_item').split(',')
        placeholders = ','.join(['?' for _ in range(len(m_item_list))])
        where_sql += f' AND m_item IN ({placeholders})'
        param.extend(m_item_list)
    if kwargs.get('s_item') != '':
        s_item_list = kwargs.get('s_item').split(',')
        placeholders = ','.join(['?' for _ in range(len(s_item_list))])
        where_sql += f' AND s_item IN ({placeholders})'
        param.extend(s_item_list)
    if kwargs.get('generate_vendor') != '':
        generate_vendor_list = kwargs.get('generate_vendor').split(',')
        placeholders = ','.join(['?' for _ in range(len(generate_vendor_list))])
        where_sql += f' AND generate_vendor IN ({placeholders})'
        param.extend(generate_vendor_list)
    if kwargs.get('generate_status') != '':
        generate_status_list = kwargs.get('generate_status').split(',')
        placeholders = ','.join(['?' for _ in range(len(generate_status_list))])
        where_sql += f' AND generate_status IN ({placeholders})'
        param.extend(generate_status_list)
    if kwargs.get('earliest_arrival_date_start') != '' and kwargs.get('earliest_arrival_date_end') != '':
        where_sql += " AND earliest_arrival_date BETWEEN ? AND ?"
        param.append(kwargs.get('earliest_arrival_date_start'))
        param.append(kwargs.get('earliest_arrival_date_end'))
    if kwargs.get('latest_arrival_date_start') != '' and kwargs.get('latest_arrival_date_end') != '':
        where_sql += " AND latest_arrival_date BETWEEN ? AND ?"
        param.append(kwargs.get('latest_arrival_date_start'))
        param.append(kwargs.get('latest_arrival_date_end'))
    if kwargs.get('complete_time') != '':
        where_sql += " AND complete_time BETWEEN ? AND ?"
        param.append(kwargs.get('complete_time'))
        param.append(kwargs.get('complete_time'))
    if kwargs.get('to_order_generate_date_start') != '' and kwargs.get('to_order_generate_date_end') != '':
        where_sql += " AND to_order_generate_date BETWEEN ? AND ?"
        param.append(kwargs.get('to_order_generate_date_start'))
        param.append(kwargs.get('to_order_generate_date_end'))
    msq = XinTeaSql()
    cmd: str = f"""SELECT 
        order_key,
        CONVERT(VARCHAR(10), to_order_generate_date, 120) AS to_order_generate_date,
        CONVERT(VARCHAR(10), earliest_arrival_date, 120) AS earliest_arrival_date,
        CONVERT(VARCHAR(10), latest_arrival_date, 120) AS latest_arrival_date,
        CASE 
            WHEN shipping_date = '1900-01-01' THEN '' 
            ELSE CONVERT(VARCHAR(10), shipping_date, 120) 
        END AS shipping_date,
        item,
        item_name,
        estimate_generate,
        customize_or_normal,
        customize_specific,
        order_remark,
        m_item,
        m_item_name,
        s_item,
        s_item_name,
        s_item_use,
        estimate_use,
        customize_item,
        uu_one,
        customer,
        item_category,
        generate_vendor,
        generate_status,
        oem_fee,
        other_expense,
        advance_expenses,
        total_expense,
        shipping_out_warehouse,
        bom_bpm_form_id,
        generate_status AS status,
        CONVERT(VARCHAR(19), complete_time, 120) AS complete_time,
        e_commerce_platform_order_no, split_before_order_no
    FROM use_item_detail
    {where_sql}
    ORDER BY order_key"""
    return msq.s_qry(cmd, param)

def qry_order_key_by_qry() -> list:
    """
    查詢生產單號(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT order_key FROM use_item_detail
             ORDER BY order_key"""
    return msq.s_qry(cmd)


def qry_m_item_by_qry() -> list:
    """
    查詢母件料號(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT m_item FROM use_item_detail
             ORDER BY m_item"""
    return msq.s_qry(cmd)


def qry_s_item_by_qry() -> list:
    """
    查詢子件用料(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT s_item FROM use_item_detail
             ORDER BY s_item"""
    return msq.s_qry(cmd)


def qry_generate_vendor_by_qry() -> list:
    """
    查詢生產廠商(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT generate_vendor FROM use_item_detail
             ORDER BY generate_vendor"""
    return msq.s_qry(cmd)


def qry_generate_status_by_qry() -> list:
    """
    查詢生產狀態(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT generate_status FROM use_item_detail
             ORDER BY generate_status"""
    return msq.s_qry(cmd)