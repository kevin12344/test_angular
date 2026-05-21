from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea
from datetime import datetime
from programs.core.cloud_eip.web_service import EIPService
from programs.core.data_work.date_format import weekly_change
from programs.core.round.round_v3 import round_v3
from programs.core.data_work import string_format
import time

# 產生B2B銷售訂單
class GenerateBToBOrder:
    def __init__(self, sq_form_id: list, user_data: dict):
        self.sq_form_id: list = sq_form_id
        self.error_sales_quotation: list = []
        self.errorm_msg: str = ''
        self.user_data: dict = user_data
        self.calendar_start: str = xin_tea.qry_calendar_start_date()[0]['value']

    def execute(self) -> dict:
        """
        執行產生B2B銷售訂單
        :return: dict
        """
        # 檢查
        error_msg: str
        error_order_key: list
        error_msg, error_order_key = self.__check_rule()
        result: dict = self.__generate_b_to_b_order(error_order_key)
        if error_msg:
            final_message: str = f"{error_msg}"
            if len(result.get('new_form')) > 0:
                final_message += f"其餘報價單拋轉B2B銷售訂單結果如下：{result.get('message')}"
            return {'new_form': result.get('new_form'), 'status': 'false', 'message': final_message}
        return result
    
    def __check_rule(self) -> str:
        """
        檢查規則
        """
        error_msg: str = ''
        error_order_key: list = []
        for per_sq_form in self.sq_form_id:
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_by_sq_id(per_sq_form)
            for per_sq in sq_form_detail:
                # 規格調整為需要調整，必須調整過後才能產生B2B訂單
                if per_sq.get('specific_remind') == '是':
                    error_order_key.append(per_sq.get('sq_form_id'))
                    error_msg += f"料號【{per_sq.get('item')}】規格需調整，請先調整規格後再產生B2B訂單<br>"
                # 差異數需為0才能產生B2B訂單
                if float(per_sq.get('max_quantity') or 0) - float(per_sq.get('different')) != 0:
                    error_order_key.append(per_sq.get('sq_form_id'))
                    error_msg += f"料號【{per_sq.get('item')}】差異數需為0才能產生B2B訂單<br>"
            # 報價單類別需選擇才能產生B2B訂單
            if sq_form_detail[0].get('order_type') == '':
                error_order_key.append(per_sq_form)
                error_msg += f"報價名稱【{sq_form_detail[0].get('sales_quotation_name')}】，報價單類別未選擇，請先設定報價單類別後再產生B2B訂單<br>"
        return error_msg, error_order_key  
    
    def __generate_b_to_b_order(self, error_order_key: list) -> str:
        """
        產生B2B銷售訂單
        :param error_order_key: 錯誤報價單
        """
        form_id: list = []
        upd_b_to_b_new_form_id: list = []
        crt_b_to_b_order_status: list = []
        clear_update_remind: list = []
        is_customize_order: str = '否'
        for per_sq in self.sq_form_id:
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_by_sq_id(per_sq)
            for per_detail in sq_form_detail:
                if per_detail.get('standard_or_customization') == '客製化禮盒':
                    is_customize_order = '是'
                    break
            if is_customize_order == '是':
                break
        for per_sq in self.sq_form_id:
            # 有錯誤的報價單不進行拋轉
            if per_sq in error_order_key:
                continue
            detail: list = []
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_by_sq_id(per_sq)
            is_already_create: bool = False
            # 表單已簽核通過不可再建立/修改表單
            bpm_form_status: str = EIPService().get_subject_state(sq_form_detail[0]['bpm_form_id']).strip()
            if bpm_form_status == '1':
                self.error_sales_quotation.append(per_sq)
                self.errorm_msg = '表單已簽核通過不可再建立/修改表單'
                continue
            update_form_id: str = sq_form_detail[0]['bpm_form_id']
            # 新增B2B訂單(表單未建立)
            if sq_form_detail[0]['bpm_form_id'] == '' and bpm_form_status in ['0']:
                is_already_create = True
            if bpm_form_status in ['-1', '']:
                is_already_create = True
                update_form_id = ''
            total_amount: float = 0
            # 查詢可拋轉類別
            to_generate_gift_data: list = xin_tea.qry_to_generate_gift()
            to_generate_gift: list = [per_data['item_category'] for per_data in to_generate_gift_data]
            order_num: int = 0
            for i, per_detail in enumerate(sq_form_detail):
                is_generate: str = '0'
                if per_detail.get('category') in to_generate_gift and per_detail.get('bom') not in [None, '']:
                    is_generate = '1'
                # bom: str = per_detail.get('customize_bom') if per_detail.get('customize_bom') else per_detail.get('bom')
                detail.append(
                    {
                        'item': per_detail.get('item', ''), 'category': per_detail.get('category'),
                        'itemName': per_detail.get('item_name', ''), 'itemSpec': per_detail.get('customization_descript', ''),
                        '客製規格描述': per_detail.get('customization_descript'), 'unitPrice': int(per_detail.get('unit_price')),
                        'quantity': int(per_detail.get('quantity')), '優惠折數a': per_detail.get('discount1'),
                        '單件優惠價': int(per_detail.get('one_discount')), '訂單金額': int(per_detail.get('order_money')),
                        'standardCustomized': self.__check_standard_or_customize(per_detail.get('standard_or_customization'), per_detail.get('category')), 
                        '圖片': '', '拋轉生產單': is_generate, '計算key': f"{per_detail.get('item')}{sq_form_detail[0].get('order_type')}",
                        'key': f"{per_detail.get('sq_form_id')}-{i+1}", '用料清單單號': per_detail.get('bom'), '禮盒生產單': '', 'mOrderNo': '',
                        '採購單連結': per_detail.get('purchase_connect'), '產品說明1': per_detail.get('product_descript_one', ''),
                        '產品說明2': per_detail.get('product_descript_two', ''), '備註': per_detail.get('detail_remark', ''),
                        '料號合併收尋欄': per_detail.get('item', '')
                    }
                )
                order_num += int(per_detail.get('quantity', 0))
                total_amount += float(per_detail.get('order_money', 0))
            # 查詢客戶主檔
            customer_data: list = xin_tea.qry_customer_data(sq_form_detail[0].get('customer_name'))
            # 外部起單
            is_direct_from_oem: str = sq_form_detail[0].get('is_direct_from_oem')
            
            if is_direct_from_oem != '':
                is_direct_from_oem = f"{sq_form_detail[0].get('is_direct_from_oem')}({sq_form_detail[0].get('is_direct_from_oem')}#unknown)"
            param: dict = {
                'version': '2020a', 'subject': '',
                'content': '', 
                'contentFields': [
                    {
                        '開立人員': self.user_data['name'], '訂單開立日期': string_format.date_time_to_timestamp(str(datetime.now().strftime('%Y-%m-%d'))),
                        '報價單類別': f"{sq_form_detail[0].get('sales_quotation_type')}({sq_form_detail[0].get('sales_quotation_type')}#unknown)",
                        '客戶窗口慣用聯繫方式': sq_form_detail[0].get('customer_contact'), '報價單連結': f"{sq_form_detail[0].get('sales_quotation_url')}/edit?usp=sharing",
                        '下訂憑證連結': sq_form_detail[0].get('order_invoice_url'), '客戶預計決策日': string_format.date_time_to_timestamp(sq_form_detail[0].get('customer_estimate_decide_date')),
                        '最早到貨日': string_format.date_time_to_timestamp(sq_form_detail[0].get('earliest_arrival_date')), '最晚到貨日': string_format.date_time_to_timestamp(sq_form_detail[0].get('latest_arrival_date')),
                        '選擇客戶': f"{customer_data[0].get('customer_id')}{customer_data[0].get('customer_name')}({customer_data[0].get('sys_id')})",
                        '客戶簡稱': sq_form_detail[0].get('customer_name'), '公司抬頭': sq_form_detail[0].get('company_title'),
                        '客戶統編': sq_form_detail[0].get('uniform_invoice_no'), '客戶地址含郵遞區號': sq_form_detail[0].get('address'),
                        '客戶窗口': sq_form_detail[0].get('customer_window'), '客戶電話': sq_form_detail[0].get('customer_phone'),
                        '客戶信箱': sq_form_detail[0].get('customer_email'), '付款條件': sq_form_detail[0].get('payment_term'),
                        '付款方式': sq_form_detail[0].get('payment'), '電子發票': f"{sq_form_detail[0].get('ele_invoice')}({sq_form_detail[0].get('ele_invoice')}#unknown)",
                        '是否代工廠直出': is_direct_from_oem, '配送方式': f"{sq_form_detail[0].get('delivery_method')}({sq_form_detail[0].get('delivery_method')}#unknown)",
                        '訂單備註': sq_form_detail[0].get('order_remark', ''), '心茶聯絡人': sq_form_detail[0].get('xin_tea_connector'), '心茶聯絡電話': sq_form_detail[0].get('xin_tea_connect_phone'), 
                        '心茶聯絡信箱': sq_form_detail[0].get('xin_tea_connect_email'),
                        '分隔線': '------------------以下金額計算------------------', '訂單金額取值': '',
                        '是否為客製化訂單': is_customize_order, '商品與客製服務金額': sq_form_detail[0]['product_and_customization_money'], '訂單總金額1': sq_form_detail[0]['product_and_customization_money'],
                        '運費單件金額': sq_form_detail[0].get('freight_per_piece_money'), '運費數量': sq_form_detail[0]['freight_amount'], '優惠折數': sq_form_detail[0]['discount'], '運費優惠價': sq_form_detail[0]['freight_discount'],
                        '總運費': sq_form_detail[0]['total_freight'], '小計1': sq_form_detail[0]['product_and_customization_money']+sq_form_detail[0]['total_freight'], '付款手續費': sq_form_detail[0]['payment_processing_fee'], '付款手續費優惠': sq_form_detail[0]['payment_processing_fee_discount'],
                        '付款手續費1': int(round_v3((sq_form_detail[0]['product_and_customization_money']+sq_form_detail[0]['total_freight'])*0.01*sq_form_detail[0]['payment_processing_fee_discount'], 0)),
                        '小計2': sq_form_detail[0]['final_total'], '訂單數量': int(sq_form_detail[0]['total_order_num']), '配送單': '',
                        '訂單類別': sq_form_detail[0].get('order_type'), '分隔線2': '------------------以下不用填------------------',
                        'message': '', 'sourceNo': '', 'uu': sq_form_detail[0].get('sq_form_id'), '年份': datetime.now().strftime('%Y'), '月份': datetime.now().strftime('%m'), 
                        '周別': str(weekly_change(sq_form_detail[0].get('earliest_arrival_date').replace('-', '/'), self.calendar_start))
                        # =vlookup(OFFSET($V$1,ROW()-1,0),'行事曆'!B:D,3,0)
                    }
                ],
                'dataFields': detail,
                'countField': '訂單金額'
            }
            bpm_form_id: str = EIPService().crt(self.user_data['bpm_account'], '心茶銷售訂單_2B_代開', param, to_be_modified_subject_id=update_form_id).strip()
            form_id.append(bpm_form_id)

            # time.sleep(1)  # 避免EIP系統忙碌無法即時取得簽核狀態
            
            sign_data: list = EIPService().get_sign_data(bpm_form_id)
            level: list = sign_data.get('SignHistory')
            # 取得當前關卡名稱
            final_level: dict = level[-1]

            # 更新訂單管理總表B2B新增的BPM單號
            upd_b_to_b_new_form_id.append(
                (
                    bpm_form_id, final_level['stepName'], per_sq
                )
            )
            if is_already_create:
                # 新增B2B訂單狀態資料
                crt_b_to_b_order_status.append(
                    (
                        bpm_form_id, '0'
                    )
                )
            # 清除提醒
            clear_update_remind.append(
                (
                    per_sq,
                )
            )
        result: bool = xin_tea.upd_genereate_b_to_b_order(upd_b_to_b_new_form_id, crt_b_to_b_order_status, clear_update_remind)
        if result:
            return {'new_form': form_id, 'status': 'success', 'message': f"BPM訂單新增/更新成功，BPM單號：{', '.join(form_id)}"}
        return {'new_form': form_id, 'status': 'fail', 'message': 'B2B銷售訂單產生失敗'}
    
    @staticmethod
    def __check_standard_or_customize(standard_or_customized: str, item_category: set) -> str:
        """
        判斷是標準品或客製品
        :param standard_or_customized: 標準或客製化
        :param item_category: 料件類別
        :return: str
        """
        if item_category != 'A':
            return ''
        if standard_or_customized == '客製化禮盒':
            return '客製化禮盒(客製化禮盒)'
        else:
            return '標準禮盒(標準禮盒)'