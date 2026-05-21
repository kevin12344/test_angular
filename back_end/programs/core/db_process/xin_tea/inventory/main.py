from programs.core.db_process.all_db_connect.main import XinTeaSql



def qry_inventory(**kwargs) -> list:
    """
    查詢庫存資料
    """
    where_sql: str = " WHERE 1=1 "
    param: list = []
    if kwargs.get('issue_date_start') != '' and kwargs.get('issue_date_end') != '':
        where_sql += " AND issue_date BETWEEN ? AND ? "
        param.append(kwargs.get('issue_date_start'))
        param.append(kwargs.get('issue_date_end'))
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?'] * len(item_list))
        where_sql += f" AND s_item IN ({placeholders}) "
        param.extend(item_list)
    if kwargs.get('warehouse') != '':
        warehouse_list = kwargs.get('warehouse').split(',')
        placeholders = ','.join(['?'] * len(warehouse_list))
        where_sql += f" AND cost_warehouse IN ({placeholders}) "
        param.extend(warehouse_list)
     
    msq = XinTeaSql()
    cmd: str = f"""SELECT 
        bpm_form_id,
        s_item,
        s_item_name,
        unit,
        estimate_cost_quantity,
        key1,
        key_word,
        cost_warehouse,
        issue_date,
        source_type,
        sort_order
    FROM (
        -- 禮盒生產單 (主檔)
        SELECT 
            gbg.bpm_form_id,
            gbg.item as s_item,
            gbg.item_name as s_item_name,
            NULL as unit,
            gbg.complete_num as estimate_cost_quantity,
            gbg.item + gbg.cost_warehouse as key1,
            gbg.item + gbg.cost_warehouse as key_word,
            gbg.cost_warehouse,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-主檔' as source_type,
            1 as sort_order,
            NULL as auto_number
        FROM gift_box_generate as gbg

        UNION ALL

        -- 禮盒生產單 (明細)
        SELECT 
            gbg.bpm_form_id,
            gbgd.s_item,
            gbgd.s_item_name,
            gbgd.unit,
            -gbgd.estimate_cost_quantity as estimate_cost_quantity,
            gbgd.s_item + gbg.cost_warehouse as key1,
            gbgd.s_item + gbg.cost_warehouse as key_word,
            gbg.cost_warehouse,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-明細' as source_type,
            2 as sort_order,
            NULL as auto_number
        FROM gift_box_generate as gbg
        INNER JOIN gift_box_generate_detail as gbgd on gbg.bpm_form_id = gbgd.bpm_form_id

        UNION ALL

        -- 出入庫單
        SELECT 
            iiod.bpm_form_id, 
            iiod.item as s_item, 
            iiod.product_name as s_item_name, 
            iiod.unit, 
            CASE 
                WHEN iiod.inventory_out = 0 THEN iiod.inventory_in
                WHEN iiod.inventory_in = 0 THEN -iiod.inventory_out
                ELSE 0
            END as estimate_cost_quantity,   
            iiod.item + iiod.warehouse as key1, 
            iiod.item + iiod.warehouse as key_word,
            iiod.warehouse as cost_warehouse, 
            CONVERT(VARCHAR(10), iio.issue_date, 23) as issue_date,
            '出入庫單' as source_type,
            3 as sort_order,
            NULL as auto_number
        FROM inventory_in_out as iio
        INNER JOIN inventory_in_out_detail as iiod on iio.bpm_form_id = iiod.bpm_form_id

        UNION ALL

        -- 銷售官網B2C
        SELECT 
            bpm_form_id, 
            item as s_item, 
            item_name as s_item_name, 
            unit, 
            inventory_num as estimate_cost_quantity, 
            key1, 
            key_word,
            warehouse_type as cost_warehouse, 
            CONVERT(VARCHAR(10), issue_date, 23) as issue_date,
            '銷售官網B2C' as source_type,
            4 as sort_order,
            auto_number
        FROM sales_order_b_to_c_inventory_detail

        UNION ALL

        -- 耗料單
        SELECT 
            co.bpm_form_id, 
            cod.s_item, 
            cod.s_item_name, 
            cod.unit, 
            -cod.estimate_consume as estimate_cost_quantity,
            cod.s_item + co.consume_warehouse as key1, 
            cod.s_item + co.consume_warehouse as key_word, 
            co.consume_warehouse as cost_warehouse,
            CONVERT(VARCHAR(10), co.issue_date, 23) as issue_date,
            '耗料單' as source_type,
            5 as sort_order,
            NULL as auto_number
        FROM consume_order as co
        INNER JOIN consume_order_detail as cod on co.bpm_form_id = cod.bpm_form_id

        UNION ALL

        -- 代工委託單
        SELECT 
            oo.bpm_form_id, 
            ood.item as s_item, 
            ood.item_name as s_item_name, 
            ood.unit, 
            ood.actual_inventory_in_num as estimate_cost_quantity,
            ood.item + oo.inventory_in_warehouse as key1, 
            ood.item + oo.inventory_in_warehouse as key_word, 
            oo.inventory_in_warehouse as cost_warehouse,
            CONVERT(VARCHAR(10), oo.issue_date, 23) as issue_date,
            '代工委託單' as source_type,
            6 as sort_order,
            NULL as auto_number
        FROM oem_order as oo
        INNER JOIN oem_order_detail as ood on oo.bpm_form_id = ood.bpm_form_id

        UNION ALL

        -- 心茶配送單
        SELECT 
            do.bpm_form_id, 
            dod.delivery_item as s_item, 
            dod.delivery_gift_box_name as s_item_name, 
            '' as unit, 
            -dod.box_num as estimate_cost_quantity, 
            dod.delivery_item + do.outbound_warehouse as key1, 
            dod.delivery_item + do.outbound_warehouse as key_word,
            do.outbound_warehouse as cost_warehouse, 
            CONVERT(VARCHAR(10), do.issue_date, 23) as issue_date,
            '心茶配送單' as source_type,
            7 as sort_order,
            NULL as auto_number
        FROM delivery_order as do
        INNER JOIN delivery_order_detail as dod on do.bpm_form_id = dod.bpm_form_id

        UNION ALL

        -- 心茶料號申請單
        SELECT 
            iad.bpm_form_id, 
            iad.item as s_item, 
            iad.item_name as s_item_name, 
            iad.unit, 
            0 as estimate_cost_quantity,
            iad.item + iad.warehouse_type as key1, 
            iad.item + iad.warehouse_type as key_word, 
            iad.warehouse_type as cost_warehouse,
            CONVERT(VARCHAR(10), iad.issue_date, 23) as issue_date,
            '心茶料號申請單' as source_type,
            8 as sort_order,
            NULL as auto_number
        FROM item_application_detail as iad
        
        UNION ALL

        --採購單
        select pu.bpm_form_id, pud.item as s_item, pud.product_name as s_item_name, pud.unit, pud.actual_warehousing_quantity as estimate_cost_quantity,
        pud.item+pu.complete_storage_warehouse as key1, pud.item+pu.complete_storage_warehouse as key_word, pu.complete_storage_warehouse as cost_warehouse,
        CONVERT(VARCHAR(10), pu.issue_date, 23) as issue_date, '採購單' as source_type, 9 as sort_order, NULL as auto_number
        FROM purchase as pu
        INNER JOIN purchase_detail as pud on pu.bpm_form_id = pud.bpm_form_id
            
        UNION ALL

        --開帳資料
        SELECT 
            '' as bpm_form_id, 
            io.s_item, iad.item_name as s_item_name, iad.unit, io.inventory_num as estimate_cost_quantity,
            io.s_item + io.warehouse_type as key1,
            io.s_item + io.warehouse_type as key_word,
            io.warehouse_type as cost_warehouse,
            CONVERT(VARCHAR(10), io.issue_date, 23) as issue_date,
            '開帳資料' as source_type,
            10 as sort_order,
            NULL as auto_number
        FROM inventory_opening as io
        INNER JOIN item_application_detail as iad on io.s_item = iad.item
    ) AS combined_inventory
    {where_sql}
    ORDER BY issue_date DESC, bpm_form_id, sort_order, auto_number"""
    return msq.s_qry(cmd, param)


