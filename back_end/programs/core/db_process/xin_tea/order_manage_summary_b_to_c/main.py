from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_order_manage_summary_b_to_c(**kwargs) -> list:
    """
    查詢訂單管理總表
    """
    where_sql: str = 'WHERE 1=1'
    param: list = []
    if kwargs.get('e_commerce_platform') != '':
        e_commerce_platform_list = kwargs.get('e_commerce_platform').split(',')
        placeholders = ','.join(['?' for _ in range(len(e_commerce_platform_list))])
        where_sql += f' AND om.e_commerce_platform IN ({placeholders})'
        param.extend(e_commerce_platform_list)
    if kwargs.get('e_commerce_platform_order_no') != '':
        e_commerce_platform_order_no_list = kwargs.get('e_commerce_platform_order_no').split(',')
        placeholders = ','.join(['?' for _ in range(len(e_commerce_platform_order_no_list))])
        where_sql += f' AND om.e_commerce_platform_order_no IN ({placeholders})'
        param.extend(e_commerce_platform_order_no_list)
    if kwargs.get('status') != '':
        status_list = kwargs.get('status').split(',')
        placeholders = ','.join(['?' for _ in range(len(status_list))])
        where_sql += f' AND om.status IN ({placeholders})'
        param.extend(status_list)
    if kwargs.get('vendor_status') != '':
        vendor_status_list = kwargs.get('vendor_status').split(',')
        placeholders = ','.join(['?' for _ in range(len(vendor_status_list))])
        where_sql += f' AND latest_vob.vendor_order_status IN ({placeholders})'
        param.extend(vendor_status_list)
    if kwargs.get('vendor_check') != '':
        vendor_check_list = kwargs.get('vendor_check').split(',')
        placeholders = ','.join(['?' for _ in range(len(vendor_check_list))])
        where_sql += f' AND latest_vob.vendor_check IN ({placeholders})'
        param.extend(vendor_check_list)
    if kwargs.get('is_check_remark_message') != '':
        is_check_remark_message_list = kwargs.get('is_check_remark_message').split(',')
        placeholders = ','.join(['?' for _ in range(len(is_check_remark_message_list))])
        where_sql += f' AND om.is_check_remark_message IN ({placeholders})'
        param.extend(is_check_remark_message_list)
    if kwargs.get('to_order_generate_date_start') != '' and kwargs.get('to_order_generate_date_end') != '':
        where_sql += ' AND om.to_order_generate_date BETWEEN ? AND ?'
        param.append(kwargs.get('to_order_generate_date_start'))
        param.append(kwargs.get('to_order_generate_date_end'))
    if kwargs.get('earliest_arrival_date_start') != '' and kwargs.get('earliest_arrival_date_end') != '':
        where_sql += ' AND om.earliest_arrival_date BETWEEN ? AND ?'
        param.append(kwargs.get('earliest_arrival_date_start'))
        param.append(kwargs.get('earliest_arrival_date_end'))
    if kwargs.get('generate_vendor') != '':
        generate_vendor_list = kwargs.get('generate_vendor').split(',')
        placeholders = ','.join(['?' for _ in range(len(generate_vendor_list))])
        where_sql += f' AND om.generate_vendor IN ({placeholders})'
        param.extend(generate_vendor_list)
    if kwargs.get('delivery_vendor') != '':
        delivery_vendor_list = kwargs.get('delivery_vendor').split(',')
        placeholders = ','.join(['?' for _ in range(len(delivery_vendor_list))])
        where_sql += f' AND om.delivery_vendor IN ({placeholders})'
        param.extend(delivery_vendor_list)
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?' for _ in range(len(item_list))])
        where_sql += f' AND om.item IN ({placeholders})'
        param.extend(item_list)
    if kwargs.get('latest_arrival_date_start') != '' and kwargs.get('latest_arrival_date_end') != '':
        where_sql += ' AND om.latest_arrival_date BETWEEN ? AND ?'
        param.append(kwargs.get('latest_arrival_date_start'))
        param.append(kwargs.get('latest_arrival_date_end'))
    if kwargs.get('check_message_order_yes') == '1' and kwargs.get('check_message_order_no') == '1':
        pass
    elif kwargs.get('check_message_order_yes') == '1':
        where_sql += " AND om.check_message IS NOT NULL AND om.check_message <> ''"
    elif kwargs.get('check_message_order_no') == '1':
        where_sql += " AND (om.check_message IS NULL OR om.check_message = '')"
    if kwargs.get('import_date') != '':
        where_sql += ' AND CONVERT(VARCHAR, om.import_date, 23) = ?'
        param.append(kwargs.get('import_date'))
    msq = XinTeaSql()
    cmd = f"""
        -- 第一層 CTE：原始查詢資料
        WITH BaseData AS (
            SELECT om.already_order_order_status, so.step AS b2c_order_is_can_sign, so.status AS b2c_order_status, om.b2c_bpm_form_id,
                om.estimate_num_and_check, om.eip_import_label, om.package_factory_import_label, om.split_berfore_order_no,
                om.common_order_no_different_vendor, CONVERT(varchar, om.common_order_no_different_shipping_date, 23) AS common_order_no_different_shipping_date, 
                CONVERT(varchar, om.latest_arrival_date, 23) AS latest_arrival_date,
                om.white_list_process, om.is_check_remark_message, om.delivery_vendor,
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
                CASE WHEN om.complete_order_error = 1 THEN '1' ELSE '0' END AS complete_order_error,
                CASE WHEN latest_vob.vendor_check = 1 THEN '1' ELSE '0' END AS vendor_check,
                om.status, om.check_message, latest_vob.vendor_order_status, om.unit,
                CONVERT(varchar, om.spread_calculate_time, 120) AS spread_calculate_time,
                CONVERT(varchar, latest_vob.import_date, 120) AS to_vendor_time,
                latest_vob.importer AS to_vendor_user, om.original_money, om.exchange, om.currency_type,
                -- 用於排序的欄位
                om.import_date AS sort_import_date,
                LAG(om.e_commerce_platform_order_no) OVER (
                    ORDER BY om.import_date DESC, om.order_key, om.e_commerce_platform, om.e_commerce_platform_order_no, om.item
                ) AS prev_order_no
            FROM order_manage_summary_b_to_c as om
            LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id 
            OUTER APPLY (
                SELECT TOP 1 *
                FROM vendor_order_b_to_c
                WHERE order_key = om.order_key
                ORDER BY import_date DESC
            ) AS latest_vob
            {where_sql}
        ),
        -- 第二層 CTE：計算變更次數
        DataWithChangeCount AS (
            SELECT 
                *,
                SUM(CASE 
                    WHEN prev_order_no IS NULL OR e_commerce_platform_order_no <> prev_order_no 
                    THEN 1 
                    ELSE 0 
                END) OVER (
                    ORDER BY sort_import_date DESC, order_key, e_commerce_platform, e_commerce_platform_order_no, item 
                    ROWS UNBOUNDED PRECEDING
                ) AS change_count
            FROM BaseData
        )
        -- 最終查詢：加入 branch_line
        SELECT 
            already_order_order_status, b2c_order_is_can_sign, b2c_order_status, b2c_bpm_form_id,
            estimate_num_and_check, eip_import_label, package_factory_import_label, split_berfore_order_no,
            common_order_no_different_vendor, common_order_no_different_shipping_date, latest_arrival_date,
            white_list_process, is_check_remark_message, to_order_generate_date, earliest_arrival_date,
            generate_vendor, shipping_out_warehouse, e_commerce_platform_order_no, e_commerce_platform,
            e_commerce_platform_order_date, new_order_order_status, new_order_payment_status, logistics_method,
            order_remark_or_shipping_remark, item, product_name, item_category, bom_bpm_form_id, platform_product_name,
            platform_specific, quantity, recipient, recipient_phone, recipient_address, recipient_email, payment_term,
            order_money, invoice_title, uniform_invoice_no, sender, sender_phone, order_key, arrival_area,
            importer, import_date, google_sheet_url, google_sheet_name, xin_tea_remark, to_vendor,
            complete_order_error, vendor_check, status, check_message, vendor_order_status, unit,
            spread_calculate_time, to_vendor_time, to_vendor_user, original_money, exchange, currency_type,
            delivery_vendor,
            -- 根據變更次數決定符號
            CASE 
                WHEN change_count % 2 = 1 THEN '○○'
                ELSE 'Ⅹ'
            END AS branch_line
        FROM DataWithChangeCount
        ORDER BY sort_import_date DESC, order_key, e_commerce_platform, e_commerce_platform_order_no, item
    """
    return msq.s_qry(cmd, param)


