from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_bom(**kwargs) -> list:
    """
    查詢BOM
    """
    msq = XinTeaSql()
    where_sql: str = "WHERE 1=1"
    param: list = []
    if kwargs.get('item') != '':
        where_sql += f" AND item = ?"
        param.append(kwargs.get('item'))
    if kwargs.get('bom') != '':
        where_sql += f" AND origin_form_id = ?"
        param.append(kwargs.get('bom'))
    if kwargs.get('m_item') != '':
        where_sql += f" AND m_item = ?"
        param.append(kwargs.get('m_item'))

    cmd: str = f"""SELECT * 
                  FROM item_bom
                  {where_sql}
                  order by item, m_item, s_item
                  """
    return msq.qry(cmd, param)