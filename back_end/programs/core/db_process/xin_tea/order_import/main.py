from programs.core.db_process.all_db_connect.main import XinTeaSql


def qry_order_import_record() -> list:
    """
    查詢訂單匯入紀錄
    """
    msq = XinTeaSql()
    cmd: str = """SELECT 
                  CONVERT(VARCHAR, upload_time, 120) AS upload_time,
                  action, platform, error_message 
                  FROM order_import_record
                  ORDER BY upload_time DESC"""
    return msq.s_qry(cmd)


def qry_customer_data_by_company_title(company_title: str) -> list:
    """
    查詢客戶資料
    :param company_title: 公司抬頭
    """
    msq = XinTeaSql()
    cmd: str = """select * FROM customer
                  WHERE customer_title = ?"""
    return msq.s_qry(cmd, company_title)


def qry_customer_data(uniform_invoice_no: str) -> list:
    """
    查詢客戶資料
    :param uniform_invoice_no: 客戶統編
    """
    msq = XinTeaSql()
    cmd: str = """select * FROM customer
                  WHERE customer_uniform_invoice_no = ?"""
    return msq.s_qry(cmd, uniform_invoice_no)


def crt_order_manage_summary_b_to_b_and_update_import_num(crt_data: list, import_num: list, crt_sq_num: list, customize_bom: list,
                                                          upd_quotation_detail: list, delete_order_param: list, delete_bom: list,
                                                          additional_product_bom: list, sales_quotataion_data: list,
                                                          upd_total_order_num: list) -> bool:
    """
    新增訂單管理總表B2B&更新報價單開立數量
    :param crt_data: 建立資料
    :param import_num: 報價單開立數量
    :param crt_sq_num: 今日報價單開立數量
    :param customize_bom: 客製化BOM
    :param upd_quotation_detail: 更新報價單明細
    :param delete_order_param: 刪除訂單明細參數
    :param delete_bom: 刪除BOM參數
    :param additional_product_bom: 新增外購品BOM參數
    :param sales_quotataion_data: 原始GS報價單資料
    :param upd_total_order_num: 更新訂單總數量
    """
    msq = XinTeaSql()
    cmd = """
    INSERT INTO order_manage_summary_b_to_b (
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
        customization_descript, unit_price, quantity, discount1,
        one_discount, order_money, standard_or_customization, bom,
        purchase_connect, product_descript_one, product_descript_two,
        detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
        bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
        customize_bom, order_seq, specific_remind, spare_item, additional_order,
        generate_vendor, shipping_out_warehouse, generate_vendor_by_generate, shipping_out_warehouse_by_generate,
        earliest_arrival_date_by_generate, different, item_batch, item_type, sales_quotation_type, is_direct_from_oem,
        sales_quotation_name, latest_arrival_date_by_generate
    ) VALUES (
        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    )
    """
    import_num_cmd: str = """UPDATE b_to_b_import SET import_num = ? WHERE import_date = ?"""
    crt_import_num_cmd: str = """INSERT INTO b_to_b_import (import_date, import_num) VALUES(?,?)"""
    customize_bom_cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, 
                                s_item, s_item_name, s_item_spec, unit, customize_item, use_quantity,
                                adjustment_quantity, bom, bom_detail_seq, customize_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    additional_product_bom_cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, 
                                s_item, s_item_name, s_item_spec, unit, customize_item, origin_use_quantity, use_quantity,
                                adjustment_quantity, bom, bom_detail_seq, customize_type, average) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    sales_quotataion_data_cmd: str = """INSERT INTO sales_quotation_gs(sales_quotation_url, item, quantity, item_batch) VALUES(?,?,?,?)"""
    upd_total_order_num_cmd: str = """UPDATE t
    SET t.total_order_num = x.total_order
    FROM order_manage_summary_b_to_b t
    JOIN (
        SELECT sales_quotation_url, SUM(quantity) AS total_order
        FROM order_manage_summary_b_to_b
        GROUP BY sales_quotation_url
    ) x ON t.sales_quotation_url = x.sales_quotation_url
    WHERE t.sales_quotation_url = ?"""
    cmds_param: list = []
    if crt_data:
        cmds_param.append((cmd, crt_data))
    if import_num:
        cmds_param.append((import_num_cmd, import_num))
    if crt_sq_num:
        cmds_param.append((crt_import_num_cmd, crt_sq_num))
    if customize_bom:
        cmds_param.append((customize_bom_cmd, customize_bom))
    if additional_product_bom:
        cmds_param.append((additional_product_bom_cmd, additional_product_bom))
    if sales_quotataion_data:
        cmds_param.append((sales_quotataion_data_cmd, sales_quotataion_data))
    cmds_param.append((upd_total_order_num_cmd, upd_total_order_num))
    return msq.transaction_v2(cmds_param)


def qry_bom_by_item(item_id: str) -> list:
    """
    查詢料件主檔BOM
    :param item_id: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM item_application_detail WHERE item = ?"""
    return msq.s_qry(cmd, item_id)


def qry_sq_num(now_date: str) -> list:
    """
    查詢今日報價單開立數量
    :param now_date: 今日日期
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM b_to_b_import WHERE import_date = ?"""
    return msq.s_qry(cmd, now_date)



def qry_item_data_in_item(item_data: list) -> list:
    """
    查詢料件主檔資料
    :param item_data: 料件清單
    """
    msq = XinTeaSql()
    format_strings = ','.join(['?'] * len(item_data))
    cmd: str = f"""SELECT * FROM item_application_detail WHERE item IN ({format_strings})"""
    return msq.s_qry(cmd, *item_data)