def crt_order_manage_summary_b_to_c_and_update_import_data(order: list, import_data: list, platform: str) -> list:
    """
    新增訂單管理總表(B to C)&匯入資料
    :param order: 訂單資料
    :param import_data: 匯入資料
    :param platform: 電商平台
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO order_manage_summary_b_to_c (
                already_order_order_status, b2c_order_is_can_sign, b2c_order_status, b2c_bpm_form_id,
                estimate_num_and_check, eip_import_label, package_factory_import_label, split_berfore_order_no,
                common_order_no_different_vendor, common_order_no_different_shipping_date, latest_arrival_date,
                white_list_process, is_check_remark_message, to_order_generate_date, earliest_arrival_date,
                generate_vendor, shipping_out_warehouse, e_commerce_platform_order_no, e_commerce_platform,
                e_commerce_platform_order_date, new_order_order_status, new_order_payment_status, logistics_method,
                order_remark_or_shipping_remark, item, product_name, item_category, bom_bpm_form_id, platform_product_name,
                platform_specific, quantity, recipient, recipient_phone, recipient_address, recipient_email, payment_term,
                original_money, exchange, currency_type, order_money, invoice_title, uniform_invoice_no, sender, sender_phone, order_key, arrival_area, google_sheet_url,
                importer, import_date, arrival_area_split, status, unit, xin_tea_remark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    import_cmd: str = ''
    if platform == 'line 禮物':
        import_cmd = """INSERT INTO line_gift_import_new_order(order_no, product_order_no, 
        order_status, product_name, specifications, custom_engraving_options, product_id, seller_product_code, item_id, brand_number, 
        brand_name, quantity, price, discount, cost, total_product_amount, coupon_money, freight, order_placement_date, payment_complete_date, 
        write_address_date, order_check_date, shipping_date, shipping_complete_date, logistics_method, freight_forwarder, logistics_order_number, 
        combine_shipping_group_number, freight_type, recipient, recipient_phone, shipping_address, postal_code, shipping_message, default_shipping_address, 
        purchase_type, payment_term, order_device, invoice_number, initiator, get_point, estimated_delivery_date_of_award, order_coupon_main_id, order_coupon_title) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    elif platform == 'pinkoi':
        import_cmd = """INSERT INTO pinkoi_import_new_order(order_date, order_status, order_id, purchase_name, recipient_name, 
        recipient_address, recipient_phone, logistics_method, shipping_id, shipping_area, purchase_item, item_specific, item_id, quantity, 
        product_price, total, freight, cash_flow_handling_fee, discount, total_amount, payment_term, currency, back_num, back_product_amount, 
        full_refund, refund_complete, back_total_amount, purchase_not_recipient, purchase, purchase_address, purchase_phone, invoice_title, 
        uniform_invoice_no, purchase_remark, order_shipping_date, track_number, paid_at, electronic_invoice_carrier, invoice_number, invoice_date, 
        allowance_number, allowance_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    elif platform == 'shopline':
        import_cmd = """INSERT INTO shopline_import_new_order(order_no, order_status, payment_status, order_date, logistics_method, order_remark, 
        shipping_remark, product_id, product_name, choose, quantity, recipient, recipient_phone, recipient_address, email, payment_term, payment_total_amount, 
        invoice_title, uniform_invoice_no, custom_order_field2, custom_order_field3) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cmds_param: list = []
    if order:
        cmds_param.append((cmd, order))
    #if import_data:
    #    cmds_param.append((import_cmd, import_data))
    return msq.transaction_v2(cmds_param)


def qry_item_data(item_id: str) -> list:
    """
    查詢料件資料
    :param item_id: 料件編號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_application_detail where item=?"""
    return msq.s_qry(cmd, item_id)


def qry_arrival_area(arrival_area_key: str) -> list:
    """
    查詢到貨區間
    :param arrival_area_key: 到貨區間key值
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM arrival_area where arrival_area_key=?"""
    return msq.s_qry(cmd, arrival_area_key)


def qry_logistics_in_jyun_mao(methods: str) -> list:
    """
    查詢物流方法是否在均茂物流表
    :param methods: 物流方法
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM to_jyun_mao_logistics where logistic_methods=? and exist='1'"""
    return msq.s_qry(cmd, methods)


def qry_item_id_in_jyun_mao(item_id: str) -> list:
    """
    查詢料件是否在均茂料件表
    :param item_id: 料件編號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM to_jyun_mao_item where item=? and exist='1'"""
    return msq.s_qry(cmd, item_id)


def qry_vendor_consume_warehouse(vendor_id: str) -> list:
    """
    查詢廠商的耗料倉別
    :param vendor_id: 廠商編號
    """
    msq = XinTeaSql()
    cmd = """SELECT v.consume_warehouse FROM vendor as v
             INNER JOIN vendor_condition_b_to_c as vc on vc.vendor = v.vendor_name
             where vc.row_number=?"""
    return msq.s_qry(cmd, vendor_id)


def qry_vendor_earliest_arrival_date(vendor_id: str, arrival_area_key: str, logistics_method: str) -> list:
    """
    查詢廠商最早到貨日期
    :param vendor_id: 廠商編號
    :param arrival_area_key: 到貨區間key值
    :param logistics_method: 物流方式
    """
    where_sql: str = "WHERE 1=1 AND generate_vendor = ? AND arrival_area_key = ?"
    param: list = [vendor_id, arrival_area_key]
    if logistics_method == '':
        where_sql += " AND logistics_list_ch = ''"
    else:
        where_sql += " AND REPLACE(REPLACE(logistics_list_ch, ' ', ''), N'　', '') LIKE ?"
        param.append(f"%{logistics_method}%")
    msq = XinTeaSql()
    cmd = f"""SELECT generate_vendor
      ,arrival_area_key
      ,FORMAT(to_order_generate_date, 'yyyy/MM/dd') AS to_order_generate_date
      ,FORMAT(earliest_arrival_date, 'yyyy/MM/dd') AS earliest_arrival_date
      ,to_generate_vendor
      ,logistics_list
      ,logistics_list_ch
      ,FORMAT(earliest_factory_date, 'yyyy/MM/dd') AS earliest_factory_date 
      FROM vendor_arrival_area_b_to_c {where_sql}"""
    return msq.s_qry(cmd, param)


def qry_order_data(order: str) -> list:
    """
    查詢訂單資料
    :param order: 訂單電商平台訂單單號資料
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ?
              ORDER BY arrival_area DESC"""
    return msq.s_qry(cmd, order)