def qry_inventory_subtotal(**kwargs) -> dict:
    """
    查詢庫存資料 - 樞紐分析表格式
    返回格式: {
        'warehouses': ['倉別1', '倉別2', ...],
        'data': [庫存資料]
    }
    """
    where_sql: str = " WHERE 1=1 AND ci.s_item <> ''"
    where_param: list = []  
    
    # 主查詢的條件
    if kwargs.get('warehouse') != '':
        warehouse_list = kwargs.get('warehouse').split(',')
        placeholders = ','.join(['?'] * len(warehouse_list))
        where_sql += f" AND ci.cost_warehouse IN ({placeholders}) "
        where_param.extend(warehouse_list)
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?'] * len(item_list))
        where_sql += f" AND ci.s_item IN ({placeholders}) "
        where_param.extend(item_list)
    
    # 開帳日期條件(排除心茶料號申請單)
    if kwargs.get('inventory_open_date') != '':
        where_sql += " AND (ci.issue_date >= ? OR ci.source_type = '心茶料號申請單') "
        where_param.append(kwargs.get('inventory_open_date'))

    having_sql: str = " HAVING 1=1 "
    if kwargs.get('is_inventory_diff_no_zero') == '1':
        having_sql += " AND CAST(SUM(ci.estimate_cost_quantity) AS DECIMAL(18, 2)) - (ISNULL(MAX(gs.total_gs_num), 0) + ISNULL(MAX(close_gs.total_gs_num), 0)) <> 0 "

    # GS 查詢的參數(單獨管理) - inventory_gs
    gs_inventory_sql: str = " WHERE 1=1 and bpm_form_id NOT LIKE '%資料%' and bpm_form_id NOT LIKE '%清洗%' "
    gs_param: list = []
    
    if kwargs.get('warehouse') != '':
        warehouse_list = kwargs.get('warehouse').split(',')
        placeholders = ','.join(['?'] * len(warehouse_list))
        gs_inventory_sql += f" AND warehouse_type IN ({placeholders}) "
        gs_param.extend(warehouse_list)
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?'] * len(item_list))
        gs_inventory_sql += f" AND item IN ({placeholders}) "
        gs_param.extend(item_list)
    if kwargs.get('inventory_open_date') != '':
        gs_inventory_sql += " AND issue_date >= ? "
        gs_param.append(kwargs.get('inventory_open_date'))

    # close_inventory_gs 查詢的參數
    close_gs_inventory_sql: str = " WHERE 1=1 "
    close_gs_param: list = []
    
    if kwargs.get('warehouse') != '':
        warehouse_list = kwargs.get('warehouse').split(',')
        placeholders = ','.join(['?'] * len(warehouse_list))
        close_gs_inventory_sql += f" AND warehouse_type IN ({placeholders}) "
        close_gs_param.extend(warehouse_list)
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?'] * len(item_list))
        close_gs_inventory_sql += f" AND item IN ({placeholders}) "
        close_gs_param.extend(item_list)
    if kwargs.get('inventory_open_date') != '':
        close_gs_inventory_sql += " AND issue_date >= ? "
        close_gs_param.append(kwargs.get('inventory_open_date'))

    # 查庫存sql
    warehouse_where_sql: str = " WHERE 1=1 "
    warehouse_param: list = []
    if kwargs.get('warehouse') != '':
        warehouse_list = kwargs.get('warehouse').split(',')
        placeholders = ','.join(['?'] * len(warehouse_list))
        warehouse_where_sql += f" AND cost_warehouse IN ({placeholders}) "
        warehouse_param.extend(warehouse_list)
    
    msq = XinTeaSql()
    
    # 取得所有倉別
    warehouse_cmd = f"""
    SELECT DISTINCT cost_warehouse 
    FROM (
        SELECT cost_warehouse FROM gift_box_generate WHERE cost_warehouse IS NOT NULL AND cost_warehouse != ''
        UNION
        SELECT consume_warehouse FROM consume_order WHERE consume_warehouse IS NOT NULL AND consume_warehouse != ''
        UNION
        SELECT inventory_in_warehouse FROM oem_order WHERE inventory_in_warehouse IS NOT NULL AND inventory_in_warehouse != ''
        UNION
        SELECT outbound_warehouse FROM delivery_order WHERE outbound_warehouse IS NOT NULL AND outbound_warehouse != ''
        UNION
        SELECT warehouse FROM inventory_in_out_detail WHERE warehouse IS NOT NULL AND warehouse != ''
        UNION
        SELECT warehouse_type FROM sales_order_b_to_c_inventory_detail WHERE warehouse_type IS NOT NULL AND warehouse_type != ''
        UNION
        SELECT warehouse_type FROM item_application_detail WHERE bpm_form_id LIKE '心茶料號申請單%' AND warehouse_type IS NOT NULL AND warehouse_type != ''
        UNION
        SELECT complete_storage_warehouse FROM purchase WHERE complete_storage_warehouse IS NOT NULL AND complete_storage_warehouse != ''
        UNION
        SELECT warehouse_type FROM inventory_opening WHERE warehouse_type IS NOT NULL AND warehouse_type != ''
    ) AS all_warehouses
    {warehouse_where_sql}
    ORDER BY cost_warehouse
    """
    warehouses_result = msq.qry(warehouse_cmd, warehouse_param)
    warehouses = [w['cost_warehouse'] for w in warehouses_result]
    
    # 動態生成 CASE WHEN 語句
    case_statements = []
    for warehouse_name in warehouses:
        case_statements.append(
            f"NULLIF(SUM(CASE WHEN ci.cost_warehouse = '{warehouse_name}' THEN ci.estimate_cost_quantity ELSE 0 END), 0) AS [{warehouse_name}]"
        )
    
    warehouse_columns = ',\n        '.join(case_statements) if case_statements else "''"
    
    # 組合所有參數
    final_param = gs_param + close_gs_param + where_param
    
    cmd: str = f"""
    WITH inventory_gs_summary AS (
        SELECT 
            item, 
            SUM(inventory_num) as total_gs_num
        FROM inventory_gs
        {gs_inventory_sql}
        GROUP BY item
    ),
    close_inventory_gs_summary AS (
        SELECT
             item,
             SUM(inventory_num) as total_gs_num
        FROM close_inventory_gs
        {close_gs_inventory_sql}
        GROUP BY item
    )
    SELECT 
        ci.s_item,
        MAX(iad.item_name) as s_item_name,
        {warehouse_columns},
        CAST(SUM(ci.estimate_cost_quantity) AS DECIMAL(18, 2)) AS total_inventory,
        ISNULL(MAX(gs.total_gs_num), 0) + ISNULL(MAX(close_gs.total_gs_num), 0) AS total_gs_num,
        CAST(SUM(ci.estimate_cost_quantity) AS DECIMAL(18, 2)) - ISNULL(MAX(gs.total_gs_num), 0) - ISNULL(MAX(close_gs.total_gs_num), 0) AS inventory_difference
    FROM (
        -- 禮盒生產單 (主檔)
        SELECT 
            gbg.item as s_item,
            gbg.cost_warehouse,
            gbg.complete_num as estimate_cost_quantity,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-主檔' as source_type
        FROM gift_box_generate as gbg

        UNION ALL

        -- 禮盒生產單 (明細)
        SELECT 
            gbgd.s_item,
            gbg.cost_warehouse,
            -gbgd.estimate_cost_quantity as estimate_cost_quantity,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-明細' as source_type
        FROM gift_box_generate as gbg
        INNER JOIN gift_box_generate_detail as gbgd on gbg.bpm_form_id = gbgd.bpm_form_id

        UNION ALL

        -- 出入庫單
        SELECT 
            iiod.item as s_item,
            iiod.warehouse as cost_warehouse,
            CASE 
                WHEN iiod.inventory_out = 0 THEN iiod.inventory_in
                WHEN iiod.inventory_in = 0 THEN -iiod.inventory_out
                ELSE 0
            END as estimate_cost_quantity,
            CONVERT(VARCHAR(10), iio.issue_date, 23) as issue_date,
            '出入庫單' as source_type
        FROM inventory_in_out as iio
        INNER JOIN inventory_in_out_detail as iiod on iio.bpm_form_id = iiod.bpm_form_id

        UNION ALL

        -- 銷售官網B2C
        SELECT 
            item as s_item,
            warehouse_type as cost_warehouse,
            inventory_num as estimate_cost_quantity,
            CONVERT(VARCHAR(10), issue_date, 23) as issue_date,
            '銷售官網B2C' as source_type
        FROM sales_order_b_to_c_inventory_detail

        UNION ALL

        -- 耗料單
        SELECT 
            cod.s_item,
            co.consume_warehouse as cost_warehouse,
            -cod.estimate_consume as estimate_cost_quantity,
            CONVERT(VARCHAR(10), co.issue_date, 23) as issue_date,
            '耗料單' as source_type
        FROM consume_order as co
        INNER JOIN consume_order_detail as cod on co.bpm_form_id = cod.bpm_form_id

        UNION ALL

        -- 代工委託單
        SELECT 
            ood.item as s_item,
            oo.inventory_in_warehouse as cost_warehouse,
            ood.actual_inventory_in_num as estimate_cost_quantity,
            CONVERT(VARCHAR(10), oo.issue_date, 23) as issue_date,
            '代工委託單' as source_type
        FROM oem_order as oo
        INNER JOIN oem_order_detail as ood on oo.bpm_form_id = ood.bpm_form_id

        UNION ALL

        -- 心茶配送單
        SELECT 
            dod.delivery_item as s_item,
            do.outbound_warehouse as cost_warehouse,
            -dod.box_num as estimate_cost_quantity,
            CONVERT(VARCHAR(10), do.issue_date, 23) as issue_date,
            '心茶配送單' as source_type
        FROM delivery_order as do
        INNER JOIN delivery_order_detail as dod on do.bpm_form_id = dod.bpm_form_id

        UNION ALL

        -- 心茶料號申請單(不受 inventory_open_date 限制)
        SELECT 
            iad.item as s_item,
            iad.warehouse_type as cost_warehouse,
            0 as estimate_cost_quantity,
            CONVERT(VARCHAR(10), iad.issue_date, 23) as issue_date,
            '心茶料號申請單' as source_type
        FROM item_application_detail as iad

        UNION ALL

        -- 採購單
        SELECT 
            pud.item as s_item,
            pu.complete_storage_warehouse as cost_warehouse,
            pud.actual_warehousing_quantity as estimate_cost_quantity,
            CONVERT(VARCHAR(10), pu.issue_date, 23) as issue_date,
            '採購單' as source_type
        FROM purchase as pu
        INNER JOIN purchase_detail as pud on pu.bpm_form_id = pud.bpm_form_id

        UNION ALL

        -- 開帳資料
        SELECT 
            io.s_item,
            io.warehouse_type as cost_warehouse,
            io.inventory_num as estimate_cost_quantity, 
            CONVERT(VARCHAR(10), io.issue_date, 23) as issue_date,
            '開帳資料' as source_type
        FROM inventory_opening as io
    ) AS ci
    LEFT JOIN (
        SELECT DISTINCT item, item_name
        FROM item_application_detail
    ) as iad ON ci.s_item = iad.item
    LEFT JOIN inventory_gs_summary as gs ON ci.s_item = gs.item
    LEFT JOIN close_inventory_gs_summary as close_gs ON ci.s_item = close_gs.item
    {where_sql}
    GROUP BY ci.s_item
    {having_sql}
    ORDER BY ci.s_item
    """
    data = msq.s_qry(cmd, final_param)
    
    return {
        'warehouses': warehouses,
        'data': data
    }


