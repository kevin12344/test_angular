from programs.core.db_process.all_db_connect.main import XinTeaSql



def qry_order_manage_summary_b_to_b(**kwargs):
    """查詢訂單管理總表B2B"""
    where_sql: str = "WHERE 1=1"
    param: list = []
    """
    if kwargs.get('generate_vendor') != '':
        generate_vendor_list = kwargs.get('generate_vendor').split(',')
        placeholders = ','.join(['?' for _ in range(len(generate_vendor_list))])
        where_sql += f' AND ob.generate_vendor IN ({placeholders})'
        param.extend(generate_vendor_list)
    """
    if kwargs.get('item') != '':
        item_list = kwargs.get('item').split(',')
        placeholders = ','.join(['?' for _ in range(len(item_list))])
        where_sql += f' AND ob.item IN ({placeholders})'
        param.extend(item_list)
    if kwargs.get('customer_name') != '':
        customer_name_list = kwargs.get('customer_name').split(',')
        placeholders = ','.join(['?' for _ in range(len(customer_name_list))])
        where_sql += f' AND ob.customer_name IN ({placeholders})'
        param.extend(customer_name_list)
    if kwargs.get('bpm_form_id') != '':
        bpm_form_id_list = kwargs.get('bpm_form_id').split(',')
        placeholders = ','.join(['?' for _ in range(len(bpm_form_id_list))])
        where_sql += f' AND ob.bpm_form_id IN ({placeholders})'
        param.extend(bpm_form_id_list)
    if kwargs.get('bpm_generate_id') != '':
        bpm_generate_id_list = kwargs.get('bpm_generate_id').split(',')
        placeholders = ','.join(['?' for _ in range(len(bpm_generate_id_list))])
        where_sql += f' AND ob.bpm_generate_id IN ({placeholders})'
        param.extend(bpm_generate_id_list)
    if kwargs.get('xin_tea_connector') != '':
        xin_tea_connector_list = kwargs.get('xin_tea_connector').split(',')
        placeholders = ','.join(['?' for _ in range(len(xin_tea_connector_list))])
        where_sql += f' AND ob.xin_tea_connector IN ({placeholders})'
        param.extend(xin_tea_connector_list)
    if kwargs.get('earliest_arrival_date_start') != '' or kwargs.get('earliest_arrival_date_end'):
        where_sql += ' AND ob.earliest_arrival_date BETWEEN ? AND ?'
        param.append(kwargs.get('earliest_arrival_date_start'))
        param.append(kwargs.get('earliest_arrival_date_end'))
    if kwargs.get('latest_arrival_date_start') != '' or kwargs.get('latest_arrival_date_end'):
        where_sql += ' AND ob.latest_arrival_date BETWEEN ? AND ?'
        param.append(kwargs.get('latest_arrival_date_start'))
        param.append(kwargs.get('latest_arrival_date_end'))
    if kwargs.get('customer_estimate_decide_date_start') != '' or kwargs.get('customer_estimate_decide_date_end'):
        where_sql += ' AND ob.customer_estimate_decide_date BETWEEN ? AND ?'
        param.append(kwargs.get('customer_estimate_decide_date_start'))
        param.append(kwargs.get('customer_estimate_decide_date_end'))
    if kwargs.get('have_update') == '1':
        where_sql += ' AND (ob.bpm_form_must_update = ? or ob.bpm_generate_must_update = ? or ob.upd_gs_remind_bpm_form = ? or ob.upd_gs_remind_bpm_generate = ?)'
        param.append(kwargs.get('have_update'))
        param.append(kwargs.get('have_update'))
        param.append(kwargs.get('have_update'))
        param.append(kwargs.get('have_update'))
    if kwargs.get('specific_remind') == '1':
        where_sql += ' AND ob.specific_remind = ?'
        param.append(kwargs.get('specific_remind'))

    # BPM 訂單狀態
    bpm_status_list: list = []
    if kwargs.get('bpm_form_processing') == '1':
        bpm_status_list.append('0')  # 處理中
    if kwargs.get('bpm_form_passed') == '1':
        bpm_status_list.append('1')  # 已通過
    if kwargs.get('bpm_form_rejected') == '1':
        bpm_status_list.append('-1')  # 已退回

    # 如果有勾選任何 BPM 表單狀態,才加入條件
    if bpm_status_list:
        placeholders = ','.join(['?' for _ in range(len(bpm_status_list))])
        where_sql += f' AND bs.status IN ({placeholders})'
        param.extend(bpm_status_list)

    # BPM 生產單狀態
    bpm_generate_status_list: list = []
    if kwargs.get('bpm_generate_processing') == '1':
        bpm_generate_status_list.append('0')  # 處理中
    if kwargs.get('bpm_generate_passed') == '1':
        bpm_generate_status_list.append('1')  # 已通過
    if kwargs.get('bpm_generate_rejected') == '1':
        bpm_generate_status_list.append('-1')  # 已退回

    # 如果有勾選任何 BPM 表單狀態,才加入條件
    if bpm_generate_status_list:
        placeholders = ','.join(['?' for _ in range(len(bpm_generate_status_list))])
        where_sql += f' AND gb.status IN ({placeholders})'
        param.extend(bpm_generate_status_list)

    # 如果有勾選任何 BPM 表單狀態,才加入條件
    if bpm_generate_status_list:
        placeholders = ','.join(['?' for _ in range(len(bpm_generate_status_list))])
        where_sql += f' AND gb.status IN ({placeholders})'
        param.extend(bpm_generate_status_list)

        # 報價單結案狀態篩選
    sales_quotation_close = kwargs.get('sales_quotation_close', '0')
    sales_quotation_open = kwargs.get('sales_quotation_open', '0')
    
    # 只有當兩個參數不同時才加入篩選條件 (一個為'1'另一個為'0')
    if sales_quotation_close != sales_quotation_open:
        if sales_quotation_close == '1':
            # 報價單已結案篩選 (bpm_form_id 必須有值且狀態為1,且所有 bpm_generate_id 如有值則狀態必須為 1)
            where_sql += """ AND ob.sales_quotation_url IN (
                SELECT sales_quotation_url
                FROM (
                    SELECT 
                        sq1.sales_quotation_url,
                        SUM(CASE WHEN sq1.bpm_form_id = '' THEN 1 ELSE 0 END) as empty_form_count,
                        SUM(CASE WHEN sq1.bpm_form_id <> '' AND ISNULL(bfs.status, '') <> '1' THEN 1 ELSE 0 END) as incomplete_form_count,
                        SUM(CASE 
                            WHEN sq1.bpm_generate_id <> '' 
                            AND ISNULL(gbs.status, '') <> '1'
                            THEN 1 ELSE 0 
                        END) as incomplete_generate_count
                    FROM order_manage_summary_b_to_b sq1
                    LEFT JOIN b2b_form_status bfs ON sq1.bpm_form_id = bfs.bpm_form_id
                    LEFT JOIN gift_box_form_status gbs ON sq1.bpm_generate_id = gbs.bpm_form_id
                    GROUP BY sq1.sales_quotation_url
                ) sub
                WHERE sub.empty_form_count = 0 
                AND sub.incomplete_form_count = 0 
                AND sub.incomplete_generate_count = 0
            )"""
        elif sales_quotation_open == '1':
            # 報價單未結案篩選 (與已結案相反的條件)
            where_sql += """ AND ob.sales_quotation_url IN (
                SELECT sales_quotation_url
                FROM (
                    SELECT 
                        sq1.sales_quotation_url,
                        SUM(CASE WHEN sq1.bpm_form_id = '' THEN 1 ELSE 0 END) as empty_form_count,
                        SUM(CASE WHEN sq1.bpm_form_id <> '' AND ISNULL(bfs.status, '') <> '1' THEN 1 ELSE 0 END) as incomplete_form_count,
                        SUM(CASE 
                            WHEN sq1.bpm_generate_id <> '' 
                            AND ISNULL(gbs.status, '') <> '1'
                            THEN 1 ELSE 0 
                        END) as incomplete_generate_count
                    FROM order_manage_summary_b_to_b sq1
                    LEFT JOIN b2b_form_status bfs ON sq1.bpm_form_id = bfs.bpm_form_id
                    LEFT JOIN gift_box_form_status gbs ON sq1.bpm_generate_id = gbs.bpm_form_id
                    GROUP BY sq1.sales_quotation_url
                ) sub
                WHERE sub.empty_form_count > 0 
                OR sub.incomplete_form_count > 0 
                OR sub.incomplete_generate_count > 0
            )"""

    msq = XinTeaSql()
    cmd: str = f"""-- 第一層 CTE:計算每個 sales_quotation_url 的群組編號
                    WITH OrdersWithGroup AS (
                        SELECT 
                            ob.order_key, ob.status, ob.customer_purchase_type, 
                            CONVERT(VARCHAR(10), ob.order_issue_date, 23) AS order_issue_date, 
                            ob.customer_contact, ob.sales_quotation_url,
                            ob.order_invoice_url, 
                            CONVERT(VARCHAR(10), ob.customer_estimate_decide_date, 23) AS customer_estimate_decide_date, 
                            CONVERT(VARCHAR(10), ob.earliest_arrival_date, 23) AS earliest_arrival_date, 
                            CONVERT(VARCHAR(10), ob.latest_arrival_date, 23) AS latest_arrival_date,
                            ob.customer_name, ob.company_title, ob.uniform_invoice_no, ob.address, 
                            ob.customer_window, ob.customer_phone, ob.customer_email, ob.payment_term,
                            ob.payment, ob.ele_invoice, ob.delivery_method, ob.order_remark, 
                            ob.xin_tea_connector, ob.xin_tea_connect_phone, ob.xin_tea_connect_email,
                            CASE 
                                WHEN ob.customization_order = '1' THEN '是' ELSE '否' 
                            END AS customization_order,
                            ob.product_and_customization_money, ob.check_money, ob.freight_per_piece_money, 
                            ob.freight_amount, ob.discount, ob.freight_discount, ob.total_freight, 
                            ob.product_and_customization_and_freight_money, ob.payment_processing_fee, 
                            ob.payment_processing_fee_discount, ob.total_payment_processing_fee, ob.final_total, 
                            ob.total_order_num, ob.delivery_order, ob.order_type, 
                            ob.item, ob.category, ob.item_name, ob.item_specific,
                            ob.customization_descript, ob.unit_price, ob.quantity, ob.discount1, 
                            ob.one_discount, ob.order_money, ob.standard_or_customization, 
                            ob.bom, ob.purchase_connect,
                            ob.product_descript_one, ob.product_descript_two, ob.detail_remark, 
                            ob.xin_tea_remark, ob.bpm_form_id, bs.status as bpm_form_status, 
                            ob.bpm_generate_id, gb.status as bpm_generate_status,
                            ob.sq_form_id, ob.import_name,
                            CONVERT(VARCHAR(19), ob.import_time, 120) AS import_time,
                            CONVERT(VARCHAR(19), ob.modify_time, 120) AS modify_time,
                            ob.customize_bom, 
                            CASE 
                                WHEN ob.specific_remind = '1' THEN '是' ELSE '否' 
                            END AS specific_remind,
                            CASE 
                                WHEN ob.bpm_form_must_update = '1' THEN '是' ELSE '否' 
                            END AS bpm_form_must_update,
                            CASE 
                                WHEN ob.bpm_generate_must_update = '1' THEN '是' ELSE '否' 
                            END AS bpm_generate_must_update,
                            ob.all_seq,
                            ob.generate_vendor,
                            ob.shipping_out_warehouse,
                            ob.is_direct_from_oem,
                            CONVERT(VARCHAR(19), ob.generate_bpm_form, 120) AS generate_bpm_form,
                            CONVERT(VARCHAR(19), ob.generate_bpm_generate, 120) AS generate_bpm_generate,
                            ob.generate_vendor_by_generate, ob.shipping_out_warehouse_by_generate,
                            ob.earliest_arrival_date_by_generate,
                            CONVERT(VARCHAR(10), ob.earliest_arrival_date_by_generate, 23) AS earliest_arrival_date_by_generate_str,
                            ob.different, ob.item_batch, ob.sales_quotation_type, ob.sales_quotation_name,
                            CONVERT(VARCHAR(10), ob.latest_arrival_date_by_generate, 23) AS latest_arrival_date_by_generate,
                            ob.package_descript_file, ob.bpm_form_level, ob.bpm_generate_level, 
                            CASE 
                                WHEN ob.upd_gs_remind_bpm_form = '1' THEN '是' ELSE '否' 
                            END AS upd_gs_remind_bpm_form,
                            CASE 
                                WHEN ob.upd_gs_remind_bpm_generate = '1' THEN '是' ELSE '否' 
                            END AS upd_gs_remind_bpm_generate,
                            -- 使用 DENSE_RANK 按 sales_quotation_url 和排序條件分配群組編號
                            DENSE_RANK() OVER (ORDER BY ob.earliest_arrival_date, ob.sales_quotation_url) AS group_number
                        FROM order_manage_summary_b_to_b AS ob
                        LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                        LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id
                        {where_sql}
                    )
                    -- 最終查詢
                    SELECT 
                        order_key, status, customer_purchase_type, order_issue_date, 
                        customer_contact, sales_quotation_url, order_invoice_url, 
                        customer_estimate_decide_date, earliest_arrival_date, latest_arrival_date,
                        customer_name, company_title, uniform_invoice_no, address, 
                        customer_window, customer_phone, customer_email, payment_term,
                        payment, ele_invoice, delivery_method, order_remark, 
                        xin_tea_connector, xin_tea_connect_phone, xin_tea_connect_email,
                        customization_order, product_and_customization_money, check_money, 
                        freight_per_piece_money, freight_amount, discount, freight_discount, 
                        total_freight, product_and_customization_and_freight_money, 
                        payment_processing_fee, payment_processing_fee_discount, 
                        total_payment_processing_fee, final_total, total_order_num, 
                        delivery_order, order_type, item, category, item_name, item_specific,
                        customization_descript, unit_price, quantity, discount1, one_discount, 
                        order_money, standard_or_customization, bom, purchase_connect,
                        product_descript_one, product_descript_two, detail_remark, xin_tea_remark, 
                        bpm_form_id, bpm_form_status, bpm_generate_id, bpm_generate_status,
                        sq_form_id, import_name, import_time, modify_time, customize_bom, 
                        specific_remind, bpm_form_must_update, bpm_generate_must_update,
                        -- 根據群組編號決定符號(奇數顯示○○,偶數顯示Ⅹ)
                        CASE 
                            WHEN group_number % 2 = 1 THEN '○○'
                            ELSE 'Ⅹ'
                        END AS branch_line,
                        generate_vendor, shipping_out_warehouse,
                        is_direct_from_oem, generate_bpm_form, generate_bpm_generate,
                        generate_vendor_by_generate, shipping_out_warehouse_by_generate,
                        earliest_arrival_date_by_generate_str as earliest_arrival_date_by_generate, 
                        different, item_batch, sales_quotation_type, sales_quotation_name,
                        latest_arrival_date_by_generate, all_seq, package_descript_file,
                        bpm_form_level, bpm_generate_level, upd_gs_remind_bpm_form, upd_gs_remind_bpm_generate
                    FROM OrdersWithGroup
                    ORDER BY earliest_arrival_date, sales_quotation_url, all_seq
        """
    return msq.s_qry(cmd, param)


