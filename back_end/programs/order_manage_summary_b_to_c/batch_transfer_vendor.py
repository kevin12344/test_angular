from datetime import datetime
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea

class BatchTransferVendor:
    def __init__(self, b_to_c: list):
        self.b_to_c: list = b_to_c
        
        
    def process(self) -> bool:
        """
        一鍵轉廠商
        """
        """
        檢查
        """
        # 1. 檢查資料
        check_message: str 
        error_order: list
        check_message, error_order = self.__check_data_rule()
        print('error_order', error_order)
        # 2. 檢查資料是否符合修改訂單管理總表條件
        check_modify_error_message: str
        error_upd_order: list
        error_data_check: list 
        check_modify_error_message, error_upd_order, error_data_check = self.__check_data(error_order)
        print('error_upd_order', error_upd_order)
        """
        修改
        """
        # 2. 修改訂單管理總表
        result: bool = self.__modify_order_manage_summary(error_order, error_upd_order)
        if not result:
            return False
        """
        拋轉廠商
        """
        # 1. 檢查資料是否符合拋轉廠商條件
        error_to_vendor_message: str
        error_to_vendor_order: list
        error_data: list
        error_to_vendor_message, error_to_vendor_order, error_data = self.__check_to_vendor_data(error_order, error_upd_order)
        print('error_to_vendor_order', error_to_vendor_order)
        print('error_data_check', error_data_check)
        print('error_data', error_data)
        final_error_data = error_data_check + error_data
        # 2. 處理拋轉廠商
        result: str = self.__to_vendor(error_order, error_upd_order, error_to_vendor_order, final_error_data)
        final_message: str = check_message + check_modify_error_message + error_to_vendor_message
        if len(final_message) > 0:
            return f"{final_message}其餘訂單皆執行成功"
        return '一鍵轉廠商成功'
        
            

    def __check_data_rule(self) -> str | list:
        """檢查訂單管理總表資料"""
        error_order: list = []
        error_m_order: list = []
        message: str = ''
        for per_b_to_c in self.b_to_c:
            # 該筆已拋給廠商則不檢查
            vendor_data: list = xin_tea.qry_vendor_order(per_b_to_c.get('order_key'))
            if vendor_data:
                continue
            # 檢查拋單生產日
            if per_b_to_c.get('status') == '2':
                check_message: str = self.__check_to_generate_date(per_b_to_c.get('order_key'), per_b_to_c.get('to_order_generate_date'))
                if len(check_message) > 0:
                    error_order.append(per_b_to_c.get('order_key'))
                    error_m_order.append(per_b_to_c.get('split_berfore_order_no'))
                    message += check_message
            """
            check_param.append(
                (
                    message, per_b_to_c.get('order_key')
                )
            )
            """
        # 找出該error_order裡的order_key的同母單明細也是一律視為錯誤
        if len(error_m_order) > 0:
            for per_error in error_m_order:
                order_data: list = xin_tea.qry_order_manage_summary_b_to_c_by_split_before_order(per_error)
                for per_order in order_data:
                    if per_order.get('order_key') not in error_order:
                        error_order.append(per_order.get('order_key'))
        return message, error_order
                
    @staticmethod
    def __check_to_generate_date(e_commerce_platform_order_no: str, to_generate_date: str) -> str:
        """
        檢查拋單生產日是否大於今天
        :param e_commerce_platform_order_no: 電商平台訂單號碼
        :param to_generate_date: 拋單生產日
        """
        if not to_generate_date:
            return ''
        
        # 將輸入的日期字串轉換為 datetime 物件
        to_generate_date_obj = datetime.strptime(to_generate_date, '%Y/%m/%d')
        
        # 取得今天的 datetime 物件，並去除時間部分
        today_obj = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    
        if to_generate_date_obj > today_obj:
            return ''
        if to_generate_date_obj < today_obj:
            return f"{e_commerce_platform_order_no}過去日期不可拋轉"+'<br>'
        if to_generate_date_obj == today_obj:
            return ''
        return f"{e_commerce_platform_order_no}未知錯誤"+'<br>'
    
    
    def __check_data(self, error_order: list) -> str | list:
        """
        檢查修改訂單管理總表資料
        :param error_order: 錯誤訂單
        """
        error_upd_order: list = []
        error_message: str = ''
        error_data: list = []
        for per_detail in self.b_to_c:
            if per_detail.get('order_key') in error_order:
                continue
            e_commerce_platform: str = per_detail.get('e_commerce_platform')
            # 修改成狀態2(必須滿足 新訂單_訂單狀態:已確認/備註欄位:已確認或空白/預計抛單日有值/拋單生產日不得小於現在日期)
            if per_detail.get('status') == '2':
                if (per_detail.get('is_check_remark_message') not in ['', '已確認']) or (per_detail.get('to_order_generate_date') == ''):
                    error_upd_order.append(per_detail.get('order_key'))
                    error_message += f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件<br>"
                    error_data.append(
                        (
                            f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件\n", per_detail.get('order_key')
                        )
                    )
                # 新訂單_訂單狀態 依電商平台決定是否可改成狀態2
                new_order_status: str = per_detail.get('new_order_order_status')
                if e_commerce_platform == 'line 禮物':
                    if new_order_status not in ['已付款']:
                        error_upd_order.append(per_detail.get('order_key'))
                        error_message += f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件<br>"
                        error_data.append(
                        (
                            f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件\n", per_detail.get('order_key')
                        )
                    )
                elif e_commerce_platform == 'shopline':
                    if new_order_status not in ['已確認']:
                        error_upd_order.append(per_detail.get('order_key'))
                        error_message += f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件<br>"
                        error_data.append(
                            (
                                f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件\n", per_detail.get('order_key')
                            )
                        )
                elif e_commerce_platform == 'pinkoi':
                    if new_order_status not in ['待出貨', '尚未付款']:
                        error_upd_order.append(per_detail.get('order_key'))
                        error_message += f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件<br>"
                        error_data.append(
                            (
                                f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件\n", per_detail.get('order_key')
                            )
                        )
                # 拋單生產日不得小於現在日期
                if per_detail.get('to_order_generate_date') < datetime.now().strftime('%Y/%m/%d'):
                    #error_upd_order.append(per_detail.get('order_key'))
                    error_message += f"心茶訂單【{per_detail.get('order_key')}】製作許可日不得小於現在日期<br>"
                    error_data.append(
                        (
                            f"心茶訂單【{per_detail.get('order_key')}】製作許可日不得小於現在日期\n", per_detail.get('order_key')
                        )
                    )
        return error_message, error_upd_order, error_data
    
    def __modify_order_manage_summary(self, error_order: list,  error_upd_order: list) -> bool:
        """
        修改訂單管理總表
        :param error_order: 錯誤檢查訂單
        :param error_upd_order: 錯誤訂單
        """
        update_param: list = []
        update_special: list = []
        now_date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for per_upd in self.b_to_c:
            order_key: str = per_upd.get('order_key')
            if order_key in error_order:
                continue
            if order_key in error_upd_order:
                continue
            update_param.append(
                (
                    per_upd.get('white_list_process'), per_upd.get('is_check_remark_message'),
                    per_upd.get('to_order_generate_date'), per_upd.get('earliest_arrival_date'),
                    per_upd.get('generate_vendor'), per_upd.get('shipping_out_warehouse'),
                    per_upd.get('status'), per_upd.get('xin_tea_remark'), now_date,
                    per_upd.get('quantity'), per_upd.get('latest_arrival_date'), per_upd.get('delivery_vendor'),
                    per_upd.get('order_key')
                )
            )
            
        result: bool = xin_tea.modify_order_manage_summary_b_to_c(update_param)
        return result
    
    
    
    def __check_to_vendor_data(self, error_order: list, error_upd_order: list) -> str | list:
        """
        檢查拋轉廠商資料
        :param error_order: 錯誤訂單
        :param error_upd_order: 錯誤修改訂單
        """
        error_message: str = ''
        error_to_vendor_order: list = []
        error_data: list = []
        # 重新查詢該訂單明細避免資料不一致
        order_key_qry: list = []
        for per_vendor in self.b_to_c:
            order_key: str = per_vendor.get('order_key')
            order_key_qry.append(order_key)
        new_b_to_c: list = xin_tea.qry_order_manage_summary_repeat(order_key_qry)
        
        # 替換成重新查詢過後的資料
        self.b_to_c = new_b_to_c
        for per_vendor in self.b_to_c:
            order_key: str = per_vendor.get('order_key')
            if order_key in error_upd_order:
                continue
            if order_key in error_order:
                continue
            # 檢查檢查訊息是否為空值(代表無錯誤)
            """
            if len(per_vendor.get('check_message')) != 0:
                error_to_vendor_order.append(order_key)
                error_message += f"{order_key}明細檢查異常，請修正問題再重新拋轉廠商\n"
                error_data.append(
                    (
                        f"{order_key}明細檢查異常，請修正問題再重新拋轉廠商\n", order_key
                    )
                )
                continue
            """
            # 檢查狀態是否為可拋轉廠商狀態
            status: str = per_vendor.get('status')
            can_to_vendor: list = xin_tea.qry_status_can_to_vendor(status)
            if not can_to_vendor:
                error_to_vendor_order.append(order_key)
                error_message += f"{order_key}明細狀態【{status}】不符合拋轉廠商狀態<br>"
                error_data.append(
                    (
                        f"{order_key}明細狀態【{status}】不符合拋轉廠商狀態\n", order_key
                    )
                )
                continue
            # 狀態3→3.1 需要該訂單所有明細都為狀態3且有勾選拋轉
            if status == '3':
                split_before_order_no = per_vendor.get('split_berfore_order_no')
                e_commerce_platform_order_no: str = per_vendor.get('e_commerce_platform_order_no')
                order_data: list = xin_tea.qry_order_data_by_cancel(split_before_order_no)
                print(len(order_data))
                count: int = 0
                # 抓當前勾選同訂單號碼有幾筆
                for per_detail in self.b_to_c:
                    if split_before_order_no == per_detail.get('split_berfore_order_no'):
                        count += 1
                print('count', count)
                # 該訂單單號實際有幾筆跟要拋轉的訂單號碼明細總計要一致才允許拋轉
                if count != len(order_data):
                    error_to_vendor_order.append(order_key)
                    error_message+= f"心茶訂單【{order_key}】該平台訂單單號【{e_commerce_platform_order_no}】沒有整批選取取消，無法拋轉廠商<br>"
                    error_data.append(
                    (
                        f"心茶訂單【{order_key}】該平台訂單單號【{e_commerce_platform_order_no}】沒有整批選取取消，無法拋轉廠商\n", order_key
                    )
                )
            """
            # 狀態4→4.1 需要該訂單所有明細都為狀態3才能拋轉廠商
            if status == '4':
                e_commerce_platform_order_no: str = per_vendor.get('e_commerce_platform_order_no')
                order_data: list = xin_tea.qry_order_data_by_delete(e_commerce_platform_order_no)
                for per_order in order_data:
                    if per_order.get('status') != '4':
                        error_to_vendor_order.append(order_key)
                        error_message += f"平台訂單單號{e_commerce_platform_order_no}】需要該訂單全部明細整批勾選才可拋轉廠商!"
                        continue
            """
            # 狀態2→2.1 需要該訂單所有明細都有勾選處理且狀態都為2才能拋轉廠商
            if status == '2':
                e_commerce_platform_order_no: str = per_vendor.get('e_commerce_platform_order_no')
                split_before_order_no: str = per_vendor.get('split_berfore_order_no')
                order_data: list = xin_tea.qry_order_data_by_to_vendor(split_before_order_no)
                # 允許2 該單可以拋轉
                total_count: int = 0
                for per_sub_vendor in self.b_to_c:
                    order_key: str = per_vendor.get('order_key')
                    if order_key in error_upd_order:
                        continue
                    if order_key in error_order:
                        continue
                    if per_sub_vendor.get('split_berfore_order_no') == split_before_order_no:
                        total_count += 1
                if len(order_data) != total_count:
                    error_to_vendor_order.append(order_key)
                    error_message+= f"心茶訂單【{order_key}】該平台訂單單號【{split_before_order_no}】需要該訂單全部明細整批勾選才可拋轉廠商!<br>"
                    error_data.append(
                        (
                            f"心茶訂單【{order_key}】該平台訂單單號【{split_before_order_no}】需要該訂單全部明細整批勾選才可拋轉廠商!\n", order_key
                        )
                    )
            # 同母單(拆單前單號)，必須生產廠商和最早到貨日都是一樣的才可以拋轉廠商(未拋轉)
            if status in ['2', '5']:
                split_berfore_order_no: str = per_vendor.get('split_berfore_order_no')
                split_berfore_order_no_data: list = xin_tea.qry_order_by_split_berfore_order_no(split_berfore_order_no)
                if len(split_berfore_order_no_data) > 0:
                    # 為每個母單重新初始化變數
                    current_vendor: list = []
                    current_earliest_arrival_date: list = []
                    current_white_list: list = []
                    has_error: bool = False
                    
                    # 收集目前母單的所有資料
                    for per_split in split_berfore_order_no_data:
                        # 確認廠商、最早到貨日的數量
                        if per_split.get('generate_vendor') not in current_vendor:
                            current_vendor.append(per_split.get('generate_vendor'))
                        if per_split.get('earliest_arrival_date') not in current_earliest_arrival_date:
                            current_earliest_arrival_date.append(per_split.get('earliest_arrival_date'))
                        
                        # 檢查是否為例外白名單
                        if per_split.get('white_list_process') == '例外白名單':
                            current_white_list.append(per_split.get('order_key'))
                    
                    # 檢查廠商一致性
                    if len(current_vendor) > 1:
                        # 有多個廠商，檢查是否有例外白名單
                        if per_vendor.get('white_list_process') != '例外白名單':
                            error_to_vendor_order.append(order_key)
                            error_message += f"心茶訂單【{order_key}】同母單生產廠商不一致，無法拋轉廠商<br>"
                            error_data.append(
                                (
                                    f"心茶訂單【{order_key}】同母單生產廠商不一致，無法拋轉廠商\n", order_key
                                )
                            )
                            has_error = True
                        else:
                            # 即使是例外白名單，如果同母單有多個廠商也不能拋轉
                            error_to_vendor_order.append(order_key)
                            error_message += f"心茶訂單【{order_key}】同母單生產廠商不一致，無法拋轉廠商<br>"
                            error_data.append(
                                (
                                    f"心茶訂單【{order_key}】同母單生產廠商不一致，無法拋轉廠商\n", order_key
                                )
                            )
                            has_error = True
                    
                    # 檢查最早到貨日一致性
                    if len(current_earliest_arrival_date) > 1 and not has_error:
                        if per_vendor.get('white_list_process') != '例外白名單':
                            error_to_vendor_order.append(order_key)
                            error_message += f"心茶訂單【{order_key}】同母單最早到貨日不一致，無法拋轉廠商<br>"
                            error_data.append(
                                (
                                    f"心茶訂單【{order_key}】同母單最早到貨日不一致，無法拋轉廠商\n", order_key
                                )
                            )
                        else:
                            # 即使是例外白名單，如果同母單有多個到貨日也不能拋轉
                            error_to_vendor_order.append(order_key)
                            error_message += f"心茶訂單【{order_key}】同母單最早到貨日不一致，無法拋轉廠商<br>"
                            error_data.append(
                                (
                                    f"心茶訂單【{order_key}】同母單最早到貨日不一致，無法拋轉廠商\n", order_key
                                )
                            )
                    
                    print(f'split_berfore_order_no: {split_berfore_order_no}')
                    print(f'current_vendor: {current_vendor}')
                    print(f'current_earliest_arrival_date: {current_earliest_arrival_date}')
                    print(f'current_white_list: {current_white_list}')
        return error_message, error_to_vendor_order, error_data

    def __to_vendor(self, error_order: list, error_upd_order: list, error_to_vendor_order: list, error_data: list) -> bool:
        """
        處理拋轉廠商
        :param error_order: 錯誤檢查訂單
        :param error_upd_order: 錯誤修改訂單
        :param error_to_vendor_order: 錯誤訂單
        :param error_data: 錯誤資料
        """
        # 廠商參數
        upd_delete_vendor_param: list = [] # 狀態5發生廠商已確認又重拋狀態，需將原有訂單刪除
        crt_to_vendor_param: list = []
        # 訂單管理總表參數
        upd_to_vendor_param: list = []
        upd_status_param: list = []
        # 用料明細參數
        crt_use_item_param: list = []
        upd_use_item_cancel_param: list = []
        upd_use_item_delete_param: list = []
        # 更新訂單管理總表-BOM表
        upd_order_manage_bom: list = []
        # 重新查詢該訂單明細避免資料不一致
        order_key_qry: list = []
        for per_vendor in self.b_to_c:
            order_key: str = per_vendor.get('order_key')
            order_key_qry.append(order_key)
        new_b_to_c: list = xin_tea.qry_order_manage_summary_repeat(order_key_qry)
        
        # BOM展算規則
        can_spread_rule: list = xin_tea.qry_bom_spread_rule_can_spread()
        no_spread_rule: list = xin_tea.qry_bom_spread_rule_no_spread()
        
        can_spread: list = [per_can.get('item_category') for per_can in can_spread_rule]
        no_spread: list = [per_no.get('item_category') for per_no in no_spread_rule]
        
        
        # 替換成重新查詢過後的資料
        self.b_to_c = new_b_to_c
        success_data: list = []
        for per_vendor in self.b_to_c:
            order_key: str = per_vendor.get('order_key')
            if order_key in error_order:
                continue
            if order_key in error_upd_order:
                continue
            if order_key in error_to_vendor_order:
                continue
            success_data.append(
                (
                    '', per_vendor.get('order_key')
                )
            )
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
            # 5以外的拋轉 2 3 4 
            if status in ['2', '3', '4']:
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
                            per_vendor.get('google_sheet_name', ''), '0', per_vendor.get('order_key', '')
                        )
                    )
            # 5.無拋轉廠商資料or已拋轉但是廠商已確認則要新增
            if status == '5':
                if not order_data or (len(order_data) > 0 and per_vendor.get('vendor_check') == '1'):
                        vendor_look_status: str = '異動'
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
                        vendor_look_status: str = '異動'
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
                origin_bom: str = ''
                try:
                    origin_bom = per_vendor.get('bom_bpm_form_id')
                except:
                    pass
                if origin_bom is None:
                    origin_bom = ''
                # BOM 改抓現行料件主檔(避免預購期間BOM表有異動)
                item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
                if item_data:
                    bom = item_data[0].get('bom')
                if bom != origin_bom:
                    # 訂單上的BOM跟料件主檔不一致要將訂單上的BOM更新成料件主檔一樣的
                    upd_order_manage_bom.append(
                        (
                            bom, per_vendor.get('order_key')
                        )
                    )
                # 有BOM表且品項類別為A,B，則查詢該品項之BOM表
                print('bom', bom)
                if len(bom) > 0 and per_vendor.get('item_category') in can_spread:
                    bom_data: list = xin_tea.qry_bom_by_item(per_vendor.get('item'), bom)
                    order_m_item: str = per_vendor.get('item')
                    quantity: float = per_vendor.get('quantity')
                    
                    for per_bom in bom_data:
                        m_item: str = per_bom.get('m_item')
                        s_item: str = per_bom.get('s_item')
                        # 只算一階料
                        if order_m_item == m_item :
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
                                    per_vendor.get('e_commerce_platform_order_no'), per_vendor.get('split_berfore_order_no'), per_vendor.get('order_key'), per_vendor.get('to_order_generate_date'), 
                                    per_vendor.get('earliest_arrival_date'), per_vendor.get('latest_arrival_date'),
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
                            per_vendor.get('e_commerce_platform_order_no'), per_vendor.get('split_berfore_order_no'), per_vendor.get('order_key'), per_vendor.get('to_order_generate_date'),
                            per_vendor.get('earliest_arrival_date'), per_vendor.get('latest_arrival_date'),
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
                                                                                crt_use_item_param, upd_use_item_cancel_param, upd_use_item_delete_param, error_data, 
                                                                                success_data, upd_order_manage_bom)
        if result:
            return '一鍵轉廠商成功'
        return '一鍵轉廠商失敗'
    