def qry_inventory_subtotal_warehouse_type() -> list:
    """查詢倉別(庫存樞紐用)"""
    msq = XinTeaSql()
    cmd: str = """
    SELECT DISTINCT cost_warehouse 
    FROM (
        SELECT cost_warehouse FROM gift_box_generate WHERE cost_warehouse IS NOT NULL AND cost_warehouse != ''
        UNION
        SELECT consume_warehouse FROM consume_order WHERE consume_warehouse IS NOT NULL AND consume_warehouse != ''
        UNION
        SELECT inventory_in_warehouse FROM oem_order WHERE inventory_in_warehouse IS NOT NULL AND inventory_in_warehouse != ''
        UNION
        SELECT outbound_warehouse FROM delivery_order WHERE outbound_warehouse IS NOT NULL AND outbound_warehouse != ''
        UNION
        SELECT warehouse FROM inventory_in_out_detail WHERE warehouse IS NOT NULL AND warehouse != ''
        UNION
        SELECT warehouse_type FROM sales_order_b_to_c_inventory_detail WHERE warehouse_type IS NOT NULL AND warehouse_type != ''
        UNION
        SELECT complete_storage_warehouse FROM purchase WHERE complete_storage_warehouse IS NOT NULL AND complete_storage_warehouse != ''
        UNION
        SELECT warehouse_type FROM item_application_detail WHERE bpm_form_id LIKE '心茶料號申請單%' AND warehouse_type IS NOT NULL AND warehouse_type != ''
    ) AS all_warehouses
    ORDER BY cost_warehouse
    """
    return msq.s_qry(cmd)