def upd_common_order_diff_shipping_date(upd_data: list) -> bool:
    """
    更新同訂單號碼不同出貨日期
    :param upd_data: 更新資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET common_order_no_different_shipping_date=?
             WHERE order_key=?"""
    cmds_param: list = [
        (cmd, upd_data)
    ]
    return msq.transaction_v2(cmds_param)


def qry_generate_vendor() -> list:
    """查詢生產廠商"""
    msq = XinTeaSql()
    cmd = """SELECT gv.vendor_name, v.consume_warehouse 
             FROM generate_vendor as gv LEFT JOIN vendor as v on gv.vendor_id=v.vendor_id
             WHERE exist='1'"""
    return msq.s_qry(cmd)


def qry_out_bound_warehouse() -> list:
    """查詢出庫倉別"""
    msq = XinTeaSql()
    cmd = """SELECT * FROM outbound_warehouse
             WHERE exist='1'"""
    return msq.s_qry(cmd)


def qry_b_to_c_order_generate(**kwargs) -> list:
    """
    查詢B2C起單
    """
    where_sql: str = "WHERE b2c_bpm_form_id =''" # AND is_check_remark_message=N'已確認'
    param: list = []
    if kwargs.get('e_commerce_platform')!= '':
        where_sql += ' AND e_commerce_platform=?'
        param.append(kwargs.get('e_commerce_platform'))
    if kwargs.get('e_commerce_platform_order_no')!= '':
        where_sql += ' AND e_commerce_platform_order_no=?'
        param.append(kwargs.get('e_commerce_platform_order_no'))
    msq = XinTeaSql()
    cmd = f"""SELECT already_order_order_status, b2c_order_is_can_sign, b2c_order_status, b2c_bpm_form_id,
                estimate_num_and_check, eip_import_label, package_factory_import_label, split_berfore_order_no,
                common_order_no_different_vendor, CONVERT(varchar, common_order_no_different_shipping_date, 23) AS common_order_no_different_shipping_date, 
                CONVERT(varchar, latest_arrival_date, 23) AS latest_arrival_date,
                white_list_process, is_check_remark_message, 
                CONVERT(varchar, to_order_generate_date, 111) AS to_order_generate_date,
                CONVERT(varchar, earliest_arrival_date, 23) AS earliest_arrival_date,
                generate_vendor, shipping_out_warehouse, e_commerce_platform_order_no, e_commerce_platform,
                CONVERT(varchar, e_commerce_platform_order_date, 111) as e_commerce_platform_order_date,
                new_order_order_status, new_order_payment_status, logistics_method,
                order_remark_or_shipping_remark, item, product_name, item_category, bom_bpm_form_id, platform_product_name,
                platform_specific, quantity, recipient, recipient_phone, recipient_address, recipient_email, payment_term,
                order_money, invoice_title, uniform_invoice_no, sender, sender_phone, order_key, arrival_area
                FROM order_manage_summary_b_to_c 
                {where_sql} 
                order by order_key"""
    return msq.s_qry(cmd, param)


def qry_vendor_google_sheet(**kwargs) -> list:
    """
    查詢給廠商google sheet
    """
    where_sql: str = "WHERE google_sheet_url =''" # AND is_check_remark_message=N'已確認'
    param: list = []
    if kwargs.get('e_commerce_platform')!= '':
        where_sql += ' AND e_commerce_platform=?'
        param.append(kwargs.get('e_commerce_platform'))
    if kwargs.get('e_commerce_platform_order_no')!= '':
        where_sql += ' AND e_commerce_platform_order_no=?'
        param.append(kwargs.get('e_commerce_platform_order_no'))
    msq = XinTeaSql()
    cmd = f"""SELECT already_order_order_status, b2c_order_is_can_sign, b2c_order_status, b2c_bpm_form_id,
                estimate_num_and_check, eip_import_label, package_factory_import_label, split_berfore_order_no,
                common_order_no_different_vendor, CONVERT(varchar, common_order_no_different_shipping_date, 23) AS common_order_no_different_shipping_date, 
                CONVERT(varchar, latest_arrival_date, 23) AS latest_arrival_date,
                white_list_process, is_check_remark_message, 
                CONVERT(varchar, to_order_generate_date, 23) AS to_order_generate_date,
                CONVERT(varchar, earliest_arrival_date, 23) AS earliest_arrival_date,
                generate_vendor, shipping_out_warehouse, e_commerce_platform_order_no, e_commerce_platform,
                CONVERT(varchar, e_commerce_platform_order_date, 111) as e_commerce_platform_order_date,
                new_order_order_status, new_order_payment_status, logistics_method,
                order_remark_or_shipping_remark, item, product_name, item_category, bom_bpm_form_id, platform_product_name,
                platform_specific, quantity, recipient, recipient_phone, recipient_address, recipient_email, payment_term,
                order_money, invoice_title, uniform_invoice_no, sender, sender_phone, order_key, arrival_area
                FROM order_manage_summary_b_to_c 
                {where_sql} 
                order by order_key"""
    return msq.s_qry(cmd, param)


def upd_b_to_c_bpm_form_id_on_order_manage_summary(upd: list) -> bool:
    """
    更新B to C bpm表單編號至訂單管理總表
    :param upd: 更新資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET b2c_bpm_form_id=?, b2c_order_status='0' WHERE order_key=?"""
    cmds_param: list = [
        (cmd, upd)
    ]
    return msq.transaction_v2(cmds_param)


def qry_vendor_google_sheet_column(generate_vendor: str) -> list:
    """
    查詢給廠商google sheet欄位
    :param generate_vendor: 生產廠商
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM vendor_google_sheet_column
             WHERE vendor_name=?
             order by column_pri_seq"""
    return msq.s_qry(cmd, generate_vendor)


def qry_calendar_start_date() -> list:
    """查詢行事曆起始日"""
    msq = XinTeaSql()
    cmd = """SELECT * FROM param WHERE param_name=N'行事曆起始日'"""
    return msq.s_qry(cmd)


def qry_e_commerce_platform_column(e_commerce_platform: str) -> list:
    """
    查詢電商平台匯入資料表頭
    :param e_commerce_platform: 電商平台
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM e_commerce_platform_column WHERE e_commerce_platform=?
             ORDER BY column_pri_seq"""
    return msq.s_qry(cmd, e_commerce_platform)


def upd_google_sheet_url(upd_data: list) -> bool:
    """
    更新google sheet id
    :param upd_data: 更新資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET google_sheet_url=?, google_sheet_name=? WHERE order_key=?"""
    cmds_param: list = [
        (cmd, upd_data)
    ]
    return msq.transaction_v2(cmds_param)


def qry_vendor_google_sheet_value(generate_vendor: str) -> list:
    """
    查詢給廠商google sheet value塞入值
    :param generate_vendor 生產廠商
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM vendor_google_sheet_value
             WHERE vendor_name=? 
             ORDER BY value_pri_seq"""
    return msq.s_qry(cmd, generate_vendor)