def qry_customize_item_replace_by_item(item: str) -> list:
    """
    查詢客製化料件替換
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """select cb.customize_item, iad.category as customize_category, iad.item_name as customize_item_name, 
                  iad.bom as customize_bom, cb.replace_item, iadd.category as replace_category, iadd.item_name as replace_item_name, 
                  iadd.bom as replace_bom
                  FROM customize_replace as cb
                  INNER JOIN item_application_detail as iad on cb.customize_item = iad.item
                  LEFT JOIN item_application_detail as iadd on cb.replace_item = iadd.item
                  WHERE cb.customize_item = ?"""
    return msq.s_qry(cmd, item)


def qry_bom_detail_by_item(item: str, bom: str) -> list:
    """
    查詢BOM明細
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT item, item_name, m_item, m_item_name, s_item, s_item_name,
                  s_item_spec, use_quantity
                  FROM item_bom
                  WHERE item = ? and origin_form_id = ? and item = m_item and m_item <> s_item
                  order by item, m_item, s_item"""
    return msq.s_qry(cmd, item, bom)


def qry_spare_item(item: str, customize: str) -> list:
    """
    查詢備用料件
    :param item: 料件
    :param customize: 客製/標準
    """
    print(item, customize)
    msq = XinTeaSql()
    cmd: str = """SELECT si.item, si.spare_item, iad.item_name as spare_item_name, iad.category as spare_item_category, iad.bom, si.customize_or_standard, si.full_num_additional_add
                  FROM spare_item as si
                  INNER JOIN item_application_detail as iad on si.spare_item = iad.item
                  WHERE si.item = ? and si.customize_or_standard = ?"""
    return msq.s_qry(cmd, item, customize)


def qry_order_item_exist(gs_url: str, item: str) -> list:
    """
    查詢訂單明細之料件是否存在
    :param gs_url: Google Sheet網址
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b 
                  WHERE sales_quotation_url = ? and item = ?"""
    return msq.s_qry(cmd, gs_url, item)


def qry_order_exist(gs_url: str) -> list:
    """
    查詢訂單是否存在
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b 
                  WHERE sales_quotation_url = ?
                  ORDER BY all_seq desc"""
    return msq.s_qry(cmd, gs_url)



def qry_order_no_spare_and_replace(gs_url: str) -> list:
    """
    查詢訂單明細(排除替代料件&備用料件)
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b 
                  WHERE sales_quotation_url = ? and additional_order = '0'
                  ORDER BY all_seq desc"""
    return msq.s_qry(cmd, gs_url)


def update_order_remind_specific(upd_data: list) -> bool:
    """
    更新明細提醒料件規格
    :param upd_data: 更新資料
    """
    msq = XinTeaSql()
    cmd: str = """UPDATE order_manage_summary_b_to_b 
                  SET specific_remind = ?
                  WHERE item = ? AND sales_quotation_url = ?"""
    cmds_param: list = []
    if upd_data:
        cmds_param.append((cmd, upd_data))
    return msq.transaction_v2(cmds_param)


def qry_customize_bom_by_replace(item: str, gs_url: str) -> list:
    """
    查詢客製化BOM(替代料件內容物)
    :param item: 料件
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """
               SELECT cb.s_item
               FROM customize_bom cb
               INNER JOIN order_manage_summary_b_to_b as ob on cb.bom = ob.customize_bom
               WHERE cb.customize_type = N'替換料件' and ob.sales_quotation_url = ? and cb.item = ?"""
    return msq.s_qry(cmd, gs_url, item)