def qry_inventory_subtotal_item() -> list:
    """查詢所有料號(庫存樞紐用)"""
    msq = XinTeaSql()
    cmd: str = """
    SELECT DISTINCT s_item, s_item_name
    FROM (
        SELECT item as s_item, item_name as s_item_name 
        FROM gift_box_generate 
        WHERE item IS NOT NULL AND item != ''
        
        UNION
        
        SELECT s_item, s_item_name 
        FROM gift_box_generate_detail 
        WHERE s_item IS NOT NULL AND s_item != ''
        
        UNION
        
        SELECT item as s_item, product_name as s_item_name 
        FROM inventory_in_out_detail 
        WHERE item IS NOT NULL AND item != ''
        
        UNION
        
        SELECT item as s_item, item_name as s_item_name 
        FROM sales_order_b_to_c_inventory_detail 
        WHERE item IS NOT NULL AND item != ''
        
        UNION
        
        SELECT s_item, s_item_name 
        FROM consume_order_detail 
        WHERE s_item IS NOT NULL AND s_item != ''
        
        UNION
        
        SELECT item as s_item, item_name as s_item_name 
        FROM oem_order_detail 
        WHERE item IS NOT NULL AND item != ''
        
        UNION
        
        SELECT delivery_item as s_item, delivery_gift_box_name as s_item_name 
        FROM delivery_order_detail 
        WHERE delivery_item IS NOT NULL AND delivery_item != ''
        
        UNION
        
        SELECT item as s_item, item_name as s_item_name 
        FROM item_application_detail 
        WHERE bpm_form_id LIKE '心茶料號申請單%' 
        AND item IS NOT NULL AND item != ''
    ) AS all_items
    ORDER BY s_item
    """
    return msq.s_qry(cmd)


