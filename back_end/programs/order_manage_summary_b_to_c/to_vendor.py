from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea
from datetime import datetime

class ToVendor:
    """拋轉廠商"""
    
    def __init__(self, to_vendor_order: list):
        self.to_vendor_order: list = to_vendor_order
        
    
    def process(self) -> str:
        """
        處理拋轉廠商動作
        """
        # 1. 檢查資料是否符合拋轉廠商條件
        result: str = self.__check_data()
        if result != 'OK':
            return result
        # 2. 處理拋轉廠商
        result: str = self.__to_vendor()
        return result
    
    def __check_data(self) -> str:
        """
        檢查拋轉廠商資料
        """
        for per_vendor in self.to_vendor_order:
            # 檢查檢查訊息是否為空值(代表無錯誤)
            if len(per_vendor.get('check_message')) != 0:
                return '明細檢查異常，請修正問題再重新拋轉廠商'
            # 檢查狀態是否為可拋轉廠商狀態
            status: str = per_vendor.get('status')
            can_to_vendor: list = xin_tea.qry_status_can_to_vendor(status)
            if not can_to_vendor:
                return f"明細狀態【{status}】，不符合拋轉廠商狀態"
            # 狀態3→3.1 需要該訂單所有明細都為狀態3且有勾選拋轉
            if status == '3':
                e_commerce_platform_order_no: str = per_vendor.get('e_commerce_platform_order_no')
                order_data: list = xin_tea.qry_order_data_by_cancel(e_commerce_platform_order_no)
                count: int = 0
                # 抓當前勾選同訂單號碼有幾筆
                for per_detail in self.to_vendor_order:
                    if e_commerce_platform_order_no == per_detail.get('e_commerce_platform_order_no'):
                        count += 1
                # 該訂單單號實際有幾筆跟要拋轉的訂單號碼明細總計要一致才允許拋轉
                if count != len(order_data):
                    return f"平台訂單單號【{e_commerce_platform_order_no}】沒有整批選取取消，無法拋轉廠商"
            # 狀態2→2.1 需要該訂單所有明細都有勾選處理且狀態2才能拋轉廠商
            if status == '2':
                e_commerce_platform_order_no: str = per_vendor.get('e_commerce_platform_order_no')
                order_data: list = xin_tea.qry_order_data_by_to_vendor(e_commerce_platform_order_no)
                # 允許2 2.0 3.1 4.1該單可以拋轉
                for per_order in order_data:
                    if per_order.get('status') not in ['2', '2.0', '3.1', '4.1']:
                        return f"平台訂單單號【{e_commerce_platform_order_no}】需要該訂單全部明細整批勾選才可拋轉廠商!"         
            """
            # 狀態4→4.1 需要該訂單所有明細都為狀態4才能拋轉廠商
            if status == '4':
                e_commerce_platform_order_no: str = per_vendor.get('e_commerce_platform_order_no')
                order_data: list = xin_tea.qry_order_data_by_delete(e_commerce_platform_order_no)
                for per_order in order_data:
                    if per_order.get('status') != '4':
                        return f"平台訂單單號{e_commerce_platform_order_no}】沒有全部明細狀態皆為4，無法拋轉廠商"
            """
        return 'OK'
    
    def __to_vendor(self) -> bool:
        """
        處理拋轉廠商
        """
        # 廠商參數
        upd_delete_vendor_param: list = [] # 狀態5發生廠商已確認又重拋狀態，需將原有訂單刪除
        crt_to_vendor_param: list = []
        # 訂單管理總表參數
        upd_to_vendor_param: list = []
        upd_status_param: list = []
        # 用料明細參數
        crt_use_item_param: list = []
        upd_use_item_delete_param: list = []
        upd_use_item_cancel_param: list = []
        # BOM展算規則
        can_spread_rule: list = xin_tea.qry_bom_spread_rule_can_spread()
        no_spread_rule: list = xin_tea.qry_bom_spread_rule_no_spread()
        
        can_spread: list = [per_can.get('item_category') for per_can in can_spread_rule]
        no_spread: list = [per_no.get('item_category') for per_no in no_spread_rule]
        for per_vendor in self.to_vendor_order:
            # 更新拋給廠商後呈現的狀態、訂單管理總表狀態
            status: str = per_vendor.get('status')
            vendor_status: list = xin_tea.qry_status(status)
            if status != '5':
                try:
                    vendor_look_status: str = vendor_status[0]['vendor_look_status']
                except IndexError:
                    vendor_look_status: str = ''
            try:
                order_manage_status: str = vendor_status[0]['to_vendor_status']
            except IndexError:
                order_manage_status: str = ''
            order_data: list = xin_tea.qry_vendor_order(per_vendor.get('order_key'))
            if status == '5':
                # 重新查詢該筆在廠商的狀態，避免狀態不一致
                qry_vendor_order_data: list = xin_tea.qry_vendor_order(per_vendor.get('order_key'))
                per_vendor['vendor_check'] = qry_vendor_order_data[0]['vendor_check']
            # 5以外的拋轉
            if status != '5':
                if not order_data:
                    crt_to_vendor_param.append(
                        (
                            per_vendor.get('status'), vendor_look_status,
                            per_vendor.get('check_message'), per_vendor.get('white_list_process'),
                            per_vendor.get('is_check_remark_message'), per_vendor.get('to_order_generate_date'),
                            per_vendor.get('earliest_arrival_date'), per_vendor.get('generate_vendor'),
                            per_vendor.get('shipping_out_warehouse'), per_vendor.get('xin_tea_remark'),
                            per_vendor.get('already_order_order_status', ''), per_vendor.get('b2c_order_is_can_sign', ''),
                            per_vendor.get('b2c_order_status', ''), per_vendor.get('b2c_bpm_form_id', ''), 
                            per_vendor.get('estimate_num_and_check', ''), per_vendor.get('eip_import_label', ''), 
                            per_vendor.get('package_factory_import_label', ''), per_vendor.get('split_berfore_order_no', ''), 
                            per_vendor.get('common_order_no_different_vendor', ''), 
                            per_vendor.get('common_order_no_different_shipping_date', ''), 
                            per_vendor.get('latest_arrival_date', ''), per_vendor.get('e_commerce_platform_order_no', ''), 
                            per_vendor.get('e_commerce_platform', ''), per_vendor.get('e_commerce_platform_order_date', ''), 
                            per_vendor.get('new_order_order_status', ''), per_vendor.get('new_order_payment_status', ''), 
                            per_vendor.get('logistics_method', ''), per_vendor.get('order_remark_or_shipping_remark', ''), 
                            per_vendor.get('item', ''), per_vendor.get('product_name', ''), 
                            per_vendor.get('item_category', ''), per_vendor.get('bom_bpm_form_id', ''), 
                            per_vendor.get('platform_product_name', ''), per_vendor.get('platform_specific', ''), 
                            per_vendor.get('quantity', ''), per_vendor.get('recipient', ''), 
                            per_vendor.get('recipient_phone', ''), per_vendor.get('recipient_address', ''), 
                            per_vendor.get('recipient_email', ''), per_vendor.get('payment_term', ''), 
                            per_vendor.get('order_money', ''), per_vendor.get('invoice_title', ''), 
                            per_vendor.get('uniform_invoice_no', ''), per_vendor.get('sender', ''), 
                            per_vendor.get('sender_phone', ''), per_vendor.get('order_key', ''), 
                            per_vendor.get('arrival_area', ''), per_vendor.get('importer', ''), 
                            per_vendor.get('import_date', ''), per_vendor.get('google_sheet_url', ''), 
                            per_vendor.get('google_sheet_name', ''), '0'
                        )
                    )
                else:
                    upd_to_vendor_param.append(
                        (   
                            per_vendor.get('order_key', ''),
                            per_vendor.get('status'), vendor_look_status,
                            per_vendor.get('check_message'), per_vendor.get('white_list_process'),
                            per_vendor.get('is_check_remark_message'), per_vendor.get('to_order_generate_date'),
                            per_vendor.get('earliest_arrival_date'), per_vendor.get('generate_vendor'),
                            per_vendor.get('shipping_out_warehouse'), per_vendor.get('xin_tea_remark'),
                            per_vendor.get('already_order_order_status', ''), per_vendor.get('b2c_order_is_can_sign', ''),
                            per_vendor.get('b2c_order_status', ''), per_vendor.get('b2c_bpm_form_id', ''), 
                            per_vendor.get('estimate_num_and_check', ''), per_vendor.get('eip_import_label', ''), 
                            per_vendor.get('package_factory_import_label', ''), per_vendor.get('split_berfore_order_no', ''), 
                            per_vendor.get('common_order_no_different_vendor', ''), 
                            per_vendor.get('common_order_no_different_shipping_date', ''), 
                            per_vendor.get('latest_arrival_date', ''), per_vendor.get('e_commerce_platform_order_no', ''), 
                            per_vendor.get('e_commerce_platform', ''), per_vendor.get('e_commerce_platform_order_date', ''), 
                            per_vendor.get('new_order_order_status', ''), per_vendor.get('new_order_payment_status', ''), 
                            per_vendor.get('logistics_method', ''), per_vendor.get('order_remark_or_shipping_remark', ''), 
                            per_vendor.get('item', ''), per_vendor.get('product_name', ''), 
                            per_vendor.get('item_category', ''), per_vendor.get('bom_bpm_form_id', ''), 
                            per_vendor.get('platform_product_name', ''), per_vendor.get('platform_specific', ''), 
                            per_vendor.get('quantity', ''), per_vendor.get('recipient', ''), 
                            per_vendor.get('recipient_phone', ''), per_vendor.get('recipient_address', ''), 
                            per_vendor.get('recipient_email', ''), per_vendor.get('payment_term', ''), 
                            per_vendor.get('order_money', ''), per_vendor.get('invoice_title', ''), 
                            per_vendor.get('uniform_invoice_no', ''), per_vendor.get('sender', ''), 
                            per_vendor.get('sender_phone', ''),  
                            per_vendor.get('arrival_area', ''), per_vendor.get('importer', ''), 
                            per_vendor.get('import_date', ''), per_vendor.get('google_sheet_url', ''), 
                            per_vendor.get('google_sheet_name', '')
                        )
                    )
            
            # 5.無拋轉廠商資料or已拋轉但是廠商已確認則要新增
            if status == '5':
                if not order_data or (len(order_data) > 0 and per_vendor.get('vendor_check') == '1'):
                        vendor_look_status: str = '訂單異動待確認'
                        upd_delete_vendor_param.append(
                            (
                                per_vendor.get('order_key'), '刪除', '0', 
                            )
                        )
                        crt_to_vendor_param.append(
                            (
                                per_vendor.get('status'), vendor_look_status,
                                per_vendor.get('check_message'), per_vendor.get('white_list_process'),
                                per_vendor.get('is_check_remark_message'), per_vendor.get('to_order_generate_date'),
                                per_vendor.get('earliest_arrival_date'), per_vendor.get('generate_vendor'),
                                per_vendor.get('shipping_out_warehouse'), per_vendor.get('xin_tea_remark'),
                                per_vendor.get('already_order_order_status', ''), per_vendor.get('b2c_order_is_can_sign', ''),
                                per_vendor.get('b2c_order_status', ''), per_vendor.get('b2c_bpm_form_id', ''), 
                                per_vendor.get('estimate_num_and_check', ''), per_vendor.get('eip_import_label', ''), 
                                per_vendor.get('package_factory_import_label', ''), per_vendor.get('split_berfore_order_no', ''), 
                                per_vendor.get('common_order_no_different_vendor', ''), 
                                per_vendor.get('common_order_no_different_shipping_date', ''), 
                                per_vendor.get('latest_arrival_date', ''), per_vendor.get('e_commerce_platform_order_no', ''), 
                                per_vendor.get('e_commerce_platform', ''), per_vendor.get('e_commerce_platform_order_date', ''), 
                                per_vendor.get('new_order_order_status', ''), per_vendor.get('new_order_payment_status', ''), 
                                per_vendor.get('logistics_method', ''), per_vendor.get('order_remark_or_shipping_remark', ''), 
                                per_vendor.get('item', ''), per_vendor.get('product_name', ''), 
                                per_vendor.get('item_category', ''), per_vendor.get('bom_bpm_form_id', ''), 
                                per_vendor.get('platform_product_name', ''), per_vendor.get('platform_specific', ''), 
                                per_vendor.get('quantity', ''), per_vendor.get('recipient', ''), 
                                per_vendor.get('recipient_phone', ''), per_vendor.get('recipient_address', ''), 
                                per_vendor.get('recipient_email', ''), per_vendor.get('payment_term', ''), 
                                per_vendor.get('order_money', ''), per_vendor.get('invoice_title', ''), 
                                per_vendor.get('uniform_invoice_no', ''), per_vendor.get('sender', ''), 
                                per_vendor.get('sender_phone', ''), per_vendor.get('order_key', ''), 
                                per_vendor.get('arrival_area', ''), per_vendor.get('importer', ''), 
                                per_vendor.get('import_date', ''), per_vendor.get('google_sheet_url', ''), 
                                per_vendor.get('google_sheet_name', ''), '0'
                            )
                        )
                # 有拋轉廠商但是廠商未確認則要更新
                if len(order_data) > 0 and per_vendor.get('vendor_check') == '0':
                        vendor_look_status: str = '訂單異動待確認'
                        upd_to_vendor_param.append(
                            (   
                                per_vendor.get('order_key', ''),
                                per_vendor.get('status'), vendor_look_status,
                                per_vendor.get('check_message'), per_vendor.get('white_list_process'),
                                per_vendor.get('is_check_remark_message'), per_vendor.get('to_order_generate_date'),
                                per_vendor.get('earliest_arrival_date'), per_vendor.get('generate_vendor'),
                                per_vendor.get('shipping_out_warehouse'), per_vendor.get('xin_tea_remark'),
                                per_vendor.get('already_order_order_status', ''), per_vendor.get('b2c_order_is_can_sign', ''),
                                per_vendor.get('b2c_order_status', ''), per_vendor.get('b2c_bpm_form_id', ''), 
                                per_vendor.get('estimate_num_and_check', ''), per_vendor.get('eip_import_label', ''), 
                                per_vendor.get('package_factory_import_label', ''), per_vendor.get('split_berfore_order_no', ''), 
                                per_vendor.get('common_order_no_different_vendor', ''), 
                                per_vendor.get('common_order_no_different_shipping_date', ''), 
                                per_vendor.get('latest_arrival_date', ''), per_vendor.get('e_commerce_platform_order_no', ''), 
                                per_vendor.get('e_commerce_platform', ''), per_vendor.get('e_commerce_platform_order_date', ''), 
                                per_vendor.get('new_order_order_status', ''), per_vendor.get('new_order_payment_status', ''), 
                                per_vendor.get('logistics_method', ''), per_vendor.get('order_remark_or_shipping_remark', ''), 
                                per_vendor.get('item', ''), per_vendor.get('product_name', ''), 
                                per_vendor.get('item_category', ''), per_vendor.get('bom_bpm_form_id', ''), 
                                per_vendor.get('platform_product_name', ''), per_vendor.get('platform_specific', ''), 
                                per_vendor.get('quantity', ''), per_vendor.get('recipient', ''), 
                                per_vendor.get('recipient_phone', ''), per_vendor.get('recipient_address', ''), 
                                per_vendor.get('recipient_email', ''), per_vendor.get('payment_term', ''), 
                                per_vendor.get('order_money', ''), per_vendor.get('invoice_title', ''), 
                                per_vendor.get('uniform_invoice_no', ''), per_vendor.get('sender', ''), 
                                per_vendor.get('sender_phone', ''),  
                                per_vendor.get('arrival_area', ''), per_vendor.get('importer', ''), 
                                per_vendor.get('import_date', ''), per_vendor.get('google_sheet_url', ''), 
                                per_vendor.get('google_sheet_name', ''), '0', per_vendor.get('order_key', '')
                            )
                        )
            upd_status_param.append(
                (
                    order_manage_status, per_vendor.get('order_key')
                )
            )
            # 用料明細處理 2 新增 3 4(狀態 0) 5 更新
            # 狀態2 和 5 需要新增用料明細
            if status in ['2', '5']:
                # 有BOM表，查詢該筆品項之BOM表
                bom: str = ''
                try:
                    print(len(per_vendor.get('bom_bpm_form_id')))
                    bom = per_vendor.get('bom_bpm_form_id')
                except:
                    pass
                # BOM 改抓現行料件主檔(避免預購期間BOM表有異動)
                item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
                if item_data:
                    bom = item_data[0].get('bom')
                # 有BOM表且品項類別為A,B，則查詢該品項之BOM表
                if len(bom) > 0 and per_vendor.get('item_category') in can_spread:
                    bom_data: list = xin_tea.qry_bom_by_item(per_vendor.get('item'), bom)
                    order_m_item: str = per_vendor.get('item')
                    quantity: float = per_vendor.get('quantity')
                    
                    for per_bom in bom_data:
                        m_item: str = per_bom.get('m_item')
                        # 只算一階料
                        if order_m_item == m_item:
                            s_item: str = per_bom.get('s_item')
                            # 計算用量(該子件用量*訂單數量)
                            s_item_use_quantity: float = float(per_bom.get('use_quantity')) * float(quantity)
                            unit: str = ''
                            item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
                            try:
                                unit = item_data[0]['unit']
                            except:
                                pass
                            crt_use_item_param.append(
                                (
                                    per_vendor.get('e_commerce_platform_order_no'), per_vendor.get('order_key'), per_vendor.get('earliest_arrival_date'), per_vendor.get('latest_arrival_date'),
                                    '', per_vendor.get('item'), per_vendor.get('product_name'), quantity, '標準', '', per_vendor.get('order_remark_or_shipping_remark'),
                                    order_m_item, per_vendor.get('product_name'), s_item, per_bom.get('s_item_name'), per_bom.get('use_quantity'), s_item_use_quantity,
                                    '', '', '官網B2C訂單', per_vendor.get('item_category'), per_vendor.get('generate_vendor'), '0', '' , '', '', '', per_vendor.get('shipping_out_warehouse'),
                                    per_vendor.get('bom_bpm_form_id'), '0', unit
                                )
                            )
                # 無BOM or 料件類別為X,Y,3,DX，直接新增
                if len(bom) == 0 or per_vendor.get('item_category') in no_spread:
                    unit: str = ''
                    item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
                    try:
                        unit = item_data[0]['unit']
                    except:
                        pass
                    crt_use_item_param.append(
                        (
                            per_vendor.get('e_commerce_platform_order_no'), per_vendor.get('order_key'), per_vendor.get('earliest_arrival_date'), per_vendor.get('latest_arrival_date'),
                            '', per_vendor.get('item'), per_vendor.get('product_name'), per_vendor.get('quantity'), '標準', '', per_vendor.get('order_remark_or_shipping_remark'),
                            per_vendor.get('item'), per_vendor.get('product_name'), per_vendor.get('item'), per_vendor.get('product_name'), '1', per_vendor.get('quantity'),
                            '', '', '官網B2C訂單', per_vendor.get('item_category'), per_vendor.get('generate_vendor'), 
                            '0', '' , '', '', '', per_vendor.get('shipping_out_warehouse'),
                            per_vendor.get('bom_bpm_form_id'), '0', unit
                        )
                    )
                if status == '5':
                    # 刪除原有展算資料
                    upd_use_item_delete_param.append(
                    (
                        per_vendor.get('order_key'),
                    )
                )
            elif status in ['3', '4']:
                upd_use_item_cancel_param.append(
                    (
                        '-1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  per_vendor.get('order_key')
                    )
                )
        result: bool = xin_tea.crt_vendor_order_b_to_c_upd_order_manage_status(crt_to_vendor_param, upd_to_vendor_param, upd_status_param, upd_delete_vendor_param,
                                                                               crt_use_item_param, upd_use_item_cancel_param, upd_use_item_delete_param)
        if result:
            return '拋轉廠商成功'
        return '拋轉廠商失敗'