def qry_bom_detail(bom: str) -> list:
    """
    查詢BOM明細(僅一階料)
    :param bom: BOM表單編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT '' as bom_detail_id, ib.item, ib.item_name, ib.s_item, ib.s_item_name, ib.s_item_spec, iad.unit, iad.category,
                  '' as customize_item,
                  ib.use_quantity, ob.quantity, 0 as adjustment_quantity, ib.use_quantity*ob.quantity+0 as total_quantity,
                  ib.origin_form_id, '' as customize_type, ib.use_quantity as origin_quantity, ob.quantity as order_quantity
                  FROM item_bom as ib
                  INNER JOIN order_manage_summary_b_to_b as ob on ob.bom = ib.origin_form_id 
                  INNER JOIN item_application_detail as iad on iad.item = ib.s_item
                  WHERE ib.origin_form_id = ? AND ib.item = ib.m_item AND ib.m_item <> ib.s_item 
                  ORDER BY ib.s_item"""
    return msq.s_qry(cmd, bom)



def qry_status_by_dashboard() -> list:
    """
    查詢狀態(儀表板用) 
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM status WHERE dashboard='1'
                  order by status_id"""
    return msq.s_qry(cmd)



def qry_order_by_status(status: str) -> list:
    """
    查詢訂單資料by訂單狀態
    :param status: 訂單狀態
    """
    msq = XinTeaSql()
    cmd: str = """SELECT COUNT(*) AS order_count
                FROM order_manage_summary_b_to_b
                WHERE status = ?"""
    return msq.s_qry(cmd, status)