def add_inventory_gs(add: list) -> bool:
    """
    新增GS出入明細
    :param add: list 新增資料
    """
    msq = XinTeaSql()
    cmd: str = """INSERT INTO inventory_gs(item, item_name, unit, 
                  inventory_num, bpm_form_id, key1, key_word, 
                  warehouse_type, issue_date, write_time) VALUES(?,?,?,?,?,?,?,?,?,?)"""
    delete_cmd: str = "DELETE FROM inventory_gs"
    cmds_param: list = [
        (delete_cmd, [()]),
        (
            cmd, add
        )
    ]
    return msq.transaction_v2(cmds_param)


def qry_item() -> list:
    """查詢料號(庫存明細用)"""
    msq = XinTeaSql()
    cmd: str = """SELECT 
        DISTINCT ci.s_item, iad.item_name as s_item_name
    FROM (
        -- 禮盒生產單 (主檔)
        SELECT 
            gbg.bpm_form_id,
            gbg.item as s_item,
            gbg.item_name as s_item_name,
            NULL as unit,
            gbg.complete_num as estimate_cost_quantity,
            gbg.item + gbg.cost_warehouse as key1,
            gbg.item + gbg.cost_warehouse as key_word,
            gbg.cost_warehouse,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-主檔' as source_type,
            1 as sort_order,
            NULL as auto_number
        FROM gift_box_generate as gbg

        UNION ALL

        -- 禮盒生產單 (明細)
        SELECT 
            gbg.bpm_form_id,
            gbgd.s_item,
            gbgd.s_item_name,
            gbgd.unit,
            -gbgd.estimate_cost_quantity as estimate_cost_quantity,
            gbgd.s_item + gbg.cost_warehouse as key1,
            gbgd.s_item + gbg.cost_warehouse as key_word,
            gbg.cost_warehouse,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-明細' as source_type,
            2 as sort_order,
            NULL as auto_number
        FROM gift_box_generate as gbg
        INNER JOIN gift_box_generate_detail as gbgd on gbg.bpm_form_id = gbgd.bpm_form_id

        UNION ALL

        -- 出入庫單
        SELECT 
            iiod.bpm_form_id, 
            iiod.item as s_item, 
            iiod.product_name as s_item_name, 
            iiod.unit, 
            CASE 
                WHEN iiod.inventory_out = 0 THEN iiod.inventory_in
                WHEN iiod.inventory_in = 0 THEN -iiod.inventory_out
                ELSE 0
            END as estimate_cost_quantity,   
            iiod.item + iiod.warehouse as key1, 
            iiod.item + iiod.warehouse as key_word,
            iiod.warehouse as cost_warehouse, 
            CONVERT(VARCHAR(10), iio.issue_date, 23) as issue_date,
            '出入庫單' as source_type,
            3 as sort_order,
            NULL as auto_number
        FROM inventory_in_out as iio
        INNER JOIN inventory_in_out_detail as iiod on iio.bpm_form_id = iiod.bpm_form_id

        UNION ALL

        -- 銷售官網B2C
        SELECT 
            bpm_form_id, 
            item as s_item, 
            item_name as s_item_name, 
            unit, 
            inventory_num as estimate_cost_quantity, 
            key1, 
            key_word,
            warehouse_type as cost_warehouse, 
            CONVERT(VARCHAR(10), issue_date, 23) as issue_date,
            '銷售官網B2C' as source_type,
            4 as sort_order,
            auto_number
        FROM sales_order_b_to_c_inventory_detail

        UNION ALL

        -- 耗料單
        SELECT 
            co.bpm_form_id, 
            cod.s_item, 
            cod.s_item_name, 
            cod.unit, 
            -cod.estimate_consume as estimate_cost_quantity,
            cod.s_item + co.consume_warehouse as key1, 
            cod.s_item + co.consume_warehouse as key_word, 
            co.consume_warehouse as cost_warehouse,
            CONVERT(VARCHAR(10), co.issue_date, 23) as issue_date,
            '耗料單' as source_type,
            5 as sort_order,
            NULL as auto_number
        FROM consume_order as co
        INNER JOIN consume_order_detail as cod on co.bpm_form_id = cod.bpm_form_id

        UNION ALL

        -- 代工委託單
        SELECT 
            oo.bpm_form_id, 
            ood.item as s_item, 
            ood.item_name as s_item_name, 
            ood.unit, 
            ood.actual_inventory_in_num as estimate_cost_quantity,
            ood.item + oo.inventory_in_warehouse as key1, 
            ood.item + oo.inventory_in_warehouse as key_word, 
            oo.inventory_in_warehouse as cost_warehouse,
            CONVERT(VARCHAR(10), oo.issue_date, 23) as issue_date,
            '代工委託單' as source_type,
            6 as sort_order,
            NULL as auto_number
        FROM oem_order as oo
        INNER JOIN oem_order_detail as ood on oo.bpm_form_id = ood.bpm_form_id

        UNION ALL

        -- 心茶配送單
        SELECT 
            do.bpm_form_id, 
            dod.delivery_item as s_item, 
            dod.delivery_gift_box_name as s_item_name, 
            '' as unit, 
            -dod.box_num as estimate_cost_quantity, 
            dod.delivery_item + do.outbound_warehouse as key1, 
            dod.delivery_item + do.outbound_warehouse as key_word,
            do.outbound_warehouse as cost_warehouse, 
            CONVERT(VARCHAR(10), do.issue_date, 23) as issue_date,
            '心茶配送單' as source_type,
            7 as sort_order,
            NULL as auto_number
        FROM delivery_order as do
        INNER JOIN delivery_order_detail as dod on do.bpm_form_id = dod.bpm_form_id

        UNION ALL

        -- 心茶料號申請單
        SELECT 
            iad.bpm_form_id, 
            iad.item as s_item, 
            iad.item_name as s_item_name, 
            iad.unit, 
            0 as estimate_cost_quantity,
            iad.item + iad.warehouse_type as key1, 
            iad.item + iad.warehouse_type as key_word, 
            iad.warehouse_type as cost_warehouse,
            CONVERT(VARCHAR(10), iad.issue_date, 23) as issue_date,
            '心茶料號申請單' as source_type,
            8 as sort_order,
            NULL as auto_number
        FROM item_application_detail as iad
        WHERE iad.bpm_form_id LIKE '心茶料號申請單%'

        UNION ALL
        --採購單
        select pu.bpm_form_id, pud.item as s_item, pud.product_name as s_item_name, pud.unit, pud.actual_warehousing_quantity as estimate_cost_quantity,
        pud.item+pu.complete_storage_warehouse as key1, pud.item+pu.complete_storage_warehouse as key_word, pu.complete_storage_warehouse as cost_warehouse,
        CONVERT(VARCHAR(10), pu.issue_date, 23) as issue_date,
        '採購單' as source_type, 9 as sort_order, NULL as auto_number
        FROM purchase as pu
        INNER JOIN purchase_detail as pud on pu.bpm_form_id = pud.bpm_form_id

    ) AS ci
    INNER JOIN item_application_detail as iad ON ci.s_item = iad.item
    ORDER BY s_item"""
    return msq.s_qry(cmd)