def qry_customize_bom_by_item_gs_url(item: str, gs_url: str) -> list:
    """
    查詢客製化BOM
    :param item: 料件
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """
               SELECT cb.*
               FROM customize_bom cb
               INNER JOIN order_manage_summary_b_to_b as ob on cb.bom = ob.customize_bom
               WHERE ob.sq_form_id = ? and cb.item = ?
               ORDER BY cb.bom_detail_seq"""
    return msq.s_qry(cmd, gs_url, item)



def upd_order_manage_summary_b_to_b_and_update_import_num(crt_data: list, customize_bom: list, upd_quotation_detail: list,
                                                          delete_order_param: list, delete_bom: list, to_delete_bom: list,
                                                          upd_replace_item_origin_use_quantity_bom: list, to_crt_bom: list,
                                                          to_upd_bom: list, upd_spare_item_bom_num: list, 
                                                          upd_spare_item_order_detail_num: list,
                                                          delete_spare_item_bom: list, delete_spare_item_order_detail: list,
                                                          upd_replace_item_order_detail_num: list, crt_replace_item_order_detail_num: list) -> bool:
    """
    新增訂單管理總表B2B&更新報價單開立數量
    :param crt_data: 建立資料
    :param customize_bom: 客製化BOM
    :param upd_quotation_detail: 更新報價單明細
    :param delete_order_param: 刪除訂單明細參數
    :param delete_bom: 刪除BOM參數
    :param to_delete_bom: 刪除BOM(替換料件)
    :param upd_replace_item_origin_use_quantity_bom: 更新被替換料件的子件用量回原始用量
    :param to_crt_bom: 新增BOM
    :param to_upd_bom: 更新BOM
    :param upd_spare_item_bom_num: 更新備用料件BOM數量
    :param upd_spare_item_order_detail_num: 更新備用料件訂單明細數量
    :param delete_spare_item_bom: 刪除備用料件BOM
    :param delete_spare_item_order_detail: 刪除備用料件訂單
    :param upd_replace_item_order_detail_num: 更新替代料件訂單明細數量
    :param crt_replace_item_order_detail_num: 新增替代料件訂單明細
    """
    msq = XinTeaSql()
    cmd = """
    INSERT INTO order_manage_summary_b_to_b (
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
        customization_descript, unit_price, quantity, discount1,
        one_discount, order_money, standard_or_customization, bom,
        purchase_connect, product_descript_one, product_descript_two,
        detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
        bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
        customize_bom, order_seq, specific_remind, spare_item, additional_order
    ) VALUES (
        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    )
    """
    customize_bom_cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, 
                                s_item, s_item_name, s_item_spec, unit, customize_item, use_quantity,
                                adjustment_quantity, bom, bom_detail_seq, customize_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    upd_quotation_detail_cmd: str = """UPDATE order_manage_summary_b_to_b 
                                       SET quantity = ?, customer_estimate_decide_date = ?, earliest_arrival_date=?,
                                       latest_arrival_date=?, customer_name=?, company_title=?, uniform_invoice_no=?,
                                       address=?, customer_window=?, customer_phone=?, customer_email=?,
                                       payment_term=?, payment=?, standard_or_customization=?
                                       WHERE sales_quotation_url = ? AND item = ?"""
    delete_order_param_cmd: str = """DELETE FROM order_manage_summary_b_to_b 
                                     WHERE item = ? AND sales_quotation_url = ?"""
    delete_bom_cmd: str = """
                        DELETE FROM customize_bom
                        WHERE item IN (
                            SELECT cb.item
                            FROM customize_bom cb
                            JOIN order_manage_summary_b_to_b om
                            ON cb.item = om.item
                            WHERE om.sales_quotation_url = ? AND cb.item = ?
                        )
                        """
    to_delete_bom_cmd: str = """
                        DELETE cb
                        FROM customize_bom cb
                        INNER JOIN order_manage_summary_b_to_b om ON cb.bom = om.customize_bom
                        WHERE cb.item = ? and cb.s_item = ? AND om.sales_quotation_url = ? AND cb.customize_type = N'替換料件'
                        """
    upd_replace_item_origin_use_quantity_bom_cmd: str = """
                                                            UPDATE cb
                                                            SET cb.use_quantity = ib.use_quantity,
                                                                cb.customize_type = NULL, 
                                                                cb.customize_item = ''
                                                            FROM customize_bom cb
                                                            INNER JOIN order_manage_summary_b_to_b ob ON cb.bom = ob.customize_bom
                                                            INNER JOIN item_bom ib ON ib.origin_form_id = ob.bom AND cb.s_item = ib.s_item
                                                            WHERE cb.item = ? AND cb.m_item = ? AND cb.s_item = ? AND ob.sales_quotation_url = ? 
                                                            AND cb.customize_type = N'被替換料件'
                                                        """
    """
    to_crt_bom_cmd: str = INSERT INTO customize_bom (bom_detail_id, item, m_item, s_item, s_item_name, s_item_spec,
                                unit, customize_item, origin_use_quantity, use_quantity, adjustment_quantity, bom, bom_detail_seq,
                                customize_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    to_upd_bom_cmd: str = UPDATE customize_bom SET use_quantity = ?, customize_item = ?,
                             customize_type = ? WHERE s_item = ? AND bom = ?"""
    upd_spare_item_bom_num_cmd: str = """UPDATE cb
                                        SET adjustment_quantity = ?
                                        FROM customize_bom cb
                                        INNER JOIN order_manage_summary_b_to_b ob ON cb.bom = ob.customize_bom
                                        WHERE cb.item = ? 
                                        AND cb.m_item = ? 
                                        AND cb.s_item = ? 
                                        AND ob.sales_quotation_url = ? 
                                        AND cb.customize_type = N'備用料件'"""
    upd_spare_item_order_detail_num_cmd: str = """UPDATE ob
                                                    SET ob.quantity = ?
                                                    FROM order_manage_summary_b_to_b ob
                                                    WHERE ob.spare_item = ? and ob.item = ? and ob.sales_quotation_url = ?
                                                """
    delete_spare_item_bom_cmd: str = """DELETE cb
                                      FROM customize_bom cb
                                        INNER JOIN order_manage_summary_b_to_b ob ON cb.bom = ob.customize_bom
                                        WHERE cb.item = ? 
                                        AND cb.m_item = ? 
                                        AND cb.s_item = ? 
                                        AND ob.sales_quotation_url = ? 
                                        AND cb.customize_type = N'備用料件'
                                    """
    delete_spare_item_order_detail_cmd: str = """DELETE FROM order_manage_summary_b_to_b
                                                WHERE spare_item = ? and item = ? and sales_quotation_url = ? and additional_order = '1'"""
    upd_replace_item_order_detail_num_cmd: str = """UPDATE ob
                                                    SET ob.quantity = ?
                                                    FROM order_manage_summary_b_to_b ob
                                                    WHERE ob.item = ? and ob.sales_quotation_url = ? and ob.additional_order = '1'"""
    crt_replace_item_order_detail_num_cmd: str = """
    INSERT INTO order_manage_summary_b_to_b (
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
        customization_descript, unit_price, quantity, discount1,
        one_discount, order_money, standard_or_customization, bom,
        purchase_connect, product_descript_one, product_descript_two,
        detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
        bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
        customize_bom, order_seq, specific_remind, spare_item, additional_order
    ) VALUES (
        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    )
    """
    cmds_param: list = []
    if crt_data:
        cmds_param.append((cmd, crt_data))
    if customize_bom:
        cmds_param.append((customize_bom_cmd, customize_bom))
    if upd_quotation_detail:
        cmds_param.append((upd_quotation_detail_cmd, upd_quotation_detail))
    if delete_order_param:
        cmds_param.append((delete_order_param_cmd, delete_order_param))
    if delete_bom:
        cmds_param.append((delete_bom_cmd, delete_bom))
    if to_delete_bom:
        cmds_param.append((to_delete_bom_cmd, to_delete_bom))
    if upd_replace_item_origin_use_quantity_bom:
        cmds_param.append((upd_replace_item_origin_use_quantity_bom_cmd, upd_replace_item_origin_use_quantity_bom))
    if upd_spare_item_order_detail_num:
        cmds_param.append((upd_spare_item_order_detail_num_cmd, upd_spare_item_order_detail_num))
    if upd_spare_item_bom_num:
        cmds_param.append((upd_spare_item_bom_num_cmd, upd_spare_item_bom_num))
    if delete_spare_item_bom:
        cmds_param.append((delete_spare_item_bom_cmd, delete_spare_item_bom))
    if delete_spare_item_order_detail:
        cmds_param.append((delete_spare_item_order_detail_cmd, delete_spare_item_order_detail))
    if upd_replace_item_order_detail_num:
        cmds_param.append((upd_replace_item_order_detail_num_cmd, upd_replace_item_order_detail_num))
    if crt_replace_item_order_detail_num:
        cmds_param.append((crt_replace_item_order_detail_num_cmd, crt_replace_item_order_detail_num))
    return msq.transaction_v2(cmds_param)



def qry_order_manage_summary_b_to_b_is_manual_update(gs_url: str) -> list:
    """
    查詢訂單是否有手動更新過任一張客製BOM
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """select * 
                  FROM order_manage_summary_b_to_b as ob
                  INNER JOIN customize_bom as cb on ob.customize_bom = cb.bom
                  where cb.manual_update = '1' and ob.sales_quotation_url = ?"""
    return msq.s_qry(cmd, gs_url)



def crt_or_update_order_manage_summary_b_to_b_and_update_import_num(crt_data: list, customize_bom: list,
                                                                    delete_order_detail: list, delete_bom: list,
                                                                    copy_bom: list, origin_bom_to_new_bom: list,
                                                                    bom_and_gs_url: list, upd_bom_and_gs_url: list,
                                                                    origin_bom_delete: list,
                                                                    copy_order_detail: list, origin_order_detail_to_new_order_detail: list,
                                                                    origin_order_detail_delete: list, origin_generate_to_new_generate: list,
                                                                    order_and_gs_url: list, upd_order_and_gs_url: list,
                                                                    origin_add_manual_item_to_new_bom: list,
                                                                    origin_add_manual_item_order_detail_to_new_bom: list,
                                                                    origin_manual_customize_bom_to_new_bom: list,
                                                                    upd_spare_item_detail_latest_arrival_date: list,
                                                                    update_order_manage_summary_b_to_b_different: list,
                                                                    additional_product_bom: list, sales_quotataion_data: list) -> bool:
    """
    新增訂單管理總表B2B&更新報價單開立數量
    :param crt_data: 建立資料
    :param customize_bom: 客製化BOM
    :param upd_quotation_detail: 更新報價單明細
    :param delete_order_detail: 刪除訂單明細參數
    :param delete_bom: 刪除BOM參數
    :param copy_bom: 複製BOM
    :param origin_bom_to_new_bom: 將原BOM內容物更新至新BOM
    :param bom_and_gs_url: 客製化BOM與Google Sheet網址對應表
    :param upd_bom_and_gs_url: 更新客製化BOM與Google Sheet網址對應表
    :param origin_bom_delete: 刪除原BOM內容物
    :param copy_order_detail: 複製訂單明細
    :param origin_order_detail_to_new_order_detail: 將原訂單明細更新至新訂單明細(B2B)
    :param origin_order_detail_delete: 刪除原訂單明細
    :param origin_generate_to_new_generate: 將原禮盒生產單產生記錄更新至新禮盒生產單產生記錄
    :param order_and_gs_url: 訂單明細與Google Sheet網址對應表
    :param upd_order_and_gs_url: 更新訂單明細與Google Sheet網址對應表
    :param update_order_update_remind: 更新訂單明細提醒
    :param origin_add_manual_item_to_new_bom: 將手動新增客製BOM新增至新BOM
    :param origin_add_manual_item_order_detail_to_new_bom: 將手動新增客製BOM新增至新訂單明細
    :param origin_manual_customize_bom_to_new_bom: 將手動更新過的客製BOM新增至新BOM
    :param upd_spare_item_detail_latest_arrival_date: 更新備用料件訂單明細最新到貨日
    :param update_order_manage_summary_b_to_b_different: 更新訂單明細已分配量欄位
    :param additional_product_bom: 新增外購品BOM
    :param sales_quotataion_data: 原始GS報價單資料
    """
    msq = XinTeaSql()
    cmd = """
    INSERT INTO order_manage_summary_b_to_b (
        order_key, status, customer_purchase_type, order_issue_date,
        customer_contact, sales_quotation_url, order_invoice_url,
        customer_estimate_decide_date, earliest_arrival_date, 
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
        customization_descript, unit_price, quantity, discount1,
        one_discount, order_money, standard_or_customization, bom,
        purchase_connect, product_descript_one, product_descript_two,
        detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
        bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
        customize_bom, specific_remind, order_seq, spare_item, additional_order,
        item_batch, item_type, different, is_direct_from_oem, sales_quotation_type,
        sales_quotation_name, latest_arrival_date_by_generate
    ) VALUES (
        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    )
    """
    customize_bom_cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, 
                                s_item, s_item_name, s_item_spec, unit, customize_item, origin_use_quantity, use_quantity,
                                adjustment_quantity, bom, bom_detail_seq, customize_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    delete_order_detail_cmd: str = """DELETE FROM order_manage_summary_b_to_b 
                                     WHERE sales_quotation_url = ?"""
    delete_bom_cmd: str = """
                        DELETE cb
                        FROM customize_bom cb
                        INNER JOIN order_manage_summary_b_to_b ob ON cb.bom = ob.customize_bom
                        WHERE ob.sales_quotation_url = ?"""
    copy_bom_cmd: str = """INSERT INTO customize_bom_batch (
                            bom_detail_id, item, m_item, s_item, s_item_name, 
                            s_item_spec, unit, customize_item, origin_use_quantity, 
                            use_quantity, adjustment_quantity, bom, bom_detail_seq, 
                            customize_type, manual_update
                        )
                        SELECT 
                            cb.bom_detail_id, cb.item, cb.m_item, cb.s_item, cb.s_item_name,
                            cb.s_item_spec, cb.unit, cb.customize_item, cb.origin_use_quantity,
                            cb.use_quantity, cb.adjustment_quantity, cb.bom, cb.bom_detail_seq,
                            cb.customize_type, cb.manual_update
                        FROM customize_bom cb
                        INNER JOIN order_manage_summary_b_to_b ob ON cb.bom = ob.customize_bom
                        WHERE ob.sales_quotation_url = ?"""
    origin_bom_to_new_bom_cmd: str = """UPDATE cb
                                        SET cb.adjustment_quantity = cbb.adjustment_quantity, 
                                            cb.use_quantity = cbb.use_quantity, 
                                            cb.customize_item = cbb.customize_item
                                        FROM customize_bom cb
                                        INNER JOIN customize_bom_batch cbb 
                                            ON cb.item = cbb.item 
                                            AND cb.m_item = cbb.m_item 
                                            AND cb.s_item = cbb.s_item 
                                            AND ISNULL(cb.customize_type, '') = ISNULL(cbb.customize_type, '')
                                        INNER JOIN order_manage_summary_b_to_b ob 
                                            ON cb.bom = ob.customize_bom
                                        WHERE ob.sales_quotation_url = ?
                                            AND ISNULL(cb.customize_type, '') != '備用料件'
                                            AND ISNULL(cbb.customize_type, '') != '備用料件'"""
    bom_and_gs_url_cmd: str = """INSERT INTO customize_bom_and_gs_url (customize_bom, gs_url) VALUES(?,?)"""
    upd_bom_and_gs_url_cmd: str = """UPDATE customize_bom_and_gs_url SET gs_url = ? WHERE customize_bom = ?"""
    origin_bom_delete_cmd: str = """DELETE FROM customize_bom_batch
                                    WHERE bom IN (
                                        SELECT customize_bom 
                                        FROM customize_bom_and_gs_url 
                                        WHERE gs_url = ?
                                    )"""
    copy_order_detail_cmd: str = """INSERT INTO order_manage_summary_b_to_b_batch (
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
                                    customization_descript, unit_price, quantity, discount1,
                                    one_discount, order_money, standard_or_customization, bom,
                                    purchase_connect, product_descript_one, product_descript_two,
                                    detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
                                    bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
                                    customize_bom, order_seq, specific_remind, spare_item, additional_order,
                                    bpm_form_must_update, bpm_generate_must_update, add_manually_item, shipping_out_warehouse, generate_vendor,
                                    shipping_out_warehouse_by_generate, generate_vendor_by_generate, earliest_arrival_date_by_generate,
                                    different, item_batch, diff_item, diff_item_bom, sales_quotation_name, sales_quotation_type, latest_arrival_date_by_generate,
                                    package_descript_file, bpm_form_level, bpm_generate_level
                                    )
                                    SELECT 
                                        ob.order_key, ob.status, ob.customer_purchase_type, ob.order_issue_date,
                                        ob.customer_contact, ob.sales_quotation_url, ob.order_invoice_url,
                                        ob.customer_estimate_decide_date, ob.earliest_arrival_date, 
                                        ob.latest_arrival_date, ob.customer_name, ob.company_title, ob.uniform_invoice_no, ob.address,
                                        ob.customer_window, ob.customer_phone, ob.customer_email, ob.payment_term,
                                        ob.payment, ob.ele_invoice, ob.delivery_method, ob.order_remark,
                                        ob.xin_tea_connector, ob.xin_tea_connect_phone, ob.xin_tea_connect_email, ob.customization_order, 
                                        ob.product_and_customization_money, ob.check_money, ob.freight_per_piece_money, ob.freight_amount, ob.discount, ob.freight_discount,
                                        ob.total_freight, ob.product_and_customization_and_freight_money,
                                        ob.payment_processing_fee, ob.payment_processing_fee_discount,
                                        ob.total_payment_processing_fee, ob.final_total, ob.total_order_num,
                                        ob.delivery_order, ob.order_type, ob.item, ob.category, ob.item_name, ob.item_specific,
                                        ob.customization_descript, ob.unit_price, ob.quantity, ob.discount1,
                                        ob.one_discount, ob.order_money, ob.standard_or_customization, ob.bom,
                                        ob.purchase_connect, ob.product_descript_one, ob.product_descript_two,
                                        ob.detail_remark, ob.xin_tea_remark, ob.bpm_form_id, ob.bpm_form_status,
                                        ob.bpm_generate_id, ob.bpm_generate_status, ob.sq_form_id, ob.import_name,
                                        ob.customize_bom, ob.order_seq, ob.specific_remind, ob.spare_item, ob.additional_order,
                                        ob.bpm_form_must_update, ob.bpm_generate_must_update, ob.add_manually_item, ob.shipping_out_warehouse, ob.generate_vendor,
                                        ob.shipping_out_warehouse_by_generate, ob.generate_vendor_by_generate, ob.earliest_arrival_date_by_generate,
                                        ob.different, ob.item_batch, ob.diff_item, ob.diff_item_bom, ob.sales_quotation_name, ob.sales_quotation_type,
                                        ob.latest_arrival_date_by_generate, ob.package_descript_file, ob.bpm_form_level, ob.bpm_generate_level
                                    FROM order_manage_summary_b_to_b ob
                                    WHERE ob.sales_quotation_url = ?"""
    origin_generate_to_new_generate_cmd: str = """UPDATE ob
                                                          SET ob.bpm_generate_id = ob2.bpm_generate_id,
                                                              ob.bpm_generate_status = ob2.bpm_generate_status,
                                                              ob.specific_remind = ob2.specific_remind,
                                                              ob.generate_vendor = ob2.generate_vendor,
                                                              ob.shipping_out_warehouse = ob2.shipping_out_warehouse,
                                                              ob.latest_arrival_date = ob2.latest_arrival_date,
                                                              ob.earliest_arrival_date_by_generate = ob2.earliest_arrival_date_by_generate,
                                                              ob.generate_vendor_by_generate = ob2.generate_vendor_by_generate,
                                                              ob.shipping_out_warehouse_by_generate = ob2.shipping_out_warehouse_by_generate,
                                                              ob.latest_arrival_date_by_generate = ob2.latest_arrival_date_by_generate,
                                                              ob.package_descript_file = ob2.package_descript_file,
                                                              ob.bpm_form_level = ob2.bpm_form_level,
                                                              ob.bpm_generate_level = ob2.bpm_generate_level
                                                          FROM order_manage_summary_b_to_b ob
                                                          INNER JOIN order_manage_summary_b_to_b_batch ob2 on ob.sales_quotation_url = ob2.sales_quotation_url and ob.item = ob2.item and ob.item_batch = ob2.item_batch
                                                          WHERE ob2.sales_quotation_url = ?""" # INNER JOIN order_detail_and_gs_url odg on odg.gs_url = ob.sales_quotation_url and odg.item = ob.item
    origin_order_detail_delete_cmd: str = """DELETE FROM order_manage_summary_b_to_b_batch
                                            WHERE sales_quotation_url = ?"""
    # 有可變動欄位要恢復原狀調整底下的 SQL
    origin_order_detail_to_new_order_detail_cmd: str = """UPDATE ob
                                                      SET ob.bpm_form_id = odg.bpm_form_id,
                                                          ob.bpm_form_status = odg.bpm_form_status,
                                                          ob.bpm_form_must_update = CASE 
                                                              WHEN odg.bpm_form_id IS NOT NULL AND odg.bpm_form_id <> '' THEN '1'
                                                              ELSE '0'
                                                          END,
                                                          ob.bpm_generate_must_update = CASE 
                                                              WHEN odg.bpm_generate_id IS NOT NULL AND odg.bpm_generate_id <> '' THEN '1'
                                                              ELSE '0'
                                                          END,
                                                          ob.customize_bom = odg.customize_bom,
                                                          ob.generate_vendor = odg.generate_vendor,
                                                          ob.shipping_out_warehouse = odg.shipping_out_warehouse,
                                                          ob.generate_vendor_by_generate = odg.generate_vendor_by_generate,
                                                          ob.shipping_out_warehouse_by_generate = odg.shipping_out_warehouse_by_generate,
                                                          ob.earliest_arrival_date_by_generate = odg.earliest_arrival_date_by_generate,
                                                          ob.latest_arrival_date_by_generate = odg.latest_arrival_date_by_generate,
                                                          ob.package_descript_file = odg.package_descript_file,
                                                          ob.bpm_form_level = odg.bpm_form_level,
                                                          ob.bpm_generate_level = odg.bpm_generate_level
                                                      FROM order_manage_summary_b_to_b ob
                                                      INNER JOIN order_manage_summary_b_to_b_batch odg on odg.sales_quotation_url = ob.sales_quotation_url
                                                      WHERE odg.sales_quotation_url = ? AND odg.item = ob.item AND ob.item_batch = odg.item_batch"""
    order_and_gs_url_cmd: str = """INSERT INTO order_detail_and_gs_url (gs_url, item) VALUES(?,?)"""
    upd_order_and_gs_url_cmd: str = """UPDATE order_detail_and_gs_url SET gs_url = ? WHERE item = ?"""
    """origin_add_manual_item_to_new_bom_cmd: str = INSERT INTO customize_bom (
            bom_detail_id, item, m_item, s_item, s_item_name, s_item_spec, 
            unit, customize_item, origin_use_quantity, use_quantity, 
            adjustment_quantity, bom, bom_detail_seq, customize_type,
            manual_update
        )
        SELECT 
            cb.bom_detail_id, cb.item, cb.m_item, cb.s_item, 
            cb.s_item_name, cb.s_item_spec, 
            cb.unit, cb.customize_item, cb.origin_use_quantity, cb.use_quantity, 
            cb.adjustment_quantity, cb.bom, cb.bom_detail_seq, cb.customize_type,
            cb.manual_update
        FROM customize_bom_batch AS cb
        INNER JOIN order_manage_summary_b_to_b_batch AS ob 
            ON cb.bom = ob.customize_bom
        WHERE (cb.customize_type = N'手動增加' or cb.customize_type = N'外購品')
            AND ob.sales_quotation_url = ?"""
    origin_add_manual_item_order_detail_to_new_bom_cmd: str = """
        INSERT INTO order_manage_summary_b_to_b (
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
            customization_descript, unit_price, quantity, discount1,
            one_discount, order_money, standard_or_customization, bom,
            purchase_connect, product_descript_one, product_descript_two,
            detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
            bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
            customize_bom, order_seq, specific_remind, spare_item, additional_order,
            bpm_form_must_update, bpm_generate_must_update, add_manually_item,
            generate_vendor, shipping_out_warehouse, generate_vendor_by_generate,
            shipping_out_warehouse_by_generate, earliest_arrival_date_by_generate,
            item_batch, sales_quotation_name, sales_quotation_type, latest_arrival_date_by_generate,
            package_descript_file
        )
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
            customization_descript, unit_price, quantity, discount1,
            one_discount, order_money, standard_or_customization, bom,
            purchase_connect, product_descript_one, product_descript_two,
            detail_remark, xin_tea_remark, bpm_form_id, bpm_form_status,
            bpm_generate_id, bpm_generate_status, sq_form_id, import_name,
            customize_bom, order_seq, specific_remind, spare_item, additional_order,
            bpm_form_must_update, bpm_generate_must_update, add_manually_item,
            generate_vendor, shipping_out_warehouse, generate_vendor_by_generate,
            shipping_out_warehouse_by_generate, earliest_arrival_date_by_generate,
            item_batch, sales_quotation_name, sales_quotation_type, latest_arrival_date_by_generate,
            package_descript_file
        FROM order_manage_summary_b_to_b_batch
        WHERE sales_quotation_url = ? 
            AND add_manually_item IS NOT NULL
            AND order_key NOT IN (
                SELECT order_key 
                FROM order_manage_summary_b_to_b 
                WHERE sales_quotation_url = ?
            )
    """
    """origin_manual_customize_bom_to_new_bom_cmd: str = INSERT INTO customize_bom (
            bom_detail_id, item, m_item, s_item, s_item_name, s_item_spec, 
            unit, customize_item, origin_use_quantity, use_quantity, 
            adjustment_quantity, bom, bom_detail_seq, customize_type,
            manual_update
        )
        SELECT 
        cb.bom_detail_id, cb.item, cb.m_item, cb.s_item, 
        cb.s_item_name, cb.s_item_spec, 
        cb.unit, cb.customize_item, cb.origin_use_quantity, cb.use_quantity, 
        cb.adjustment_quantity, cb.bom, cb.bom_detail_seq, cb.customize_type,
        cb.manual_update
        FROM customize_bom_batch AS cb
        INNER JOIN order_manage_summary_b_to_b_batch AS ob 
            ON cb.bom = ob.customize_bom
        WHERE ob.sales_quotation_url = ? 
            AND ISNULL(cb.customize_type, '') <> N'手動增加'"""
    # AND ob.standard_or_customization = ''
    upd_spare_item_detail_latest_arrival_date_cmd: str = """
        UPDATE ob
        SET ob.latest_arrival_date = first_order.latest_arrival_date,
            ob.generate_vendor_by_generate = first_order.generate_vendor_by_generate,
            ob.shipping_out_warehouse_by_generate = first_order.shipping_out_warehouse_by_generate,
            ob.earliest_arrival_date_by_generate = first_order.earliest_arrival_date_by_generate,
            ob.latest_arrival_date_by_generate = first_order.latest_arrival_date_by_generate,
            ob.package_descript_file = first_order.package_descript_file
        FROM order_manage_summary_b_to_b ob
        CROSS APPLY (
            -- 抓有正常完整資料的
            SELECT TOP 1 latest_arrival_date, generate_vendor_by_generate,
                     shipping_out_warehouse_by_generate, earliest_arrival_date_by_generate,
                     latest_arrival_date_by_generate, package_descript_file
            FROM order_manage_summary_b_to_b
            WHERE sales_quotation_url = ob.sales_quotation_url
            AND additional_order = '0' AND latest_arrival_date IS NOT NULL  -- 只抓正常訂單明細，不抓備用料件
            ORDER BY all_seq ASC  -- 取第一筆
        ) AS first_order
        WHERE ob.additional_order = '1' 
        AND ob.sales_quotation_url = ? OR ob.latest_arrival_date IS NULL
    """
    # 更新原有BOM
    update_origin_bom_cmd: str = """UPDATE order_manage_summary_b_to_b SET customize_bom=order_key WHERE category IN ('A', 'B') AND bom <> ''"""
    # 更新原有已分配量
    update_order_manage_summary_b_to_b_different_cmd: str = """
        UPDATE ob
         SET ob.different = ob.quantity
         FROM order_manage_summary_b_to_b ob
         WHERE ob.sales_quotation_url = ?"""
    # 新增外購品BOM數量
    additional_product_bom_cmd: str = """INSERT INTO customize_bom (bom_detail_id, item, m_item, 
                                s_item, s_item_name, s_item_spec, unit, customize_item, origin_use_quantity, use_quantity,
                                adjustment_quantity, bom, bom_detail_seq, customize_type, average) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    # 原始報價單GS資料
    sales_quotataion_data_cmd: str = """INSERT INTO sales_quotation_gs (sales_quotation_url, item, quantity, item_batch) VALUES (?,?,?,?)"""
    # 刪除原有GS報價單資料
    delete_sales_quotation_data_cmd: str = """DELETE FROM sales_quotation_gs WHERE sales_quotation_url = ?"""
    # 更新總訂單數量
    upd_total_order_num_cmd: str = """UPDATE t
    SET t.total_order_num = x.total_order,
        t.bpm_form_must_update = CASE 
            WHEN t.bpm_form_id IS NOT NULL AND t.bpm_form_id <> '' THEN '1'
            ELSE '0'
        END,
        t.bpm_generate_must_update = CASE 
            WHEN t.bpm_generate_id IS NOT NULL AND t.bpm_generate_id <> '' THEN '1'
            ELSE '0'
        END
    FROM order_manage_summary_b_to_b t
    JOIN (
        SELECT sales_quotation_url, SUM(quantity) AS total_order
        FROM order_manage_summary_b_to_b
        GROUP BY sales_quotation_url
    ) x ON t.sales_quotation_url = x.sales_quotation_url
    WHERE t.sales_quotation_url = ?"""
    # 更新報價單標準禮盒異常處理
    update_order_detail_specific_remind_error_cmd: str = """
        UPDATE order_manage_summary_b_to_b
        SET specific_remind = '0'
        WHERE standard_or_customization = '標準禮盒' and sales_quotation_url = ?"""
    # 更新報價單客製化禮盒異常處理
    update_order_detail_specific_customzie_error_cmd: str = """
    UPDATE order_manage_summary_b_to_b
            SET specific_remind = '1'
            WHERE standard_or_customization = '客製化禮盒' and sales_quotation_url = ?
    """
    # 更新原有的手動增加和外購品的客製化料件
    update_customize_bom_manual_and_additional_cmd: str = """UPDATE cb
                                        SET  
                                            cb.customize_item = cbb.customize_item
                                        FROM customize_bom cb
                                        INNER JOIN customize_bom_batch cbb 
                                            ON cb.item = cbb.item 
                                            AND cb.m_item = cbb.m_item 
                                            AND cb.s_item = cbb.s_item 
                                            AND ISNULL(cb.customize_type, '') = ISNULL(cbb.customize_type, '')
                                        INNER JOIN order_manage_summary_b_to_b ob 
                                            ON cb.bom = ob.customize_bom
                                        WHERE ob.sales_quotation_url = ?
                                            AND cb.customize_type IN (N'外購品', N'手動增加')
                                            AND cbb.customize_type IN (N'外購品', N'手動增加')"""
    cmds_param: list = [
        (copy_bom_cmd, copy_bom),
        (copy_order_detail_cmd, copy_order_detail),
        (delete_bom_cmd, delete_bom),
        (delete_order_detail_cmd, delete_order_detail)
    ]
    
    if crt_data:
        cmds_param.append((cmd, crt_data))
    if customize_bom:
        cmds_param.append((customize_bom_cmd, customize_bom))
    
    if bom_and_gs_url:
        cmds_param.append((bom_and_gs_url_cmd, bom_and_gs_url))
    if upd_bom_and_gs_url:
        cmds_param.append((upd_bom_and_gs_url_cmd, upd_bom_and_gs_url))
    
    if order_and_gs_url:
        cmds_param.append((order_and_gs_url_cmd, order_and_gs_url))
    if upd_order_and_gs_url:
        cmds_param.append((upd_order_and_gs_url_cmd, upd_order_and_gs_url))
    #if origin_add_manual_item_to_new_bom:
    #    cmds_param.append((origin_add_manual_item_to_new_bom_cmd, origin_add_manual_item_to_new_bom))
    
    #if origin_manual_customize_bom_to_new_bom:
    #    cmds_param.append((origin_manual_customize_bom_to_new_bom_cmd, origin_manual_customize_bom_to_new_bom))
    
    if origin_add_manual_item_order_detail_to_new_bom:
        cmds_param.append((origin_add_manual_item_order_detail_to_new_bom_cmd, origin_add_manual_item_order_detail_to_new_bom))
    
    if origin_bom_to_new_bom:
        cmds_param.append((origin_bom_to_new_bom_cmd, origin_bom_to_new_bom))
    
    if origin_order_detail_to_new_order_detail:
        cmds_param.append((origin_order_detail_to_new_order_detail_cmd, origin_order_detail_to_new_order_detail))
    if origin_generate_to_new_generate:
        cmds_param.append((origin_generate_to_new_generate_cmd, origin_generate_to_new_generate))
    cmds_param.append((update_origin_bom_cmd, [()]))
    cmds_param.append((upd_spare_item_detail_latest_arrival_date_cmd, upd_spare_item_detail_latest_arrival_date))
    if origin_order_detail_delete:
        cmds_param.append((origin_order_detail_delete_cmd, origin_order_detail_delete))
    cmds_param.append((update_order_manage_summary_b_to_b_different_cmd, update_order_manage_summary_b_to_b_different))
    cmds_param.append((delete_sales_quotation_data_cmd, update_order_manage_summary_b_to_b_different))
    cmds_param.append((sales_quotataion_data_cmd, sales_quotataion_data))
    if additional_product_bom:
        cmds_param.append((additional_product_bom_cmd, additional_product_bom))
    cmds_param.append((upd_total_order_num_cmd, update_order_manage_summary_b_to_b_different))
    cmds_param.append((update_order_detail_specific_remind_error_cmd, update_order_manage_summary_b_to_b_different))
    # 保留原有外購品和手動新增的客製化料件欄為
    cmds_param.append((update_customize_bom_manual_and_additional_cmd, update_order_manage_summary_b_to_b_different))
    # 刪除copy出來的BOM
    if origin_bom_delete:
        cmds_param.append((origin_bom_delete_cmd, origin_bom_delete))
    #cmds_param.append((update_order_detail_specific_customzie_error_cmd, update_order_manage_summary_b_to_b_different))
    
    return msq.transaction_v2(cmds_param)


def qry_order_replace_item_exist(gs_url: str, item: str) -> list:
    """
    查詢訂單明細之替代料件是否存在
    :param gs_url: Google Sheet網址
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b 
                  WHERE sales_quotation_url = ? and item = ? and additional_order = '1'"""
    return msq.s_qry(cmd, gs_url, item)


def qry_customize_bom_and_gs_url_exist(customize_bom: str, gs_url: str) -> list:
    """
    查詢客製化BOM與Google Sheet網址對應表是否存在
    :param customize_bom: 客製化BOM
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM customize_bom_and_gs_url 
                  WHERE customize_bom = ? and gs_url = ?"""
    return msq.s_qry(cmd, customize_bom, gs_url)


def qry_order_detail_and_gs_url_exist(gs_url: str, item: str) -> list:
    """
    查詢訂單明細與Google Sheet網址對應表是否存在
    :param gs_url: Google Sheet網址
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_detail_and_gs_url 
                  WHERE gs_url = ? and item = ?"""
    return msq.s_qry(cmd, gs_url, item)


def qry_generate_vendor() -> list:
    """
    查詢生產廠商
    """
    msq = XinTeaSql()
    cmd: str = """SELECT vendor, 
                  CONVERT(VARCHAR, start_date, 23) AS start_date, 
                  order_money, 
                  pri_seq
                  FROM vendor_condition
                  ORDER BY 
                    CASE WHEN pri_seq = 0 THEN 1 ELSE 0 END,  
                    pri_seq ASC"""
    return msq.s_qry(cmd)



def qry_item_vendor_reference(item: str, vendor: str) -> list:
    """
    查詢料件參照表
    :param item: 料件
    :param vendor: 廠商
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM item_reference
                  WHERE item_id = ? AND vendor_name = ?
                  AND relationship='1'"""
    return msq.s_qry(cmd, item, vendor)


def qry_shipping_warehouse_by_generate_vendor(vendor: str) -> list:
    """
    查詢出庫倉別
    :param vendor: 廠商
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM vendor 
                  WHERE vendor_name = ?"""
    return msq.s_qry(cmd, vendor)


def qry_b_to_b_check_rule() -> list:
    """
    查詢B2B訂單匯入規則
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM b_to_b_check_rule"""
    return msq.s_qry(cmd)


def qry_order_manage_summary_b_to_b_first_item_bom_by_sales_quotation(gs_url: str) -> list:
    """
    查詢訂單管理總表B2B資料(禮盒的BOM)
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """WITH FirstOrder AS (
                        SELECT TOP 1 customize_bom 
                        FROM order_manage_summary_b_to_b 
                        WHERE sales_quotation_url = ?
                        ORDER BY order_seq
                    )
                    SELECT cb.* 
                    FROM customize_bom cb
                    INNER JOIN FirstOrder fo ON cb.bom = fo.customize_bom
                    ORDER BY cb.bom_detail_seq"""
    return msq.s_qry(cmd, gs_url)


def qry_origin_sales_quotation_gs(gs_url: str) -> list:
    """
    查詢原始報價單GS資料
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM sales_quotation_gs WHERE sales_quotation_url = ?"""
    return msq.s_qry(cmd, gs_url)


def qry_customize_item_and_replace_item_in_bom(customize_item: str, item: str) -> list:
    """
    查詢客製料件替換的被替代料件是否存在於該料號裡的BOM
    :param customize_item: 客製料件
    :param item: 料件
    """
    msq = XinTeaSql()
    cmd: str = """SELECT iad.*, ib.*, cr.*
                FROM item_application_detail as iad
                INNER JOIN item_bom as ib 
                    on iad.item = ib.item 
                    and iad.bom = ib.origin_form_id
                LEFT JOIN customize_replace as cr 
                    on ib.s_item = cr.replace_item
                    AND cr.replace_item IS NOT NULL
                    AND cr.replace_item <> ''
                WHERE iad.item = ?
                    AND EXISTS (
                        SELECT 1 
                        FROM customize_replace 
                        WHERE customize_item = ?
                        AND (
                            (replace_item = ib.s_item AND replace_item IS NOT NULL AND replace_item <> '')
                            OR (replace_item IS NULL OR replace_item = '')
                        )
                    )"""
    return msq.s_qry(cmd, item, customize_item)


def crt_order_import_record_b_to_b(add_data: list) -> bool:
    """
    新增訂單匯入紀錄(B2B)
    :param add_data: 新增資料
    """
    msq = XinTeaSql()
    cmd: str = """INSERT INTO order_import_record(action, platform, error_message) VALUES(?,?,?)"""
    cmds_param: list = [
        (cmd, add_data)
    ]
    return msq.transaction_v2(cmds_param)


def qry_add_manually_item(gs_url: str, item: str, item_batch: str) -> list:
    """
    查詢手動增加BOM料件
    :param gs_url: Google Sheet網址
    :param item: 料件
    :param item_batch: 料號
    """
    msq = XinTeaSql()
    cmd: str = """
    SELECT 
        ob.sales_quotation_url,
        ob.item,
        ob.item_batch,
        cb.s_item,
        iad.item_name as s_item_name,
        cb.use_quantity,
        cb.adjustment_quantity
    FROM customize_bom cb
    INNER JOIN order_manage_summary_b_to_b ob ON cb.bom = ob.customize_bom
    INNER JOIN item_application_detail as iad on iad.item = cb.s_item
    WHERE cb.customize_type = N'手動增加' AND ob.sales_quotation_url = ? AND ob.item=? AND ob.item_batch=?"""
    return msq.s_qry(cmd, gs_url, item, item_batch)


def qry_sales_quotation_is_alrady_have_bpm_form_bpm_generate(gs_url: str) -> list:
    """
    查詢報價單是否已有訂單或是生產單
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * 
                  FROM order_manage_summary_b_to_b as ob
                  LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                  LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id
                  where sales_quotation_url=?
                  """
    return msq.s_qry(cmd, gs_url)


def delete_sales_quotation_data(gs_url: str) -> bool:
    """
    刪除報價單資料
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    delete_sales_quotation_gs_cmd: str = """DELETE FROM sales_quotation_gs WHERE sales_quotation_url = ?"""
    delete_customize_bom_cmd: str = """DELETE FROM customize_bom
                                WHERE bom IN (
                                    SELECT DISTINCT ob.customize_bom
                                    FROM order_manage_summary_b_to_b ob
                                    WHERE ob.sales_quotation_url = ?
                                    AND ob.customize_bom IS NOT NULL
                                    AND ob.customize_bom <> ''
                                )"""
    delete_customize_bom_gs_cmd: str = """DELETE FROM customize_bom_and_gs_url WHERE gs_url = ?"""
    delete_sales_quotation_cmd: str = """DELETE FROM order_manage_summary_b_to_b WHERE sales_quotation_url = ?"""
    cmds_param: list = [
        (
            delete_customize_bom_cmd,
            [(gs_url,)]
        ),
        (
            delete_sales_quotation_gs_cmd,
            [(gs_url,)]
        ),
        (
            delete_customize_bom_gs_cmd,
            [(gs_url,)]
        ),
        (
            delete_sales_quotation_cmd,
            [(gs_url,)]
        )   
    ]
    return msq.transaction_v2(cmds_param)


def qry_order_manage_summary_b_to_b_different(gs_url: str) -> list:
    """
    查詢訂單管理總表B2B資料差異量
    :param gs_url: Google Sheet網址
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM order_manage_summary_b_to_b WHERE sales_quotation_url = ? and item_batch <> ''"""
    return msq.s_qry(cmd, gs_url)


def qry_item_batch_has_active_bpm_form(gs_url: str, item_id: str, item_batch: str) -> bool:
    """
    查詢特定料號+批次組合是否有進行中或簽核通過的表單
    :param gs_url: Google Sheet網址
    :param item_id: 料號
    :param item_batch: 批次
    :return: True表示有進行中的表單, False表示沒有
    """
    msq = XinTeaSql()
    cmd: str = """SELECT ob.* 
                  FROM order_manage_summary_b_to_b as ob
                  LEFT JOIN b2b_form_status AS bs ON bs.bpm_form_id = ob.bpm_form_id
                  LEFT JOIN gift_box_form_status AS gb ON gb.bpm_form_id = ob.bpm_generate_id
                  WHERE ob.sales_quotation_url = ?
                  AND ob.item = ?
                  AND ob.item_batch = ?
                  """
    return msq.s_qry(cmd, gs_url, item_id, item_batch)


def qry_item_spare_data_exist(item_id: str) -> list:
    """
    檢查料號是否有對應的備用提袋資料
    :param item_id: 料號
    """
    msq = XinTeaSql()
    cmd: str = """SELECT * FROM spare_item WHERE item = ?"""
    return msq.s_qry(cmd, item_id)