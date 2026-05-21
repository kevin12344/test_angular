from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_item_detail_in_out(**kwargs) -> list:
    """
    出入明細查詢
    """
    where_sql: str = "WHERE generate_status='1'"
    param: list = []
    if kwargs.get('s_item') != '':
        s_item_list = kwargs.get('s_item').split(',')
        placeholders = ','.join(['?' for _ in range(len(s_item_list))])
        where_sql += f' AND s_item IN ({placeholders})'
        param.extend(s_item_list)
    if kwargs.get('shipping_out_warehouse') != '':
        shipping_out_warehouse_list = kwargs.get('shipping_out_warehouse').split(',')
        placeholders = ','.join(['?' for _ in range(len(shipping_out_warehouse_list))])
        where_sql += f' AND shipping_out_warehouse IN ({placeholders})'
        param.extend(shipping_out_warehouse_list)
    msq = XinTeaSql()
    cmd: str = f"""SELECT 
        SUM(estimate_generate) AS total_estimate_generate,
        s_item,
        s_item_name,
        -SUM(estimate_use) AS total_estimate_use,
        unit,
        shipping_out_warehouse,
        generate_status,
        CONVERT(VARCHAR(19), complete_time, 120) AS complete_time
    FROM use_item_detail
    {where_sql}
    GROUP BY 
        s_item, 
        s_item_name, 
        unit,
        shipping_out_warehouse,
        generate_status, 
        complete_time
    ORDER BY s_item"""
    return msq.s_qry(cmd, param)


def qry_s_item_select() -> list:
    """
    查詢子件代號(下拉選單)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT s_item, s_item_name
                FROM use_item_detail
                WHERE generate_status='1'
                GROUP BY 
                    s_item, 
                    s_item_name, 
                    unit,
                    generate_vendor, 
                    shipping_out_warehouse,
                    generate_status, complete_time
                    order by s_item"""
    return msq.s_qry(cmd)


def qry_shipping_out_warehouse_select() -> list:
    """
    查詢倉別(下拉選單)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT shipping_out_warehouse
                FROM use_item_detail
                WHERE generate_status='1'
                GROUP BY 
                    s_item, 
                    s_item_name, 
                    unit,
                    generate_vendor, 
                    shipping_out_warehouse,
                    generate_status, complete_time
                    order by shipping_out_warehouse"""
    return msq.s_qry(cmd)



def qry_item_detail_in_out_for_google_sheet() -> list:

    msq = XinTeaSql()
    cmd: str = f"""SELECT 
        SUM(estimate_generate) AS total_estimate_generate,
        s_item,
        s_item_name,
        -SUM(estimate_use) AS total_estimate_use,
        unit,
        shipping_out_warehouse,
        generate_status,
        CONVERT(VARCHAR(19), complete_time, 120) AS complete_time
    FROM use_item_detail
    WHERE generate_status='1'
    GROUP BY 
        s_item, 
        s_item_name, 
        unit,
        shipping_out_warehouse,
        generate_status, 
        complete_time
    ORDER BY s_item"""
    return msq.s_qry(cmd)