def qry_warehouse() -> list:
    """查詢料號(庫存明細用)"""
    msq = XinTeaSql()
    cmd: str = """SELECT 
        DISTINCT cost_warehouse
    FROM (
        -- 禮盒生產單 (主檔)
        SELECT 
            gbg.bpm_form_id,
            gbg.item as s_item,
            gbg.item_name as s_item_name,
            NULL as unit,
            gbg.complete_num as estimate_cost_quantity,
            gbg.item + gbg.cost_warehouse as key1,
            gbg.item + gbg.cost_warehouse as key_word,
            gbg.cost_warehouse,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-主檔' as source_type,
            1 as sort_order,
            NULL as auto_number
        FROM gift_box_generate as gbg

        UNION ALL

        -- 禮盒生產單 (明細)
        SELECT 
            gbg.bpm_form_id,
            gbgd.s_item,
            gbgd.s_item_name,
            gbgd.unit,
            -gbgd.estimate_cost_quantity as estimate_cost_quantity,
            gbgd.s_item + gbg.cost_warehouse as key1,
            gbgd.s_item + gbg.cost_warehouse as key_word,
            gbg.cost_warehouse,
            CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date,
            '禮盒生產單-明細' as source_type,
            2 as sort_order,
            NULL as auto_number
        FROM gift_box_generate as gbg
        INNER JOIN gift_box_generate_detail as gbgd on gbg.bpm_form_id = gbgd.bpm_form_id

        UNION ALL

        -- 出入庫單
        SELECT 
            iiod.bpm_form_id, 
            iiod.item as s_item, 
            iiod.product_name as s_item_name, 
            iiod.unit, 
            CASE 
                WHEN iiod.inventory_out = 0 THEN iiod.inventory_in
                WHEN iiod.inventory_in = 0 THEN -iiod.inventory_out
                ELSE 0
            END as estimate_cost_quantity,   
            iiod.item + iiod.warehouse as key1, 
            iiod.item + iiod.warehouse as key_word,
            iiod.warehouse as cost_warehouse, 
            CONVERT(VARCHAR(10), iio.issue_date, 23) as issue_date,
            '出入庫單' as source_type,
            3 as sort_order,
            NULL as auto_number
        FROM inventory_in_out as iio
        INNER JOIN inventory_in_out_detail as iiod on iio.bpm_form_id = iiod.bpm_form_id

        UNION ALL

        -- 銷售官網B2C
        SELECT 
            bpm_form_id, 
            item as s_item, 
            item_name as s_item_name, 
            unit, 
            inventory_num as estimate_cost_quantity, 
            key1, 
            key_word,
            warehouse_type as cost_warehouse, 
            CONVERT(VARCHAR(10), issue_date, 23) as issue_date,
            '銷售官網B2C' as source_type,
            4 as sort_order,
            auto_number
        FROM sales_order_b_to_c_inventory_detail

        UNION ALL

        -- 耗料單
        SELECT 
            co.bpm_form_id, 
            cod.s_item, 
            cod.s_item_name, 
            cod.unit, 
            -cod.estimate_consume as estimate_cost_quantity,
            cod.s_item + co.consume_warehouse as key1, 
            cod.s_item + co.consume_warehouse as key_word, 
            co.consume_warehouse as cost_warehouse,
            CONVERT(VARCHAR(10), co.issue_date, 23) as issue_date,
            '耗料單' as source_type,
            5 as sort_order,
            NULL as auto_number
        FROM consume_order as co
        INNER JOIN consume_order_detail as cod on co.bpm_form_id = cod.bpm_form_id

        UNION ALL

        -- 代工委託單
        SELECT 
            oo.bpm_form_id, 
            ood.item as s_item, 
            ood.item_name as s_item_name, 
            ood.unit, 
            ood.actual_inventory_in_num as estimate_cost_quantity,
            ood.item + oo.inventory_in_warehouse as key1, 
            ood.item + oo.inventory_in_warehouse as key_word, 
            oo.inventory_in_warehouse as cost_warehouse,
            CONVERT(VARCHAR(10), oo.issue_date, 23) as issue_date,
            '代工委託單' as source_type,
            6 as sort_order,
            NULL as auto_number
        FROM oem_order as oo
        INNER JOIN oem_order_detail as ood on oo.bpm_form_id = ood.bpm_form_id

        UNION ALL

        -- 心茶配送單
        SELECT 
            do.bpm_form_id, 
            dod.delivery_item as s_item, 
            dod.delivery_gift_box_name as s_item_name, 
            '' as unit, 
            -dod.box_num as estimate_cost_quantity, 
            dod.delivery_item + do.outbound_warehouse as key1, 
            dod.delivery_item + do.outbound_warehouse as key_word,
            do.outbound_warehouse as cost_warehouse, 
            CONVERT(VARCHAR(10), do.issue_date, 23) as issue_date,
            '心茶配送單' as source_type,
            7 as sort_order,
            NULL as auto_number
        FROM delivery_order as do
        INNER JOIN delivery_order_detail as dod on do.bpm_form_id = dod.bpm_form_id

        UNION ALL

        -- 心茶料號申請單
        SELECT 
            iad.bpm_form_id, 
            iad.item as s_item, 
            iad.item_name as s_item_name, 
            iad.unit, 
            0 as estimate_cost_quantity,
            iad.item + iad.warehouse_type as key1, 
            iad.item + iad.warehouse_type as key_word, 
            iad.warehouse_type as cost_warehouse,
            CONVERT(VARCHAR(10), iad.issue_date, 23) as issue_date,
            '心茶料號申請單' as source_type,
            8 as sort_order,
            NULL as auto_number
        FROM item_application_detail as iad
        WHERE iad.bpm_form_id LIKE '心茶料號申請單%'

        UNION ALL

        --採購單
        select pu.bpm_form_id, pud.item as s_item, pud.product_name as s_item_name, pud.unit, pud.actual_warehousing_quantity as estimate_cost_quantity,
        pud.item+pu.complete_storage_warehouse as key1, pud.item+pu.complete_storage_warehouse as key_word, pu.complete_storage_warehouse as cost_warehouse,
        CONVERT(VARCHAR(10), pu.issue_date, 23) as issue_date,
        '採購單' as source_type, 9 as sort_order, NULL as auto_number
        FROM purchase as pu
        INNER JOIN purchase_detail as pud on pu.bpm_form_id = pud.bpm_form_id

    ) AS ci
    ORDER BY cost_warehouse"""
    return msq.s_qry(cmd)