def qry_sales_quotation(sq_form_id: str) -> list:
    """
    查詢報價單資料
    :param sq_form_id: 報價單表單編號
    """
    msq = XinTeaSql()
    cmd: str = """
               SELECT ob.order_key, ob.status, ob.customer_purchase_type, CONVERT(VARCHAR(10), ob.order_issue_date, 23) AS order_issue_date, ob.customer_contact, 
                ob.sales_quotation_url,
                ob.order_invoice_url, CONVERT(VARCHAR(10), ob.customer_estimate_decide_date, 23) AS customer_estimate_decide_date, 
                CONVERT(VARCHAR(10), ob.earliest_arrival_date, 23) AS earliest_arrival_date, 
                CONVERT(VARCHAR(10), ob.latest_arrival_date, 23) AS latest_arrival_date,
                ob.customer_name, ob.company_title, ob.uniform_invoice_no, ob.address, ob.customer_window, ob.customer_phone, ob.customer_email, ob.payment_term,
                ob.payment, ob.ele_invoice, ob.delivery_method, ob.order_remark, ob.xin_tea_connector, ob.xin_tea_connect_phone, ob.xin_tea_connect_email,
                CASE 
                    WHEN ob.customization_order = '1' THEN '是' ELSE '否' 
                END AS customization_order,
                ob.product_and_customization_money, ob.check_money, ob.freight_per_piece_money, ob.freight_amount, ob.discount,
                ob.freight_discount, ob.total_freight, ob.product_and_customization_and_freight_money, ob.payment_processing_fee, 
                ob.payment_processing_fee_discount,
                ob.total_payment_processing_fee, ob.final_total, ob.total_order_num, ob.delivery_order, ob.order_type, 
                ob.item, ob.category, ob.item_name, ob.item_specific,
                ob.customization_descript, ob.unit_price, ob.quantity, ob.discount1, ob.one_discount, ob.order_money, 
                ob.standard_or_customization, ob.bom, ob.purchase_connect,
                ob.product_descript_one, ob.product_descript_two, ob.detail_remark, ob.xin_tea_remark, ob.bpm_form_id, 
                bfs.status as bpm_form_status, ob.bpm_generate_id, gbs.status as bpm_generate_status,
                ob.sq_form_id, ob.import_name,
                CONVERT(VARCHAR(19), ob.import_time, 120) AS import_time,
                CONVERT(VARCHAR(19), ob.modify_time, 120) AS modify_time,
                ob.customize_bom, 
                CASE WHEN ob.specific_remind = '1' THEN '是' ELSE '否' END AS specific_remind,
                CASE WHEN ob.bpm_form_must_update = '1' THEN '是' ELSE '否' END AS bpm_form_must_update,
                CASE WHEN ob.bpm_generate_must_update = '1' THEN '是' ELSE '否' END AS bpm_generate_must_update,
                CASE WHEN ob.additional_order = '1' THEN '是' ELSE '否' END AS additional_order,
                ob.generate_vendor, ob.shipping_out_warehouse, ob.different, ob.item_batch,
                ob.sales_quotation_type, ob.sales_quotation_name
                FROM order_manage_summary_b_to_b as ob
                LEFT JOIN b2b_form_status as bfs on bfs.bpm_form_id = ob.bpm_form_id
                LEFT JOIN gift_box_form_status as gbs on gbs.bpm_form_id = ob.bpm_generate_id
                WHERE ob.sq_form_id = ?
                ORDER BY all_seq"""
    return msq.s_qry(cmd, sq_form_id)


def qry_customize_bom(bom: str) -> list:
    """
    查詢客製BOM
    :param bom: BOM表單單號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT cb.bom_detail_id, cb.item, iad2.item_name, cb.s_item, cb.s_item_name, cb.s_item_spec, iad.unit,
                  iad.category,
                  cb.customize_item, 
                  ISNULL(ib.use_quantity, 0) as origin_quantity,
                  cb.use_quantity, ob.quantity*cb.use_quantity as quantity,
                  cb.adjustment_quantity, cb.use_quantity*ob.quantity+cb.adjustment_quantity as total_quantity, 
                  cb.bom, cb.customize_type, ob.quantity as order_quantity, cb.average
                  FROM customize_bom as cb
                  INNER JOIN order_manage_summary_b_to_b as ob on ob.customize_bom = cb.bom
                  INNER JOIN item_application_detail as iad on cb.s_item = iad.item
                  INNER JOIN item_application_detail as iad2 on cb.item = iad2.item
                  LEFT JOIN item_bom as ib on ib.origin_form_id = ob.bom and cb.s_item = ib.s_item
                  WHERE cb.bom = ?
                  ORDER BY bom_detail_seq asc"""
    return msq.s_qry(cmd, bom)


