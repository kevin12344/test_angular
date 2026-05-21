from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_foundry(**kwargs) -> list:
    """
    代工廠大表
    """
    where_sql: str = "WHERE generate_status='0' "
    param: list = []
    if kwargs.get('earliest_arrival_date_start')!= '' and kwargs.get('earliest_arrival_date_end') != '':
        where_sql += "AND earliest_arrival_date BETWEEN ? AND ? "
        param.append(kwargs['earliest_arrival_date_start'])
        param.append(kwargs['earliest_arrival_date_end'])
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
    msq = XinTeaSql()
    cmd: str = f"""
                SELECT 
                    CONVERT(VARCHAR(10), earliest_arrival_date, 120) AS earliest_arrival_date,
                    s_item,
                    s_item_name,
                    SUM(estimate_use) AS total_estimate_use,
                    generate_vendor,
                    generate_status
                FROM use_item_detail
                {where_sql}
                GROUP BY 
                    earliest_arrival_date, 
                    s_item,
                    s_item_name,
                    generate_status, 
                    generate_vendor
                ORDER BY 
                    earliest_arrival_date, 
                    s_item
                """
    return msq.s_qry(cmd, param)


def qry_s_item_select() -> list:
    """
    查詢子件料號(下拉選單)
    """
    msq = XinTeaSql()
    cmd: str = """
                SELECT DISTINCT s_item, s_item_name
                FROM use_item_detail
                WHERE generate_status='0'
                ORDER BY s_item
                """
    return msq.s_qry(cmd)


def qry_generate_vendor_select() -> list:
    """
    查詢生產廠商(下拉選單)
    """
    msq = XinTeaSql()
    cmd: str = """
                SELECT DISTINCT generate_vendor
                FROM use_item_detail
                WHERE generate_status='0'
                ORDER BY generate_vendor
                """
    return msq.s_qry(cmd)



def qry_foundry_by_gs() -> list:
    """
    查詢代工廠大表 By Google Sheet
    """
    msq = XinTeaSql()
    
    cmd: str = """SELECT 
                CONVERT(VARCHAR(10), earliest_arrival_date, 120) AS earliest_arrival_date,
                CONVERT(VARCHAR(10), latest_arrival_date, 120) AS latest_arrival_date,
                CASE 
                    WHEN shipping_date = '1900-01-01' THEN '' 
                    ELSE CONVERT(VARCHAR(10), shipping_date, 120) 
                END AS shipping_date,
                item,
                item_name,
                SUM(estimate_generate) AS total_estimate_generate,
                m_item,
                m_item_name,
                s_item,
                s_item_name,
                s_item_use,
                SUM(estimate_use) AS total_estimate_use,
                generate_vendor,
                generate_status,
                status
            FROM use_item_detail
            WHERE generate_status='0'
            GROUP BY 
                earliest_arrival_date, 
                latest_arrival_date, 
                shipping_date,
                item, 
                item_name, 
                m_item, 
                m_item_name, 
                s_item, 
                s_item_name, 
                s_item_use,
                generate_vendor, 
                generate_status,
                status
            ORDER BY 
                earliest_arrival_date, 
                item
                """
    return msq.s_qry(cmd)