def insert_vendor_arrival_data(add: list) -> bool:
    """
    新增廠商到貨區間
    """
    msq = XinTeaSql()
    cmd: str = """INSERT INTO vendor_arrival_area_b_to_c
                  (generate_vendor, arrival_area_key, to_order_generate_date,
                  earliest_factory_date, earliest_arrival_date, to_generate_vendor,
                  logistics_list_ch) VALUES(?,?,?,?,?,?,?)"""
    cmds_param: list = [
        (
            cmd, add
        )
    ]
    return msq.transaction_v2(cmds_param)


def add_inventory_gs_data(add_data: list) -> bool:
    """新增開帳資料"""
    msq = XinTeaSql()
    cmd: str = """INSERT INTO inventory_opening(s_item, inventory_num, warehouse_type, issue_date) VALUES(?,?,?,?)"""
    cmds_param: list = [
        (
            cmd, add_data
        )
    ]
    return msq.transaction_v2(cmds_param)


def qry_inventory_gs_diff(**kwargs) -> list:
    """
    查詢 GS 與資料庫的差異
    """
    inventory_open_date = kwargs.get('inventory_open_date')
    
    msq = XinTeaSql()
    cmd: str = f"""
    -- 情況1: GS 或 close_GS 有但資料庫沒有
    SELECT DISTINCT 
        ig.bpm_form_id,
        CONVERT(VARCHAR(10), ig.issue_date, 23) as issue_date,
        'GS有但資料庫沒有' as status,
        1 as sort_order
    FROM inventory_gs AS ig
    WHERE ig.issue_date >= ?
        AND ig.bpm_form_id IS NOT NULL 
        AND ig.bpm_form_id != ''
        AND NOT EXISTS (
            SELECT 1
            FROM (
              SELECT gbg.bpm_form_id FROM gift_box_generate as gbg
              UNION
              SELECT iio.bpm_form_id FROM inventory_in_out as iio
              UNION
              SELECT bpm_form_id FROM sales_order_b_to_c_inventory_detail 
              WHERE bpm_form_id IS NOT NULL AND bpm_form_id != ''
              UNION
              SELECT co.bpm_form_id FROM consume_order as co
              UNION
              SELECT oo.bpm_form_id FROM oem_order as oo
              UNION
              SELECT do.bpm_form_id FROM delivery_order as do
              UNION
              SELECT iad.bpm_form_id FROM item_application_detail as iad
              WHERE iad.bpm_form_id LIKE '心茶料號申請單%'
              UNION
              SELECT pu.bpm_form_id FROM purchase as pu
            ) AS all_sources
            WHERE all_sources.bpm_form_id = ig.bpm_form_id
        ) AND (ig.bpm_form_id NOT LIKE '%資料%' AND ig.bpm_form_id NOT LIKE '%清洗%')
    
    UNION ALL
    
    SELECT DISTINCT 
        cig.bpm_form_id,
        CONVERT(VARCHAR(10), cig.issue_date, 23) as issue_date,
        'GS有但資料庫沒有' as status,
        1 as sort_order
    FROM close_inventory_gs AS cig
    WHERE cig.issue_date >= ?
        AND cig.bpm_form_id IS NOT NULL 
        AND cig.bpm_form_id != ''
        AND NOT EXISTS (
            SELECT 1
            FROM (
              SELECT gbg.bpm_form_id FROM gift_box_generate as gbg
              UNION
              SELECT iio.bpm_form_id FROM inventory_in_out as iio
              UNION
              SELECT bpm_form_id FROM sales_order_b_to_c_inventory_detail 
              WHERE bpm_form_id IS NOT NULL AND bpm_form_id != ''
              UNION
              SELECT co.bpm_form_id FROM consume_order as co
              UNION
              SELECT oo.bpm_form_id FROM oem_order as oo
              UNION
              SELECT do.bpm_form_id FROM delivery_order as do
              UNION
              SELECT iad.bpm_form_id FROM item_application_detail as iad
              WHERE iad.bpm_form_id LIKE '心茶料號申請單%'
              UNION
              SELECT pu.bpm_form_id FROM purchase as pu
            ) AS all_sources
            WHERE all_sources.bpm_form_id = cig.bpm_form_id
        ) AND cig.bpm_form_id NOT LIKE '%資料%'
    
    UNION ALL

    -- 情況2: 資料庫有但 GS 和 close_GS 都沒有
    SELECT DISTINCT 
        src.bpm_form_id,
        src.issue_date,
        '資料庫有但GS沒有' as status,
        2 as sort_order
    FROM (
        SELECT gbg.bpm_form_id, CONVERT(VARCHAR(10), gbg.issue_date, 23) as issue_date 
        FROM gift_box_generate as gbg
        WHERE gbg.issue_date >= ?
        
        UNION
        
        SELECT iio.bpm_form_id, CONVERT(VARCHAR(10), iio.issue_date, 23) as issue_date 
        FROM inventory_in_out as iio
        WHERE iio.issue_date >= ?
        
        UNION
        
        SELECT bpm_form_id, CONVERT(VARCHAR(10), issue_date, 23) as issue_date 
        FROM sales_order_b_to_c_inventory_detail 
        WHERE bpm_form_id IS NOT NULL AND bpm_form_id != ''
        AND issue_date >= ?
        
        UNION
        
        SELECT co.bpm_form_id, CONVERT(VARCHAR(10), co.issue_date, 23) as issue_date 
        FROM consume_order as co
        WHERE co.issue_date >= ?
        
        UNION
        
        SELECT oo.bpm_form_id, CONVERT(VARCHAR(10), oo.issue_date, 23) as issue_date 
        FROM oem_order as oo
        WHERE oo.issue_date >= ?
        
        UNION
        
        SELECT do.bpm_form_id, CONVERT(VARCHAR(10), do.issue_date, 23) as issue_date 
        FROM delivery_order as do
        WHERE do.issue_date >= ?
        
        UNION
        
        SELECT iad.bpm_form_id, CONVERT(VARCHAR(10), iad.issue_date, 23) as issue_date 
        FROM item_application_detail as iad
        WHERE iad.bpm_form_id LIKE '心茶料號申請單%'
        AND iad.issue_date >= ?
        
        UNION
        
        SELECT pu.bpm_form_id, CONVERT(VARCHAR(10), pu.issue_date, 23) as issue_date 
        FROM purchase as pu
        WHERE pu.issue_date >= ?
    ) AS src
    WHERE NOT EXISTS (
        SELECT 1
        FROM inventory_gs AS ig
        WHERE ig.bpm_form_id = src.bpm_form_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM close_inventory_gs AS cig
        WHERE cig.bpm_form_id = src.bpm_form_id
    )
    AND src.bpm_form_id NOT LIKE '%資料%'

    ORDER BY sort_order, issue_date DESC, bpm_form_id
    """
    param = [inventory_open_date] * 10
    
    return msq.s_qry(cmd, param)


def add_close_inventory_gs(add: list, delete_param: list) -> bool:
    """
    新增GS(打包資料)
    :param add: list 新增資料
    :param delete_param: list 刪除資料
    """
    msq = XinTeaSql()
    cmd: str = """INSERT INTO close_inventory_gs(item, item_name, unit, 
                  inventory_num, bpm_form_id, key1, key_word, 
                  warehouse_type, issue_date, write_time, gs_url) VALUES(?,?,?,?,?,?,?,?,?,?,?)"""
    delete_cmd: str = """DELETE FROM close_inventory_gs WHERE gs_url = ?"""
    cmds_param: list = [
        (
            delete_cmd, delete_param
        ),
        (
            cmd, add
        )
    ]
    return msq.transaction_v2(cmds_param)