def crt_upd_customize_bpm(crt_data: list, upd_data: list, upd_order_detail_customize_bom: list,
                          upd_spare_order_detail_num: list, upd_add_manually_item: list,
                          upd_order_detail_bpm_generate_must_update: list,
                          upd_order_detail_bpm_form_must_update: list,
                          add_customize_bom_and_gs_url: list, upd_different_data: list,
                          upd_order_detaild_diff: list, delete_origin_diff: list,
                          upd_order_quantity: list, upd_add_additional_item: list,
                          upd_other_item: list) -> list:
    """
    新增/更新客製BOM
    :param crt_data: 新增資料
    :param upd_data: 更新資料
    :param upd_order_detail_customize_bom: 更新訂單明細客製BOM
    :param upd_spare_order_detail_num: 更新訂單明細備用料件數量
    :param upd_add_manually_item: 更新手動新增料件
    :param upd_order_detail_bpm_generate_must_update: 更新訂單明細BPM生產單須更新
    :param upd_order_detail_bpm_form_must_update: 更新訂單明細BPM訂單須更新
    :param add_customize_bom_and_gs_url: 新增客製BOM與報價單網址關係
    :param upd_order_detaild_diff: 新增差異數訂單明細
    :param delete_origin_diff: 刪除原有差異數
    :param upd_order_quantity: 更新訂單數量
    :param upd_add_additional_item: 更新外購品料件
    :param upd_other_item: 更新外購品平均用量
    """
    msq = XinTeaSql()
    crt_cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, s_item, s_item_name,
                      s_item_spec, unit, customize_item, use_quantity, adjustment_quantity,
                      bom, bom_detail_seq)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"""
    upd_cmd: str = """UPDATE customize_bom
                      SET item = ?, m_item = ?, s_item = ?, s_item_name = ?,
                          s_item_spec = ?, unit = ?, customize_item = ?, use_quantity = ?,
                          adjustment_quantity = ?, manual_update='1' WHERE bom_detail_id = ?"""
    upd_order_detail_customize_bom_cmd: str = """UPDATE order_manage_summary_b_to_b
                                                 SET customize_bom = ?, specific_remind = '0'
                                                 WHERE order_key = ?"""
    upd_spare_order_detail_num_cmd: str = """UPDATE order_manage_summary_b_to_b
                                             SET different = different+?
                                             WHERE spare_item = ? and sales_quotation_url = ?"""
    upd_add_manually_item_cmd: str = """UPDATE order_manage_summary_b_to_b
                                         SET different = different+?
                                         WHERE add_manually_item = ? and item = ?"""
    upd_add_additional_item_cmd: str = """UPDATE order_manage_summary_b_to_b
                                          SET different = different+?
                                          WHERE additional_order = '0' and item_type='外購品' and item = ?"""
    upd_order_detail_bpm_generate_must_update_cmd: str = """UPDATE order_manage_summary_b_to_b
                                                          SET bpm_generate_must_update = '1'
                                                          WHERE order_key = ?"""
    upd_order_detail_bpm_form_must_update_cmd: str = """UPDATE order_manage_summary_b_to_b
                                                            SET bpm_form_must_update = '1'
                                                            WHERE sales_quotation_url = ?"""
    add_customize_bom_and_gs_url_cmd: str = """INSERT INTO customize_bom_and_gs_url(customize_bom, gs_url) VALUES(?,?)"""
    upd_different_data_cmd: str = """UPDATE order_manage_summary_b_to_b SET different = different+? WHERE sales_quotation_url = ? AND item = ?"""
    upd_order_detaild_diff_cmd: str = """INSERT INTO order_manage_summary_b_to_b (
                                    order_key, status, customer_purchase_type,
                                    order_issue_date, customer_contact,
                                    sales_quotation_url, order_invoice_url,
                                    customer_estimate_decide_date, earliest_arrival_date,
                                    latest_arrival_date, customer_name, company_title,
                                    uniform_invoice_no, address, customer_window,
                                    customer_phone, customer_email, payment_term,
                                    payment, ele_invoice, delivery_method,
                                    order_remark, xin_tea_connector,
                                    xin_tea_connect_phone, xin_tea_connect_email,
                                    customization_order, product_and_customization_money,
                                    check_money, freight_per_piece_money,
                                    freight_amount, discount, freight_discount,
                                    total_freight, product_and_customization_and_freight_money,
                                    payment_processing_fee, payment_processing_fee_discount,
                                    total_payment_processing_fee, final_total, total_order_num,
                                    delivery_order, order_type, item, category,
                                    item_name, item_specific, customization_descript,
                                    unit_price, quantity, discount1, one_discount,
                                    order_money, standard_or_customization, bom,
                                    customize_bom, purchase_connect, product_descript_one,
                                    product_descript_two, detail_remark,
                                    xin_tea_remark, bpm_form_id, bpm_form_status, bpm_generate_id,
                                    bpm_generate_status, sq_form_id, import_name, order_seq,
                                    spare_item, additional_order, add_manually_item, bpm_form_must_update,
                                    generate_vendor, shipping_out_warehouse, generate_vendor_by_generate,
                                    shipping_out_warehouse_by_generate, earliest_arrival_date_by_generate,
                                    different, diff_item, diff_item_bom, sales_quotation_type, is_direct_from_oem,
                                    sales_quotation_name
                                )
                                VALUES (
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?
                                )"""
    delete_origin_diff_cmd: str = """DELETE FROM order_manage_summary_b_to_b WHERE diff_item = '1' and diff_item_bom = ?"""
    # 更新外購品平均用量
    upd_other_item_cmd: str = """UPDATE customize_bom SET average = ? WHERE bom_detail_id = ?"""
    # 重新計算訂單數量
    upd_order_quantity_cmd: str = """UPDATE order_manage_summary_b_to_b 
                                        SET total_order_num = (
                                            SELECT SUM(quantity) 
                                            FROM order_manage_summary_b_to_b AS sub
                                            WHERE sub.sales_quotation_url = order_manage_summary_b_to_b.sales_quotation_url
                                        )
                                        WHERE sales_quotation_url = ?"""
    cmds_param: list = [
        (
            upd_order_detail_customize_bom_cmd, upd_order_detail_customize_bom
        )
    ]
    if crt_data:
        cmds_param.append((crt_cmd, crt_data))
    if upd_data:
        cmds_param.append((upd_cmd, upd_data))
    if upd_spare_order_detail_num:
        cmds_param.append((upd_spare_order_detail_num_cmd, upd_spare_order_detail_num))
    if upd_add_manually_item:
        cmds_param.append((upd_add_manually_item_cmd, upd_add_manually_item))
    if upd_add_additional_item:
        cmds_param.append((upd_add_additional_item_cmd, upd_add_additional_item))
    if upd_order_detail_bpm_generate_must_update:
        cmds_param.append((upd_order_detail_bpm_generate_must_update_cmd, upd_order_detail_bpm_generate_must_update))
    if upd_order_detail_bpm_form_must_update:
        cmds_param.append((upd_order_detail_bpm_form_must_update_cmd, upd_order_detail_bpm_form_must_update))
    if add_customize_bom_and_gs_url:
        cmds_param.append((add_customize_bom_and_gs_url_cmd, add_customize_bom_and_gs_url))
    if upd_different_data:
        cmds_param.append((upd_different_data_cmd, upd_different_data))
    #if delete_origin_diff:
    #    cmds_param.append((delete_origin_diff_cmd, delete_origin_diff))
    if upd_order_detaild_diff:
        cmds_param.append((upd_order_detaild_diff_cmd, upd_order_detaild_diff))
    if upd_order_quantity:
        cmds_param.append((upd_order_quantity_cmd, upd_order_quantity))
    if upd_other_item:
        cmds_param.append((upd_other_item_cmd, upd_other_item))
    return msq.transaction_v2(cmds_param)


def qry_customize_bom_item() -> list:
    """
    查詢可客製料件
    """
    msq = XinTeaSql()
    cmd: str = """select ci.item, iad.item_name
                  FROM customize_item as ci
                  INNER JOIN item_application_detail as iad on ci.item = iad.item"""
    return msq.s_qry(cmd)



def crt_customize_bom_item(crt_bom: list, crt_order_detail: list) -> bool:
    """
    新增客製BOM客製料件/新增訂單明細(客製品)
    :param crt_bom: 新增BOM資料
    :param crt_order_detail: 新增訂單明細
    """
    msq = XinTeaSql()
    cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, s_item, 
                  s_item_name, s_item_spec, unit,
                  customize_item, use_quantity, adjustment_quantity, bom, bom_detail_seq,
                  manual_update, customize_type
                  )
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    crt_order_detail_cmd: str = """INSERT INTO order_manage_summary_b_to_b (
                                    order_key, status, customer_purchase_type,
                                    order_issue_date, customer_contact,
                                    sales_quotation_url, order_invoice_url,
                                    customer_estimate_decide_date, earliest_arrival_date,
                                    latest_arrival_date, customer_name, company_title,
                                    uniform_invoice_no, address, customer_window,
                                    customer_phone, customer_email, payment_term,
                                    payment, ele_invoice, delivery_method,
                                    order_remark, xin_tea_connector,
                                    xin_tea_connect_phone, xin_tea_connect_email,
                                    customization_order, product_and_customization_money,
                                    check_money, freight_per_piece_money,
                                    freight_amount, discount, freight_discount,
                                    total_freight, product_and_customization_and_freight_money,
                                    payment_processing_fee, payment_processing_fee_discount,
                                    total_payment_processing_fee, final_total, total_order_num,
                                    delivery_order, order_type, item, category,
                                    item_name, item_specific, customization_descript,
                                    unit_price, quantity, discount1, one_discount,
                                    order_money, standard_or_customization, bom,
                                    customize_bom, purchase_connect, product_descript_one,
                                    product_descript_two, detail_remark,
                                    xin_tea_remark, bpm_form_id, bpm_form_status, bpm_generate_id,
                                    bpm_generate_status, sq_form_id, import_name, order_seq,
                                    spare_item, additional_order, add_manually_item, bpm_form_must_update,
                                    generate_vendor, shipping_out_warehouse, generate_vendor_by_generate,
                                    shipping_out_warehouse_by_generate, earliest_arrival_date_by_generate,
                                    different
                                )
                                VALUES (
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?
                                )"""
    cmds_param: list = [
        (
            cmd, crt_bom
        ),
        #(
        #    crt_order_detail_cmd, crt_order_detail
        #)
    ]
    return msq.transaction_v2(cmds_param)


def qry_order_manage_summary_b_to_b_by_sales_quotation(gs_url: str) -> list:
    """
    查詢訂單管理總表B2B by 報價單網址
    :param gs_url: 報價單網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b WHERE sales_quotation_url = ?
                  ORDER BY order_seq"""
    return msq.s_qry(cmd, gs_url)


def qry_item_by_item_id(item_id: str) -> list:
    """
    查詢料件資料by料件編號
    :param item_id: 料件編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM item_application_detail WHERE item = ?"""
    return msq.s_qry(cmd, item_id)


def qry_order_detail_by_order_key(order_key: str) -> list:
    """
    查詢訂單明細by訂單編號
    :param order_key: 訂單編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b WHERE order_key = ?"""
    return msq.s_qry(cmd, order_key)



def qry_order_manage_summary_b_to_b_by_sq_id(sq_id: str) -> list:
    """
    查詢訂單管理總表B2B by 報價單編號
    :param gs_url: 報價單編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT 
                    MAX(ob.order_key) as order_key,
                    MAX(ob.status) as status,
                    MAX(ob.customer_purchase_type) as customer_purchase_type,
                    MAX(CONVERT(VARCHAR(10), ob.order_issue_date, 23)) AS order_issue_date,
                    MAX(ob.customer_contact) as customer_contact,
                    MAX(ob.sales_quotation_url) as sales_quotation_url,
                    MAX(ob.order_invoice_url) as order_invoice_url,
                    MAX(CONVERT(VARCHAR(10), ob.customer_estimate_decide_date, 23)) AS customer_estimate_decide_date,
                    MAX(CONVERT(VARCHAR(10), ob.earliest_arrival_date, 23)) AS earliest_arrival_date,
                    MAX(CONVERT(VARCHAR(10), ob.latest_arrival_date, 23)) AS latest_arrival_date,
                    MAX(ob.customer_name) as customer_name,
                    MAX(ob.company_title) as company_title,
                    MAX(ob.uniform_invoice_no) as uniform_invoice_no,
                    MAX(ob.address) as address,
                    MAX(ob.customer_window) as customer_window,
                    MAX(ob.customer_phone) as customer_phone,
                    MAX(ob.customer_email) as customer_email,
                    MAX(ob.payment_term) as payment_term,
                    MAX(ob.payment) as payment,
                    MAX(ob.ele_invoice) as ele_invoice,
                    MAX(ob.delivery_method) as delivery_method,
                    MAX(ob.order_remark) as order_remark,
                    MAX(ob.xin_tea_connector) as xin_tea_connector,
                    MAX(ob.xin_tea_connect_phone) as xin_tea_connect_phone,
                    MAX(ob.xin_tea_connect_email) as xin_tea_connect_email,
                    MAX(CASE WHEN ob.customization_order = '1' THEN '是' ELSE '否' END) AS customization_order,
                    MAX(ob.product_and_customization_money) as product_and_customization_money,
                    MAX(ob.check_money) as check_money,
                    MAX(ob.freight_per_piece_money) as freight_per_piece_money,
                    MAX(ob.freight_amount) as freight_amount,
                    MAX(ob.discount) as discount,
                    MAX(ob.freight_discount) as freight_discount,
                    MAX(ob.total_freight) as total_freight,
                    MAX(ob.product_and_customization_and_freight_money) as product_and_customization_and_freight_money,
                    MAX(ob.payment_processing_fee) as payment_processing_fee,
                    MAX(ob.payment_processing_fee_discount) as payment_processing_fee_discount,
                    MAX(ob.total_payment_processing_fee) as total_payment_processing_fee,
                    MAX(ob.final_total) as final_total,
                    MAX(ob.total_order_num) as total_order_num,
                    MAX(ob.delivery_order) as delivery_order,
                    MAX(ob.order_type) as order_type,
                    ob.item,  -- 用於分組的欄位
                    MAX(ob.category) as category,
                    MAX(ob.item_name) as item_name,
                    MAX(ob.item_specific) as item_specific,
                    MAX(ob.customization_descript) as customization_descript,
                    MAX(ob.unit_price) as unit_price,
                    SUM(ob.quantity) as quantity,  -- 數量加總
                    MAX(ob.quantity) as max_quantity,
                    MAX(ob.discount1) as discount1,
                    MAX(ob.one_discount) as one_discount,
                    SUM(ob.order_money) as order_money,  -- 訂單金額加總
                    MAX(ob.standard_or_customization) as standard_or_customization,
                    ISNULL(MAX(ob.bom), '') as bom,
                    MAX(ob.purchase_connect) as purchase_connect,
                    MAX(ob.product_descript_one) as product_descript_one,
                    MAX(ob.product_descript_two) as product_descript_two,
                    MAX(ob.detail_remark) as detail_remark,
                    MAX(ob.xin_tea_remark) as xin_tea_remark,
                    MAX(ob.bpm_form_id) as bpm_form_id,
                    MAX(bfs.status) as bpm_form_status,
                    MAX(ob.bpm_generate_id) as bpm_generate_id,
                    MAX(gbs.status) as bpm_generate_status,
                    MAX(ob.sq_form_id) as sq_form_id,
                    MAX(ob.import_name) as import_name,
                    MAX(CONVERT(VARCHAR(19), ob.import_time, 120)) AS import_time,
                    MAX(CONVERT(VARCHAR(19), ob.modify_time, 120)) AS modify_time,
                    MAX(ob.customize_bom) as customize_bom,
                    MAX(CASE WHEN ob.specific_remind = '1' THEN '是' ELSE '否' END) AS specific_remind,
                    MAX(ob.is_direct_from_oem) AS is_direct_from_oem,
                    MAX(ob.different) as different,
                    MAX(ob.sales_quotation_type) as sales_quotation_type,
                    MIN(ob.all_seq) as all_seq,
                    MAX(ob.sales_quotation_name) as sales_quotation_name
                FROM order_manage_summary_b_to_b as ob
                LEFT JOIN b2b_form_status as bfs on bfs.bpm_form_id = ob.bpm_form_id
                LEFT JOIN gift_box_form_status as gbs on gbs.bpm_form_id = ob.bpm_generate_id
                WHERE ob.sq_form_id = ?
                GROUP BY ob.item, ob.item_batch  -- 依料號分組
                ORDER BY all_seq"""
    return msq.s_qry(cmd, sq_id)


def upd_genereate_b_to_b_order(upd_b_to_b_new_form_id: list, crt_b_to_b_order_status: list,
                               clear_update_remind: list) -> bool:
    """
    更新B2B銷售訂單產生後的BPM單號
    :param upd_b_to_b_new_form_id: 更新B2B銷售訂單的BPM單號
    :param crt_b_to_b_order_status: 新增B2B訂單狀態
    :param clear_update_remind: 清除更新提醒
    """
    msq = XinTeaSql()
    cmd: str = """UPDATE order_manage_summary_b_to_b
                  SET bpm_form_id = ?, bpm_form_status='0', generate_bpm_form=GETDATE(), upd_gs_remind_bpm_form='1',
                  bpm_form_level = ?
                  WHERE sq_form_id = ?"""
    crt_b_to_b_order_status_cmd: str = """INSERT INTO b2b_form_status (bpm_form_id, status) VALUES (?,?)"""
    clear_update_remind_cmd: str = """UPDATE order_manage_summary_b_to_b
                                       SET bpm_form_must_update = '0'
                                       WHERE sq_form_id = ?"""
    cmds_param: list = []
    if upd_b_to_b_new_form_id:
        cmds_param.append((cmd, upd_b_to_b_new_form_id))
    if crt_b_to_b_order_status:
        cmds_param.append((crt_b_to_b_order_status_cmd, crt_b_to_b_order_status))
    if clear_update_remind:
        cmds_param.append((clear_update_remind_cmd, clear_update_remind))
    return msq.transaction_v2(cmds_param)


def delete_b_to_b_order_status(delete_param: list, clear_b_to_b_order_form: list) -> bool:
    """
    刪除B2B訂單狀態
    :param delete_param: list 刪除參數
    :param clear_b_to_b_order_form: list 清除B2B訂單明細的BPM單號
    """
    msq = XinTeaSql()
    cmd: str = """DELETE FROM b2b_form_status WHERE bpm_form_id = ?"""
    clear_b_to_b_order_form_cmd: str = """UPDATE order_manage_summary_b_to_b 
                                          SET bpm_form_id = '', bpm_form_status='',
                                          bpm_form_must_update = '0'
                                          WHERE sq_form_id = ?"""
    cmds_param: list = [
        (cmd, delete_param),
        (clear_b_to_b_order_form_cmd, clear_b_to_b_order_form)
    ]
    return msq.transaction_v2(cmds_param)


def qry_to_generate_gift() -> list:
    """
    查詢可拋轉生產單
    """
    msq = XinTeaSql()
    cmd: str = """SELECT *
                  FROM item_category
                  WHERE is_spread_calculate='1' AND is_bom='1'"""
    return msq.s_qry(cmd)


def crt_or_update_gift_box_form_status(crt_gift_box_status: list, upd_b_to_b_new_form_id: list,
                                       clear_update_remind: list) -> bool:
    """
    新增/更新B2B訂單狀態/更新B2B訂單明細的禮盒生產單號
    :param crt_gift_box_status: 新增禮盒生產單狀態
    :param upd_b_to_b_new_form_id: 更新B2B訂單明細的禮盒生產單號
    :param clear_update_remind: 清除更新提醒
    """
    msq = XinTeaSql()
    crt_gift_box_status_cmd: str = """INSERT INTO gift_box_form_status (bpm_form_id, status) VALUES(?,?)"""
    upd_b_to_b_new_form_id_cmd: str = """UPDATE order_manage_summary_b_to_b
                                         SET bpm_generate_id = ?, bpm_generate_status = ?, generate_bpm_generate=GETDATE(),
                                         upd_gs_remind_bpm_generate='1', bpm_generate_level = ?
                                         WHERE order_key = ?"""
    clear_update_remind_cmd: str = """UPDATE order_manage_summary_b_to_b
                                       SET bpm_generate_must_update = '0'
                                       WHERE order_key = ?"""
    cmds_param: list = []
    if crt_gift_box_status:
        cmds_param.append((crt_gift_box_status_cmd, crt_gift_box_status))
    if upd_b_to_b_new_form_id:
        cmds_param.append((upd_b_to_b_new_form_id_cmd, upd_b_to_b_new_form_id))
    if clear_update_remind:
        cmds_param.append((clear_update_remind_cmd, clear_update_remind))
    return msq.transaction_v2(cmds_param)



def delete_gift_box_form(delete_gift_box_status: list, clear_gift_box_form: list) -> bool:
    """
    刪除禮盒生產單狀態/清除B2B訂單明細的禮盒生產單號
    :param delete_gift_box_status: 刪除禮盒生產單狀態參數
    :param clear_gift_box_form: 清除B2B訂單明細的禮盒生產單號參數
    """
    msq = XinTeaSql()
    delete_gift_box_status_cmd: str = """DELETE FROM gift_box_form_status WHERE bpm_form_id = ?"""
    clear_gift_box_form_cmd: str = """UPDATE order_manage_summary_b_to_b 
                                      SET bpm_generate_id = '', bpm_generate_status = '',
                                      bpm_generate_must_update = '0'
                                      WHERE order_key = ?"""
    cmds_param: list = []
    if delete_gift_box_status:
        cmds_param.append((delete_gift_box_status_cmd, delete_gift_box_status))
    if clear_gift_box_form:
        cmds_param.append((clear_gift_box_form_cmd, clear_gift_box_form))
    return msq.transaction_v2(cmds_param)



def qry_order_manage_summary_b_to_b_gift_box(bpm_generate_id: str) -> list:
    """
    查詢訂單管理總表B2B by 禮盒生產單單號
    :param bpm_generate_id: 禮盒生產單單號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT ob.order_key, ob.status, ob.customer_purchase_type, CONVERT(VARCHAR(10), ob.order_issue_date, 23) AS order_issue_date, ob.customer_contact, 
                        ob.sales_quotation_url,
                        ob.order_invoice_url, CONVERT(VARCHAR(10), ob.customer_estimate_decide_date, 23) AS customer_estimate_decide_date, 
                        CONVERT(VARCHAR(10), ob.earliest_arrival_date, 23) AS earliest_arrival_date, 
                        CONVERT(VARCHAR(10), ob.latest_arrival_date, 23) AS latest_arrival_date,
                        ob.customer_name, ob.company_title, ob.uniform_invoice_no, ob.address, ob.customer_window, ob.customer_phone, 
                        ob.customer_email, ob.payment_term,
                        ob.payment, ob.ele_invoice, ob.delivery_method, ob.order_remark, ob.xin_tea_connector, ob.xin_tea_connect_phone, 
                        ob.xin_tea_connect_email,
                        CASE 
                            WHEN ob.customization_order = '1' THEN '是' ELSE '否' 
                        END AS customization_order,
                        ob.product_and_customization_money, ob.check_money, ob.freight_per_piece_money, ob.freight_amount, ob.discount,
                        ob.freight_discount, ob.total_freight, ob.product_and_customization_and_freight_money, ob.payment_processing_fee, 
                        ob.payment_processing_fee_discount,
                        ob.total_payment_processing_fee, ob.final_total, ob.total_order_num, ob.delivery_order, ob.order_type, ob.item, 
                        ob.category, ob.item_name, ob.item_specific,
                        ob.customization_descript, ob.unit_price, ob.quantity, ob.discount1, ob.one_discount, ob.order_money, 
                        ob.standard_or_customization, bom, purchase_connect,
                        ob.product_descript_one, ob.product_descript_two, ob.detail_remark, ob.xin_tea_remark, 
                        ob.bpm_form_id, bfs.status as bpm_form_status, 
                        ob.bpm_generate_id, gbs.status as bpm_generate_status,
                        ob.sq_form_id, ob.import_name,
                        CONVERT(VARCHAR(19), ob.import_time, 120) AS import_time,
                        CONVERT(VARCHAR(19), ob.modify_time, 120) AS modify_time,
                        ob.customize_bom, 
                        CASE 
                            WHEN ob.specific_remind = '1' THEN '是' ELSE '否' 
                        END AS specific_remind, ob.generate_vendor, ob.shipping_out_warehouse,
                        ob.order_seq, 
                        ob.generate_vendor_by_generate, ob.shipping_out_warehouse_by_generate,
                        CONVERT(VARCHAR(10), ob.earliest_arrival_date_by_generate, 23) AS earliest_arrival_date_by_generate,
                        ob.different,
                        CONVERT(VARCHAR(10), ob.latest_arrival_date_by_generate, 23) AS latest_arrival_date_by_generate,
                        ob.package_descript_file, ob.item_batch
                    FROM order_manage_summary_b_to_b as ob
                    LEFT JOIN b2b_form_status as bfs on bfs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status as gbs on gbs.bpm_form_id = ob.bpm_generate_id
                    WHERE ob.order_key = ?
                    ORDER BY ob.order_seq"""
    return msq.s_qry(cmd, bpm_generate_id)



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


def upd_work_task_error(task_id: str, error_message: str) -> bool:
    """
    更新工作任務(失敗)
    :param task_id: 工作任務ID
    """
    msq = XinTeaSql()
    cmd = """UPDATE work_task SET success='-1', message=? WHERE task_id=?"""
    cmds_param: list = [
        (cmd, [(error_message, task_id)])
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



def qry_all_status_select() -> list:
    """
    查詢所有狀態下拉選單
    """
    msq = XinTeaSql()
    cmd = """select su.status_id, su.can_use, s.status_name, s.select_name
             FROM status_use as su
             INNER JOIN status as s on su.can_use = s.status_id"""
    return msq.s_qry(cmd)


def qry_customize_bom_item_exist(customize_bom_id: str, item: str) -> list:
    """
    查詢客製BOM料件是否存在(手動新增)
    :param customize_bom_id: 客製BOM編號
    :param item: 料件編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM customize_bom WHERE bom = ? AND s_item = ? AND customize_type=N'手動增加'"""
    return msq.s_qry(cmd, customize_bom_id, item)



def qry_order_manage_summary_b_to_b_by_order_key(order_key: str) -> list:
    """
    查詢訂單管理總表B2B by 訂單編號
    :param order_key: 訂單編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT ob.order_key, ob.status, ob.customer_purchase_type, CONVERT(VARCHAR(10), ob.order_issue_date, 23) AS order_issue_date, ob.customer_contact, 
                        ob.sales_quotation_url,
                        ob.order_invoice_url, CONVERT(VARCHAR(10), ob.customer_estimate_decide_date, 23) AS customer_estimate_decide_date, 
                        CONVERT(VARCHAR(10), ob.earliest_arrival_date, 23) AS earliest_arrival_date, 
                        CONVERT(VARCHAR(10), ob.latest_arrival_date, 23) AS latest_arrival_date,
                        ob.customer_name, ob.company_title, ob.uniform_invoice_no, ob.address, ob.customer_window, ob.customer_phone, 
                        ob.customer_email, ob.payment_term,
                        ob.payment, ob.ele_invoice, ob.delivery_method, ob.order_remark, ob.xin_tea_connector, ob.xin_tea_connect_phone, 
                        ob.xin_tea_connect_email,
                        CASE 
                            WHEN ob.customization_order = '1' THEN '是' ELSE '否' 
                        END AS customization_order,
                        ob.product_and_customization_money, ob.check_money, ob.freight_per_piece_money, ob.freight_amount, ob.discount,
                        ob.freight_discount, ob.total_freight, ob.product_and_customization_and_freight_money, ob.payment_processing_fee, 
                        ob.payment_processing_fee_discount,
                        ob.total_payment_processing_fee, ob.final_total, ob.total_order_num, ob.delivery_order, ob.order_type, ob.item, 
                        ob.category, ob.item_name, ob.item_specific,
                        ob.customization_descript, ob.unit_price, ob.quantity, ob.discount1, ob.one_discount, ob.order_money, 
                        ob.standard_or_customization, bom, purchase_connect,
                        ob.product_descript_one, ob.product_descript_two, ob.detail_remark, ob.xin_tea_remark, 
                        ob.bpm_form_id, bfs.status as bpm_form_status, 
                        ob.bpm_generate_id, gbs.status as bpm_generate_status,
                        ob.sq_form_id, ob.import_name,
                        CONVERT(VARCHAR(19), ob.import_time, 120) AS import_time,
                        CONVERT(VARCHAR(19), ob.modify_time, 120) AS modify_time,
                        ob.customize_bom, 
                        CASE 
                            WHEN ob.specific_remind = '1' THEN '是' ELSE '否' 
                        END AS specific_remind
                    FROM order_manage_summary_b_to_b as ob
                    LEFT JOIN b2b_form_status as bfs on bfs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status as gbs on gbs.bpm_form_id = ob.bpm_generate_id
                    WHERE ob.order_key = ?
                    ORDER BY ob.order_seq"""
    return msq.s_qry(cmd, order_key)


def qry_calendar_start_date() -> list:
    """
    查詢行事曆起始日期
    """
    msq = XinTeaSql()
    cmd: str = """SELECT value FROM param WHERE param_name = N'行事曆起始日'"""
    return msq.s_qry(cmd)


def qry_vendor_data(vendor_name: str) -> list:
    """
    查詢廠商資料
    :param vendor_name: 廠商名稱
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM vendor WHERE vendor_name = ?"""
    return msq.s_qry(cmd, vendor_name)



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


def upd_order_head_detail(upd_data: list, upd_bpm_form_must_update: list, upd_bpm_generate_must_update: list) -> bool:
    """
    更新訂單表頭資料
    :param upd_data: 更新資料
    :param upd_bpm_form_must_update: 更新BPM訂單須更新提醒
    :param upd_bpm_generate_must_update: 更新BPM生產單須更新提醒
    """
    msq = XinTeaSql()
    cmd: str = """
        UPDATE order_manage_summary_b_to_b
        SET 
            order_issue_date = ?, 
            customer_contact = ?, customer_estimate_decide_date = ?, earliest_arrival_date = ?, 
            latest_arrival_date = ?, customer_name = ?, company_title = ?, 
            uniform_invoice_no = ?, address = ?, customer_window = ?, 
            customer_phone = ?, customer_email = ?, payment_term = ?, 
            payment = ?, ele_invoice = ?, delivery_method = ?, order_remark = ?, 
            xin_tea_connector = ?, xin_tea_connect_phone = ?, xin_tea_connect_email = ?, 
            customization_order = ?, product_and_customization_money = ?, 
            freight_per_piece_money = ?, freight_amount = ?, 
            discount = ?, freight_discount = ?, total_freight = ?, 
            product_and_customization_and_freight_money = ?, 
            payment_processing_fee = ?, payment_processing_fee_discount = ?, 
            total_payment_processing_fee = ?, final_total = ?, delivery_order = ?, 
            total_order_num = ?, order_type = ?, order_invoice_url = ?, is_direct_from_oem = ?
        WHERE sq_form_id = ?
    """
    upd_bpm_form_must_update_cmd: str = """UPDATE order_manage_summary_b_to_b SET bpm_form_must_update = ? WHERE sq_form_id = ?"""
    upd_bpm_generate_must_update_cmd: str = """UPDATE order_manage_summary_b_to_b SET bpm_generate_must_update = ? WHERE sq_form_id = ? AND bpm_generate_id <> ''"""
    cmds_param: list = [
        (
            cmd, upd_data
        ),
        (
            upd_bpm_form_must_update_cmd, upd_bpm_form_must_update
        ),
        (
            upd_bpm_generate_must_update_cmd, upd_bpm_generate_must_update
        )
    ]
    return msq.transaction_v2(cmds_param)


def qry_generate_vendor_by_select() -> list:
    """
    查詢生產廠商(下拉選單用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT ob.generate_vendor
                    FROM order_manage_summary_b_to_b AS ob
                    LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id"""
    return msq.s_qry(cmd)


def qry_item_by_select() -> list:
    """
    查詢料件(下拉選單用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT ob.item, ob.item_name
                    FROM order_manage_summary_b_to_b AS ob
                    LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id"""
    return msq.s_qry(cmd)


def qry_customer_name_by_select() -> list:
    """
    查詢客戶簡稱(下拉選單用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT ob.customer_name
                    FROM order_manage_summary_b_to_b AS ob
                    LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id"""
    return msq.s_qry(cmd)



def qry_bpm_form_id_by_select() -> list:
    """
    查詢BPM表單單號(下拉選單用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT ob.bpm_form_id
                    FROM order_manage_summary_b_to_b AS ob
                    LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id"""
    return msq.s_qry(cmd)


def qry_bpm_generate_id_by_select() -> list:
    """
    查詢BPM生產單單號(下拉選單用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT ob.bpm_generate_id
                    FROM order_manage_summary_b_to_b AS ob
                    LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id"""
    return msq.s_qry(cmd)


def qry_xin_tea_connector_by_select() -> list:
    """
    查詢心茶聯絡人(下拉選單用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT DISTINCT ob.xin_tea_connector
                    FROM order_manage_summary_b_to_b AS ob
                    LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                    LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id"""
    return msq.s_qry(cmd)


def qry_customer_data(customer_name: str) -> list:
    """
    查詢客戶主檔
    :param customer_name: 客戶簡稱
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM customer WHERE customer_name = ?"""
    return msq.s_qry(cmd, customer_name)


def qry_customer_data_order_head() -> list:
    """
    查詢客戶主檔(訂單表頭用)
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM customer"""
    return msq.s_qry(cmd)


def batch_modify(upd_data: list, upd_generate_must_update: list) -> bool:
    """
    批次修改(生產廠商/出庫倉別/最早到貨日/包裝說明檔案)、更新BPM生產單須更新提醒
    :param upd_data: 更新資料
    """
    msq = XinTeaSql()
    cmd: str = """UPDATE order_manage_summary_b_to_b
                  SET generate_vendor_by_generate = ?, shipping_out_warehouse_by_generate = ?, earliest_arrival_date_by_generate = ?,
                  latest_arrival_date_by_generate = ?, package_descript_file = ?
                  WHERE order_key = ?"""
    upd_generate_must_update_cmd: str = """UPDATE order_manage_summary_b_to_b
                                           SET bpm_generate_must_update = '1'
                                           WHERE order_key = ? and bpm_generate_id <> ''"""
    cmds_param: list = [
        (
            cmd, upd_data
        ),
        (
            upd_generate_must_update_cmd, upd_generate_must_update
        )
    ]
    return msq.transaction_v2(cmds_param)


def qry_order_manage_b_to_b_item_detail(gs_url: str, item: str) -> list:
    """
    查詢訂單管理總表B2B by 報價單網址及料件編號(訂單明細)
    :param gs_url: 報價單網址
    :param item: 料件編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT SUM(quantity) AS total_quantity 
                  FROM order_manage_summary_b_to_b WHERE sales_quotation_url = ? AND item = ? AND additional_order='0'
                  GROUP BY item"""
    return msq.s_qry(cmd, gs_url, item)


def qry_order_manage_summary_b_to_b_item_have_different(gs_url: str, item: str) -> list:
    """
    查詢訂單管理總表B2B by 報價單網址及料件編號是否有差異數>0
    :param gs_url: 報價單網址
    :param item: 料件編號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT *
                  FROM order_manage_summary_b_to_b WHERE sales_quotation_url = ? AND item = ? AND different > 0"""
    return msq.s_qry(cmd, gs_url, item)


def qry_bom_detail_use_quantity(bom_detail_id: str) -> list:
    """
    查詢BOM明細(使用數量)
    :param bom_detail_id: BOM明細ID
    """
    msq = XinTeaSql()
    cmd: str = """SELECT ob.quantity*ci.use_quantity+ci.adjustment_quantity as total_use, ob.quantity
                  FROM customize_bom as ci
                  INNER JOIN order_manage_summary_b_to_b as ob on ci.bom = ob.customize_bom
                  WHERE bom_detail_id = ?"""
    return msq.s_qry(cmd, bom_detail_id)


def qry_order_manage_b_to_b_summary() -> list:
    """
    查詢訂單管理總表B2B彙總資料
    """
    msq = XinTeaSql()
    cmd: str = """SELECT 
                    COUNT(DISTINCT sales_quotation_url) AS total_sq_form, 
                    COUNT(DISTINCT CASE WHEN bpm_form_id <> '' THEN bpm_form_id END) AS total_order, 
                    COUNT(DISTINCT CASE WHEN bpm_generate_id <> '' THEN bpm_generate_id END) AS total_generate 
                FROM order_manage_summary_b_to_b"""
    return msq.s_qry(cmd)