def check_platform_order_no(e_commerce_platform_order_no_list: list, e_commerce_platform: str) -> list:
    """
    查詢多個電商平台訂單編號是否存在
    :param e_commerce_platform_order_no_list: 電商平台訂單編號列表
    :param e_commerce_platform: 電商平台
    :return: 存在的訂單資料列表
    """
    msq = XinTeaSql()
    
    # 如果輸入是單一訂單編號而非列表，將其轉換為列表
    if not isinstance(e_commerce_platform_order_no_list, list):
        e_commerce_platform_order_no_list = [e_commerce_platform_order_no_list]
    
    # 建立查詢的參數列表
    params = []
    placeholders = []
    
    # 為每個訂單編號建立參數和佔位符
    for order_no in e_commerce_platform_order_no_list:
        placeholders.append("?")
        params.append(order_no)
    
    # 添加電商平台參數
    params.append(e_commerce_platform)
    
    cmd = f"""SELECT DISTINCT e_commerce_platform_order_no FROM order_manage_summary_b_to_c 
          WHERE e_commerce_platform_order_no IN ({','.join(placeholders)}) 
          AND e_commerce_platform=?"""
    # 執行查詢
    return msq.s_qry(cmd, *params)

def upd_complete_order(upd: list) -> list:
    """
    更新完成訂單
    :param upd: 更新資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET already_order_order_status='已完成' WHERE e_commerce_platform_order_no=?"""
    cmds_param: list = [
        (cmd, upd)
    ]
    return msq.transaction_v2(cmds_param)


def compare_order_data(generate_vendor: str, to_order_generate_date: str) -> list:
    """
    查詢比對資料(預計拋單數量跟實際檢查)
    :param generate_vendor: 生產廠商
    :param to_order_generate_date: 拋單日期
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM order_manage_summary_b_to_c
             WHERE generate_vendor=? AND to_order_generate_date=? 
             AND (new_order_order_status='已付款' or new_order_order_status='已確認' 
             or new_order_order_status='待出貨')"""
    return msq.s_qry(cmd, generate_vendor, to_order_generate_date)


def crt_sales_order_b_to_c(sales_order_head: list, sales_order_detail: list) -> int:
    """
    新增銷售訂單-官網B2C(內容欄位)
    :param sales_order_head: 銷售訂單-官網B2C(內容欄位)
    :param sales_order_detail: 銷售訂單-官網B2C(統計欄位)
    """
    msq = XinTeaSql()
    sales_order_head_cmd = """INSERT INTO sales_order_b_to_c(bpm_form_id, bpm_content, issue_employee, issue_date, customer_name, order_type, uu,
                              status, step) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    sales_order_detail_cmd = """
    INSERT INTO sales_order_b_to_c_detail (bpm_form_id, row_number,
        item, category, item_name, bom_bpm_form_id, order_num,
        generate_vendor, outbound_warehosue, cost_item_warehouse,
        completed_storage_warehouse, order_production_date,
        estimate_production_date, earliest_arrival_date, latest_arrival_date,
        new_order_status, new_order_payment_status,
        e_commerce_platform, e_commerce_platform_order_date, e_commerce_platform_order_no,
        logistics_method, order_remark_and_shipping_remark, platform_product_name,
        platform_product_specific, recipient, recipient_phone,
        recipient_address, recipient_email, payment_term, order_money,
        invoice_title, uniform_invoice_no, uu_one, year, month, sales_order_key
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cmds_params = [
        (sales_order_head_cmd, sales_order_head),
        (sales_order_detail_cmd, sales_order_detail)
    ]
    return msq.transaction_v2(cmds_params)


def qry_vendor_condition() -> list:
    """
    查詢廠商設定條件
    """
    msq = XinTeaSql()
    cmd = """SELECT row_number, vendor, 
                CONVERT(VARCHAR(10), start_date, 120) AS start_date,
                order_money, logistics_list, logistics_list_ch, pri_seq
            FROM vendor_condition_b_to_c
            ORDER BY 
                CASE WHEN pri_seq = 0 THEN 1 ELSE 0 END,  
                pri_seq ASC"""
    return msq.s_qry(cmd)


def qry_logistics_method() -> list:
    """
    查詢物流方式
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM logistics_method"""
    return msq.s_qry(cmd)

def qry_vendor_item(vendor: str, item_id: str) -> list:
    """
    查詢廠商料件
    :param vendor: 廠商編號
    :param item_id: 料件編號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_reference WHERE item_id = ? AND vendor_name = ? AND relationship='1'"""
    return msq.s_qry(cmd, item_id, vendor)


def upd_order_manage_summary_b_to_c_and_delete_error_arrival_area(upd_data: list, delete_param: list) -> list:
    """
    更新後續計算訂單管理轉換資料(B to C) and 刪除訂單管理總表(B to C)到貨區間錯誤資料
    :param upd_data: 更新資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET generate_vendor = ?, shipping_out_warehouse =?,
             to_order_generate_date = ?, earliest_arrival_date = ?, latest_arrival_date = ?, common_order_no_different_shipping_date = ?,
             arrival_area = ?, delivery_generate_vendor = ?
             WHERE split_berfore_order_no = ?"""
    delete_param_cmd: str = """DELETE FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ?"""
    delete_error_cmd: str = """DELETE FROM order_manage_summary_b_to_c WHERE arrival_area_split!='' and generate_vendor=''"""
    cmds_param: list = []
    if upd_data:
        cmds_param.append((cmd, upd_data))
    if delete_param:
        cmds_param.append((delete_param_cmd, delete_param))
    #if delete_error_cmd:
    #    cmds_param.append((delete_error_cmd, []))
    return msq.transaction_v2(cmds_param)


def delete_order_manage_summary_b_to_c(delete_param: list) -> bool:
    """
    刪除訂單管理總表(B to C)
    :param delete_param: 刪除資料
    """
    msq = XinTeaSql()
    cmd = """DELETE FROM order_manage_summary_b_to_c WHERE order_key = ?"""
    cmds_param: list = [
        (cmd, delete_param)
    ]
    return msq.transaction_v2(cmds_param)


def modify_order_manage_summary_b_to_c(modify_param: list) -> bool:
    """
    修改訂單管理總表(B to C)
    :param modify_param: 修改資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET white_list_process=?, is_check_remark_message=?,
             to_order_generate_date=?, earliest_arrival_date=?, generate_vendor=?, shipping_out_warehouse=?,
             status=?, xin_tea_remark=?, import_date=?, quantity=?, latest_arrival_date=?, delivery_vendor=?
             WHERE order_key=?"""
    cmds_param: list = []
    if modify_param:
        cmds_param.append((cmd, modify_param))
    return msq.transaction_v2(cmds_param)


def to_vendor_order_manage_summary_b_to_c(to_vendor_param: list) -> bool:
    """
    訂單管理總表(B to C)-拋轉廠商
    :param delete_param: 刪除資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET to_vendor_time=?, to_vendor='1' WHERE order_key = ?"""
    cmds_param: list = [
        (cmd, to_vendor_param)
    ]
    return msq.transaction_v2(cmds_param)


def upd_check_message(check_param: list) -> bool:
    """
    更新檢查訊息
    :param check_param 檢查資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET check_message=? WHERE order_key = ?"""
    cmds_param: list =[]
    if check_param:
        cmds_param.append((cmd, check_param))
    return msq.transaction_v2(cmds_param)


def qry_vendor_order_b_to_c(**kwargs) -> list:
    """
    查詢廠商訂單(B to C)
    """
    where_sql: str = 'WHERE 1=1'
    param: list = []
    if kwargs.get('e_commerce_platform') != '':
        where_sql += ' AND e_commerce_platform=?'
        param.append(kwargs.get('e_commerce_platform'))
    if kwargs.get('e_commerce_platform_order_no') != '':
        where_sql += ' AND e_commerce_platform_order_no=?'
        param.append(kwargs.get('e_commerce_platform_order_no'))
    msq = XinTeaSql()
    cmd = f"""SELECT om.already_order_order_status, so.step AS b2c_order_is_can_sign, so.status AS b2c_order_status, om.b2c_bpm_form_id,
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
                om.status, om.vendor_order_status, om.check_message
                FROM vendor_order_b_to_c as om
                LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id 
                
                {where_sql}
                order by order_key"""
    return msq.s_qry(cmd, param)

def crt_vendor_order_b_to_c_upd_order_manage_status(vendor_order: list, upd_to_vendor_param: list, upd_status: list,
                                                    upd_delete_vendor_param: list, crt_use_item_param: list, 
                                                    upd_use_item_cancel_param: list, upd_use_item_delete_param: list,
                                                    error_data: list, success_data: list, upd_order_manage_bom: list) -> bool:
    """
    拋轉至廠商訂單(B to C)&更改訂單管理總表狀態
    :param vendor_order: 廠商訂單資料
    :param upd_to_vendor_param: 更新廠商訂單資料
    :param upd_status: 更新狀態資料
    :param upd_delete_vendor_param: 更新刪除廠商訂單資料
    :param crt_use_item_param: 新增用料明細資料
    :param upd_use_item_cancel_param: 更新用料明細資料
    :param upd_use_item_delete_param: 更新刪除用料明細資料
    :param error_data: 錯誤資料
    :param success_data: 成功資料
    :param upd_order_manage_bom: 更新訂單管理BOM資料
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO vendor_order_b_to_c(
        status, vendor_order_status, check_message, white_list_process,
        is_check_remark_message, to_order_generate_date, earliest_arrival_date, generate_vendor,
        shipping_out_warehouse, xin_tea_remark, already_order_order_status, b2c_order_is_can_sign,
        b2c_order_status, b2c_bpm_form_id, estimate_num_and_check, eip_import_label,
        package_factory_import_label, split_berfore_order_no, common_order_no_different_vendor,
        common_order_no_different_shipping_date, latest_arrival_date, e_commerce_platform_order_no,
        e_commerce_platform, e_commerce_platform_order_date, new_order_order_status, new_order_payment_status,
        logistics_method, order_remark_or_shipping_remark, item, product_name,
        item_category, bom_bpm_form_id, platform_product_name, platform_specific,
        quantity, recipient, recipient_phone, recipient_address, 
        recipient_email, payment_term, order_money, invoice_title,
        uniform_invoice_no, sender, sender_phone, order_key,
        arrival_area, importer, import_date, google_sheet_url,
        google_sheet_name, vendor_check
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    
    upd_status_cmd: str = """UPDATE order_manage_summary_b_to_c SET status=? WHERE order_key=?"""
    
    upd_vendor_cmd: str = """
        WITH LatestRecord AS (
            SELECT order_key, import_date, 
                ROW_NUMBER() OVER (PARTITION BY order_key ORDER BY import_date DESC) as row_num
            FROM vendor_order_b_to_c
            WHERE order_key = ?
        )
        UPDATE v
        SET v.status = ?, v.vendor_order_status = ?, v.check_message = ?, v.white_list_process = ?,
            v.is_check_remark_message = ?, v.to_order_generate_date = ?, v.earliest_arrival_date = ?, v.generate_vendor = ?,
            v.shipping_out_warehouse = ?, v.xin_tea_remark = ?, v.already_order_order_status = ?, v.b2c_order_is_can_sign = ?,
            v.b2c_order_status = ?, v.b2c_bpm_form_id = ?, v.estimate_num_and_check = ?, v.eip_import_label = ?,
            v.package_factory_import_label = ?, v.split_berfore_order_no = ?, v.common_order_no_different_vendor = ?,
            v.common_order_no_different_shipping_date = ?, v.latest_arrival_date = ?, v.e_commerce_platform_order_no = ?,
            v.e_commerce_platform = ?, v.e_commerce_platform_order_date = ?, v.new_order_order_status = ?, v.new_order_payment_status = ?,
            v.logistics_method = ?, v.order_remark_or_shipping_remark = ?, v.item = ?, v.product_name = ?,
            v.item_category = ?, v.bom_bpm_form_id = ?, v.platform_product_name = ?, v.platform_specific = ?,
            v.quantity = ?, v.recipient = ?, v.recipient_phone = ?, v.recipient_address = ?, 
            v.recipient_email = ?, v.payment_term = ?, v.order_money = ?, v.invoice_title = ?,
            v.uniform_invoice_no = ?, v.sender = ?, v.sender_phone = ?,
            v.arrival_area = ?, v.importer = ?, v.import_date = ?, v.google_sheet_url = ?,
            v.google_sheet_name = ?, v.vendor_check = ?
        FROM vendor_order_b_to_c v
        INNER JOIN LatestRecord lr ON v.order_key = lr.order_key AND v.import_date = lr.import_date
        WHERE lr.row_num = 1 and v.order_key = ?
    """
        
    upd_delete_vendor_param_cmd: str = """
        WITH LatestRecord AS (
            SELECT order_key, import_date, 
                ROW_NUMBER() OVER (PARTITION BY order_key ORDER BY import_date DESC) as row_num
            FROM vendor_order_b_to_c
            WHERE order_key = ? AND vendor_check = '1'
        )
        UPDATE vendor_order_b_to_c
        SET vendor_order_status = ?, vendor_check = ?
        FROM vendor_order_b_to_c v
        INNER JOIN LatestRecord lr ON v.order_key = lr.order_key AND v.import_date = lr.import_date
        WHERE lr.row_num = 1
    """
    # 用料明細
    upd_use_item_delete_cmd: str = """DELETE use_item_detail WHERE order_key=?"""
    crt_use_item_cmd: str = """INSERT INTO use_item_detail(e_commerce_platform_order_no, split_before_order_no, order_key, to_order_generate_date, 
    earliest_arrival_date, latest_arrival_date,
    shipping_date, item, item_name, estimate_generate, customize_or_normal, customize_specific, order_remark,
    m_item, m_item_name, s_item, s_item_name, s_item_use, estimate_use, customize_item, uu_one, customer,
    item_category, generate_vendor, generate_status, oem_fee, other_expense, advance_expenses, total_expense,
    shipping_out_warehouse, bom_bpm_form_id, status, unit)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    upd_use_item_cancel_cmd: str = """UPDATE use_item_detail SET generate_status=?, modify_time=? WHERE order_key=?"""
    
    # 拋轉廠商失敗將錯誤訊息寫入檢查訊息
    error_data_cmd: str = """UPDATE order_manage_summary_b_to_c SET check_message=? WHERE order_key=?"""
    # 拋轉廠商成功將錯誤訊息清除
    success_data_cmd: str = """UPDATE order_manage_summary_b_to_c SET check_message=? WHERE order_key=?"""
    # 更新BOM
    upd_order_manage_bom_cmd: str = """UPDATE order_manage_summary_b_to_c SET bom_bpm_form_id=? WHERE order_key=?"""


    cmds_param: list = []
    if upd_status:
        cmds_param.append((upd_status_cmd, upd_status))
    if vendor_order:
        cmds_param.append((cmd, vendor_order))
    if upd_to_vendor_param:
        cmds_param.append((upd_vendor_cmd, upd_to_vendor_param))
    if upd_delete_vendor_param:
        cmds_param.append((upd_delete_vendor_param_cmd, upd_delete_vendor_param))
    # 用料明細
    if upd_use_item_delete_param:
        cmds_param.append((upd_use_item_delete_cmd, upd_use_item_delete_param))
    if crt_use_item_param:
        cmds_param.append((crt_use_item_cmd, crt_use_item_param))
    if upd_use_item_cancel_param:
        cmds_param.append((upd_use_item_cancel_cmd, upd_use_item_cancel_param))
    # 錯誤訊息
    if error_data:
        cmds_param.append((error_data_cmd, error_data))
    if success_data:
        cmds_param.append((success_data_cmd, success_data))
    # 更新訂單BOM
    if upd_order_manage_bom:
        cmds_param.append((upd_order_manage_bom_cmd, upd_order_manage_bom))
    return msq.transaction_v2(cmds_param)


def qry_order_no_can_import(order_no: str) -> list:
    """
    查詢訂單號碼是否可重新匯入(訂單已取消已拋單)
    :param order_no: 訂單號碼
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM order_manage_summary_b_to_c WHERE e_commerce_platform_order_no=?
             AND status in ('0', '3.1', '4.1', '7', '7.1', '6', '6.1', '6.2', '2.0')"""
    return msq.s_qry(cmd, order_no)


def qry_order_no(order_no: str) -> list:
    """
    查詢訂單號碼是否存在
    :param order_no: 訂單號碼
    """
    msq = XinTeaSql()
    cmd = """SELECT om.status, 
             CASE WHEN latest_vob.vendor_check = 1 THEN '1' ELSE '0' END AS vendor_check,
             om.e_commerce_platform_order_no FROM order_manage_summary_b_to_c as om
             OUTER APPLY (
                        SELECT TOP 1 *
                        FROM vendor_order_b_to_c
                        WHERE order_key = om.order_key
                        ORDER BY import_date DESC
             ) AS latest_vob 
    WHERE om.e_commerce_platform_order_no=?"""
    return msq.s_qry(cmd, order_no)


def qry_status_select(select_id: str) -> list:
    """
    查詢狀態下拉選單
    :param select_id: 下拉選單ID
    """
    msq = XinTeaSql()
    cmd = """select su.status_id, su.can_use, s.status_name, s.select_name
             FROM status_use as su
             INNER JOIN status as s on su.can_use = s.status_id
             where su.status_id=?"""
    return msq.s_qry(cmd, select_id)


def qry_all_status_select() -> list:
    """
    查詢所有狀態下拉選單
    """
    msq = XinTeaSql()
    cmd = """select su.status_id, su.can_use, s.status_name, s.select_name
             FROM status_use as su
             INNER JOIN status as s on su.can_use = s.status_id"""
    return msq.s_qry(cmd)


def qry_status_can_to_vendor(status: str) -> list:
    """
    查詢狀態可否拋轉廠商
    :param status: 狀態
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM status WHERE status_id=? AND can_to_vendor='1'"""
    return msq.s_qry(cmd, status)

def qry_status(status: str) -> list:
    """
    查詢狀態資料
    :param status: 狀態
    """
    msq = XinTeaSql()
    cmd = """SELECT status_id, status_name, select_name, to_vendor_status
            , can_to_vendor, vendor_look_status, complete_close_status
            , complete_cancel_status
            , CASE WHEN complete_close_error = 1 THEN 1 ELSE 0 END AS complete_close_error
            , CASE WHEN complete_cancel_error = 1 THEN 1 ELSE 0 END AS complete_cancel_error
             FROM status WHERE status_id=?"""
    return msq.s_qry(cmd, status)


def qry_vendor_order(order: str) -> list:
    """
    查詢廠商訂單資料(僅返回最新一筆)
    :param order: 訂單電商平台訂單單號資料
    """
    msq = XinTeaSql()
    cmd = f"""SELECT TOP 1 order_key, CASE WHEN vendor_check = 1 THEN '1' ELSE '0' END AS vendor_check 
              FROM vendor_order_b_to_c 
              WHERE order_key = ? 
              ORDER BY import_date DESC"""
    return msq.s_qry(cmd, order)


def qry_order_data_by_cancel(order: str) -> list:
    """
    查詢訂單資料(取消處理)
    :param order: 訂單電商平台訂單單號資料
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ? and status in ('2', '3', '5')
              ORDER BY arrival_area DESC"""
    return msq.s_qry(cmd, order)


def qry_order_data_by_to_vendor(order: str) -> list:
    """
    查詢訂單資料(拋廠商)
    :param order: 訂單電商平台訂單單號資料
    """
    msq = XinTeaSql()
    cmd = f"""SELECT * FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ? and status not in ('2.0', '3.1', '4.1')
              ORDER BY arrival_area DESC"""
    return msq.s_qry(cmd, order)


def upd_complete_order_data(upd_param: list, upd_vendor_close_param: list, upd_vendor_cancel_param: list, upd_use_detail: list) -> bool:
    """
    更新完成訂單狀態
    :param upd_param: 更新資料
    :param upd_vendor_close_param: 更新廠商結案資料
    :param upd_vendor_cancel_param: 更新廠商取消資料
    :param upd_use_detail: 更新用料明細資料
    """
    msq = XinTeaSql()
    cmd = """UPDATE order_manage_summary_b_to_c SET status=?, complete_order_error=?
             WHERE e_commerce_platform_order_no=?"""
    upd_vendor_close_cmd: str = """UPDATE vendor_order_b_to_c SET vendor_order_status=? where e_commerce_platform_order_no=?"""
    upd_vendor_cancel_cmd: str = """UPDATE vendor_order_b_to_c SET vendor_order_status=?, vendor_check=? where e_commerce_platform_order_no=?"""
    upd_use_detail_cmd: str = """UPDATE use_item_detail SET generate_status=?, complete_time=? WHERE e_commerce_platform_order_no=?"""
    cmds_param: list = []
    if upd_param:
        cmds_param.append((cmd, upd_param))
    if upd_vendor_close_param:
        cmds_param.append((upd_vendor_close_cmd, upd_vendor_close_param))
    if upd_vendor_cancel_param:
        cmds_param.append((upd_vendor_cancel_cmd, upd_vendor_cancel_param))
    if upd_use_detail:
        cmds_param.append((upd_use_detail_cmd, upd_use_detail))
    return msq.transaction_v2(cmds_param)


def crt_work_task(task_id: str) -> bool:
    """
    新增工作任務
    :param task_id: 工作任務ID
    """
    msq = XinTeaSql()
    cmd = """INSERT INTO work_task(task_id) VALUES(?)"""
    cmds_param: list = [
        (cmd, [(task_id,)])
    ]
    return msq.transaction_v2(cmds_param)


def upd_work_task_success(task_id: str, message: str) -> bool:
    """
    更新工作任務(成功)
    :param task_id: 工作任務ID
    """
    msq = XinTeaSql()
    cmd = """UPDATE work_task SET success='1', message=? WHERE task_id=?"""
    cmds_param: list = [
        (cmd, [(message, task_id)])
    ]
    return msq.transaction_v2(cmds_param)


def upd_work_task_error(task_id: str) -> bool:
    """
    更新工作任務(失敗)
    :param task_id: 工作任務ID
    """
    msq = XinTeaSql()
    cmd = """UPDATE work_task SET success='-1' WHERE task_id=?"""
    cmds_param: list = [
        (cmd, [(task_id, )])
    ]
    return msq.transaction_v2(cmds_param)

def qry_task_is_success(task_id: str) -> list:
    """
    查詢工作任務是否成功
    :param task_id: 工作任務ID
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM work_task WHERE task_id=? and success='1'"""
    return msq.s_qry(cmd, task_id)


def qry_task_is_error(task_id: str) -> list:
    """
    查詢工作任務是否失敗
    :param task_id: 工作任務ID
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM work_task WHERE task_id=? and success='-1'"""
    return msq.s_qry(cmd, task_id)

def qry_order_manage_summary_repeat(order_key: list) -> list:
    """
    重新查詢訂單管理總表
    :param order_key: 訂單key列表
    """
    msq = XinTeaSql()
    
    if not order_key:
        return []
    
    placeholders = ','.join(['?' for _ in range(len(order_key))])
    
    cmd = f"""SELECT om.already_order_order_status, so.step AS b2c_order_is_can_sign, so.status AS b2c_order_status, om.b2c_bpm_form_id,
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
                CASE WHEN om.complete_order_error = 1 THEN '1' ELSE '0' END AS complete_order_error,
                CASE WHEN latest_vob.vendor_check = 1 THEN '1' ELSE '0' END AS vendor_check,
                om.status, om.check_message, latest_vob.vendor_order_status
            FROM order_manage_summary_b_to_c as om
            LEFT JOIN sales_order_b_to_c as so ON om.b2c_bpm_form_id = so.bpm_form_id 
            OUTER APPLY (
                SELECT TOP 1 *
                FROM vendor_order_b_to_c
                WHERE order_key = om.order_key
                ORDER BY import_date DESC
            ) AS latest_vob
            WHERE om.order_key IN ({placeholders})
            ORDER BY e_commerce_platform, e_commerce_platform_order_no, item, order_key"""
    
    return msq.s_qry(cmd, *order_key)


def qry_bom_by_item(item: str, bom: str) -> list:
    """
    查詢BOM表(依件號-一階料)
    :param item: 件號
    :param bom: BOM表單號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_bom WHERE item = ? AND origin_form_id = ? AND m_item=? AND s_item <> ?"""
    return msq.s_qry(cmd, item, bom, item, item)


def qry_order_no_already_close(order_no: str) -> list:
    """
    查詢訂單是否已經出貨-結案or取消
    :param order_no: 電商平台訂單單號
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM order_manage_summary_b_to_c
             WHERE e_commerce_platform_order_no = ? and status IN ('6', '6.1', '6.2', '7', '7.1', '7.2')"""
    return msq.s_qry(cmd, order_no)


def qry_status_from_qry() -> list:
    """
    查詢狀態(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """select DISTINCT status_id, select_name  FROM order_manage_summary_b_to_c as o
             INNER JOIN status as sta on sta.status_id = o.status"""
    return msq.s_qry(cmd)


def qry_vendor_status_from_qry() -> list:
    """
    查詢廠商狀態(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT vendor_order_status FROM vendor_order_b_to_c"""
    return msq.s_qry(cmd)


def qry_vendor_check_by_qry() -> list:
    """
    查詢廠商確認(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT latest_vob.vendor_check, CASE WHEN latest_vob.vendor_check = 1 THEN '已確認' ELSE '待確認' END AS vendor_check_name
            FROM order_manage_summary_b_to_c as om
            OUTER APPLY (
                SELECT TOP 1 *
                FROM vendor_order_b_to_c
                WHERE order_key = om.order_key
                ORDER BY import_date DESC
            ) AS latest_vob
            WHERE latest_vob.order_key IS NOT NULL"""
    return msq.s_qry(cmd)


def qry_is_check_remark_message_by_qry() -> list:
    """
    查詢是否檢查備註訊息(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT is_check_remark_message FROM order_manage_summary_b_to_c"""
    return msq.s_qry(cmd)


def qry_generate_vendor_by_qry() -> list:
    """
    查詢生產廠商(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT generate_vendor FROM order_manage_summary_b_to_c"""
    return msq.s_qry(cmd)


def qry_delivery_vendor_by_qry() -> list:
    """
    查詢配送廠商(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT delivery_vendor FROM order_manage_summary_b_to_c"""
    return msq.s_qry(cmd)


def qry_e_commerce_platform_by_qry() -> list:
    """
    查詢電商平台(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT e_commerce_platform FROM order_manage_summary_b_to_c"""
    return msq.s_qry(cmd)


def qry_e_commerce_platform_order_no_by_qry() -> list:
    """
    查詢電商平台訂單號(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT e_commerce_platform_order_no FROM order_manage_summary_b_to_c"""
    return msq.s_qry(cmd)


def qry_spread_calculate(order_key: str) -> list:
    """
    查詢用料明細展算
    :param order_key: 心茶訂單key
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM spread_calculate WHERE order_key = ?"""
    return msq.s_qry(cmd, order_key)


def crt_spread_calculate(crt_use_item_param: list, upd_spread_calculate_param: list) -> bool:
    """
    拋轉至廠商訂單(B to C)&更改訂單管理總表狀態
    :param crt_use_item_param: 新增用料展算資料
    :param upd_spread_calculate_param: 更新展算時間資料
    """
    msq = XinTeaSql()
    
    # 刪除現有展算
    delete_spread_calculate_cmd: str = """DELETE FROM spread_calculate"""

    # 用料明細
    crt_use_item_cmd: str = """INSERT INTO spread_calculate(e_commerce_platform_order_no, split_before_order_no, order_key, earliest_arrival_date, latest_arrival_date,
    to_order_generate_date,
    shipping_date, item, item_name, estimate_generate, customize_or_normal, customize_specific, order_remark,
    m_item, m_item_name, s_item, s_item_name, s_item_use, estimate_use, customize_item, uu_one, customer,
    item_category, generate_vendor, generate_status, oem_fee, other_expense, advance_expenses, total_expense,
    shipping_out_warehouse, bom_bpm_form_id, status, unit)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    upd_spread_calculate_time_cmd: str = """UPDATE order_manage_summary_b_to_c SET spread_calculate_time=? WHERE order_key=?"""
    
        
    cmds_param: list = [
        (delete_spread_calculate_cmd, [()]),
    ]
    if crt_use_item_param:
        cmds_param.append((crt_use_item_cmd, crt_use_item_param))
    if upd_spread_calculate_param:
        cmds_param.append((upd_spread_calculate_time_cmd, upd_spread_calculate_param))
    return msq.transaction_v2(cmds_param)


def qry_order_by_status(status: str) -> list:
    """
    查詢訂單資料by訂單狀態
    :param status: 訂單狀態
    """
    msq = XinTeaSql()
    cmd: str = """SELECT COUNT(*) AS order_count
                FROM order_manage_summary_b_to_c
                WHERE status = ?"""
    return msq.s_qry(cmd, status)


def qry_status_by_dashboard() -> list:
    """
    查詢狀態(儀表板用) 
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM status WHERE dashboard='1'
                  order by status_id"""
    return msq.s_qry(cmd)


def qry_vendor_order_check_by_dashboard(status: str) -> list:
    """
    查詢廠商訂單狀態(儀表板用) 
    """
    msq = XinTeaSql()
    cmd: str = f"""SELECT COUNT(*) AS order_count
                FROM order_manage_summary_b_to_c as om
                INNER JOIN (
                    SELECT order_key, vendor_check
                    FROM (
                        SELECT order_key, vendor_check,
                            ROW_NUMBER() OVER (PARTITION BY order_key ORDER BY import_date DESC) AS rn
                        FROM vendor_order_b_to_c
                    ) t
                    WHERE t.rn = 1
                ) AS latest_vob ON om.order_key = latest_vob.order_key
                WHERE ISNULL(latest_vob.vendor_check, '0') = ?"""
    return msq.s_qry(cmd, status)


def crt_upload_record(error_message: list) -> bool:
    """
    新增上傳紀錄
    :param error_message: 錯誤訊息
    """
    msq = XinTeaSql()
    cmd: str = """INSERT INTO order_import_record(platform, action, error_message) VALUES(?,?,?)"""
    cmds_param: list = [
        (cmd, error_message)
    ]
    return msq.transaction_v2(cmds_param)


def qry_bom_spread_rule_can_spread() -> list:
    """
    查詢BOM展算規則(可展算)
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_category WHERE is_spread_calculate='1' and is_bom='1'"""
    return msq.s_qry(cmd)


def qry_bom_spread_rule_no_spread() -> list:
    """
    查詢BOM展算規則(不可展算)
    """
    msq = XinTeaSql()
    cmd = """SELECT * FROM item_category WHERE is_spread_calculate='0'"""
    return msq.s_qry(cmd)


def qry_item_category_can_import(item_category: str) -> list:
    """
    查詢料件類別是否可匯入
    :param item_category: 料件類別
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM item_category WHERE item_category = ?"""
    return msq.s_qry(cmd, item_category)


def qry_is_remark_check_condition() -> list:
    """
    查詢是否備註欄確認判定
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM is_remark_check_condition"""
    return msq.s_qry(cmd)


def qry_order_by_split_berfore_order_no(split_berfore_order_no: str) -> list:
    """
    查詢訂單資料By拆單前單號
    :param split_berfore_order_no: 拆單前單號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ? and white_list_process <> '例外白名單'"""
    return msq.s_qry(cmd, split_berfore_order_no)


def qry_no_close_order() -> list:
    """
    查詢未結訂單
    """
    msq = XinTeaSql()
    cmd: str = """select DISTINCT oms.order_key as real_order_key, '銷售訂單-官網B2C-'+oms.e_commerce_platform_order_no as order_key, oms.e_commerce_platform_order_no,　　　
                CONVERT(VARCHAR(10), oms.e_commerce_platform_order_date, 120) AS e_commerce_platform_order_date,
                REPLACE(oms.latest_arrival_date, '/', '-') AS latest_arrival_date_str,
                oms.item, oms.product_name, oms.platform_specific, oms.quantity,
                ROUND(CAST(order_money AS FLOAT) / CAST(quantity AS FLOAT), 2) AS special_price,
                oms.order_money, uidd.generate_status, '實際' as order_type, 
                oms.order_remark_or_shipping_remark,
                YEAR(oms.e_commerce_platform_order_date) AS order_year,
                MONTH(oms.e_commerce_platform_order_date) AS order_month,
                '' AS order_week, oms.item+'實際' as count_key,  '標準禮盒' as customize_normal,
                '官網B2C訂單' AS customer_name, oms.importer, oms.shipping_out_warehouse, 
                REPLACE(oms.earliest_arrival_date, '/', '-') AS earliest_arrival_date,
                oms.latest_arrival_date
                FROM order_manage_summary_b_to_c as oms
                INNER JOIN use_item_detail as uidd on oms.order_key=uidd.order_key
                """
    return msq.s_qry(cmd)


def qry_order_manage_summary_b_to_c_error_arrival_area_split(order_no: str) -> list:
    """
    查詢訂單管理總表(B to C)到貨區間錯誤
    :param order_no: 訂單號碼
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_c WHERE arrival_area='到貨區間錯誤' and e_commerce_platform_order_no = ?"""
    return msq.s_qry(cmd, order_no)




def qry_order_no_to_vendor(order_no: str) -> list:
    """
    查詢訂單號碼是否已拋轉廠商
    :param order_no: 訂單號碼
    """
    msq = XinTeaSql()
    cmd = """SELECT om.status, 
                CASE WHEN latest_vob.vendor_check = 1 THEN '1' ELSE '0' END AS vendor_check,
                om.e_commerce_platform_order_no 
            FROM order_manage_summary_b_to_c as om
            INNER JOIN (
                SELECT DISTINCT order_key, 
                    FIRST_VALUE(vendor_check) OVER (PARTITION BY order_key ORDER BY import_date DESC) as vendor_check
                FROM vendor_order_b_to_c
            ) AS latest_vob ON om.order_key = latest_vob.order_key
            WHERE om.e_commerce_platform_order_no = ?"""
    return msq.s_qry(cmd, order_no)


def qry_order_b_to_c_count_by_split_before_order_no(split_before_order_no: str) -> list:
    """
    查詢訂單(B to C)數量By拆單前單號
    :param split_before_order_no: 拆單前單號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ?"""
    return msq.s_qry(cmd, split_before_order_no)



def qry_order_manage_summary_b_to_c_by_split_before_order(split_before_order: str) -> list:
    """
    查詢訂單管理總表(B to C)By拆單前單號
    :param split_before_order: 拆單前單號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_c WHERE split_berfore_order_no = ?"""
    return msq.s_qry(cmd, split_before_order)


def qry_logistics_method_exist(logistics_method: str) -> list:
    """
    查詢物流方式是否存在
    :param logistics_method: 物流方式
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM logistics WHERE REPLACE(REPLACE(logistics_method, ' ', ''), N'　', '') = ?"""
    return msq.s_qry(cmd, logistics_method)


def qry_item_category_must_bom(item_category: str) -> list:
    """
    查詢料件類別是否必須有BOM
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM item_category WHERE item_category = ? and is_bom = '1'"""
    return msq.s_qry(cmd, item_category)


def qry_item_reference(item: str) -> list:
    """
    查詢料件參照表
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM item_reference WHERE item_id = ?"""
    return msq.s_qry(cmd, item)

def batch_repeat_spread(crt_use_item_param: list, upd_use_item_delete_param: list, upd_order_manage_check_message_clear: list) -> bool:
    """
    批次重新展算
    :param crt_use_item_param: 新增用料明細
    :param upd_use_item_delete_param: 刪除用料明細
    :param upd_order_manage_check_message_clear: 更新訂單管理檢查訊息
    """
    msq = XinTeaSql()
    # 用料明細
    upd_use_item_delete_cmd: str = """DELETE use_item_detail WHERE order_key=?"""
    crt_use_item_cmd: str = """INSERT INTO use_item_detail(e_commerce_platform_order_no, split_before_order_no, order_key, to_order_generate_date, 
    earliest_arrival_date, latest_arrival_date,
    shipping_date, item, item_name, estimate_generate, customize_or_normal, customize_specific, order_remark,
    m_item, m_item_name, s_item, s_item_name, s_item_use, estimate_use, customize_item, uu_one, customer,
    item_category, generate_vendor, generate_status, oem_fee, other_expense, advance_expenses, total_expense,
    shipping_out_warehouse, bom_bpm_form_id, status, unit)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    upd_order_manage_check_message_clear_cmd: str = """UPDATE order_manage_summary_b_to_c SET check_message = ? WHERE order_key = ?"""
    cmds_param: list = []
    if upd_use_item_delete_param:
        cmds_param.append((upd_use_item_delete_cmd, upd_use_item_delete_param))
    if crt_use_item_param:
        cmds_param.append((crt_use_item_cmd, crt_use_item_param))
    if upd_order_manage_check_message_clear:
        cmds_param.append((upd_order_manage_check_message_clear_cmd, upd_order_manage_check_message_clear))
    return msq.transaction_v2(cmds_param)


def qry_item_by_qry() -> list:
    """
    查詢料號(下拉選單)(查詢用)
    """
    msq = XinTeaSql()
    cmd = """SELECT DISTINCT item FROM order_manage_summary_b_to_c"""
    return msq.s_qry(cmd)


def qry_inventory_open_date() -> list:
    """
    查詢庫存開帳日
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM param WHERE param_name=N'庫存開帳日期'"""
    return msq.s_qry(cmd)


if __name__ == '__main__':
    print(qry_all_status_select())