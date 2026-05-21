from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea
from datetime import datetime
from programs.core.cloud_eip.web_service import EIPService
from programs.core.data_work import string_format
import time

# 產生禮盒生產單
class GenerateGiftBox:
    def __init__(self, sq_form_id: list, user_data: dict):
        self.sq_form_id = sq_form_id
        self.user_data: dict = user_data

    def execute(self) -> dict:
        """
        執行產生禮盒生產單
        :return: dict
        """
        # 檢查規則
        error_msg: str = ''
        error_order_key: list
        error_msg, error_order_key = self.__check_rule()
        # 檢查項目
        result: dict = self.__generate_gift_box(error_order_key)
        if error_msg:
            final_message: str = f"{error_msg}{result.get('error_msg')}"
            if len(result.get('new_form')) > 0:
                final_message += f"其餘報價單拋轉禮盒生產單結果如下：{result.get('message')}"
            return {'new_form': result.get('new_form'), 'status': 'false', 'message': final_message}
        return result
    
    def __check_rule(self) -> str:
        """
        檢查是否符合產生禮盒生產單規則
        """
        error_msg: str = ''
        error_order_key: list = []
        for per_sq in self.sq_form_id:
            detail: list = []
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_gift_box(per_sq.get('key'))
            for per_sq in sq_form_detail:
                # 是否有先產生B2B訂單
                bpm_form_status: str = EIPService().get_subject_state(per_sq.get('bpm_form_id')).strip()
                if (per_sq.get('bpm_form_id') == '' or bpm_form_status == '-1'):
                    error_order_key.append(per_sq.get('order_key'))
                    error_msg += f"訂單編號【{per_sq.get('order_key')}】未產生B2B訂單，請先產生B2B訂單<br>"
                # 規格調整為需要調整，必須調整過後才能產生禮盒生產單
                if per_sq.get('specific_remind') == '是':
                    error_order_key.append(per_sq.get('order_key'))
                    error_msg += f"訂單編號【{per_sq.get('order_key')}】規格需調整，請先調整規格後再產生禮盒生產單<br>"
                # 差異數需為0才能產生B2B訂單
                if float(per_sq.get('quantity') or 0) - float(per_sq.get('different')) != 0:
                    error_order_key.append(per_sq.get('sq_form_id'))
                    error_msg += f"報價單編號【{per_sq.get('sq_form_id')}】差異數需為0才能產生B2B訂單<br>"
                # 生產廠商不可為空
                if per_sq.get('generate_vendor_by_generate') == '':
                    error_order_key.append(per_sq.get('order_key'))
                    error_msg += f"料號：【{per_sq.get('item')}】，批次：【{per_sq.get('item_batch')}】，生產廠商不可為空<br>"
                # 預測類別不可以開禮盒生產單
                if per_sq.get('order_type') == '預測':
                    error_order_key.append(per_sq.get('order_key'))
                    error_msg += f"報價單編號【{per_sq.get('sq_form_id')}】為【預測類別】，不可開立禮盒生產單<br>"
        
        return error_msg, error_order_key

    def __generate_gift_box(self, error_order_key: list) -> str:
        """
        產生禮盒生產單
        :param error_order_key: list 錯誤訂單編號
        """
        form_id: list = []
        crt_gift_box_status: list = []
        upd_b_to_b_new_form_id: list = []
        clear_update_remind: list = []
        error_msg: str = ''
        for k, per_sq in enumerate(self.sq_form_id):
            # 跳過有錯誤的訂單
            if per_sq.get('key') in error_order_key:
                continue
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_gift_box(per_sq.get('key'))
            # 查詢可拋轉類別
            to_generate_gift_data: list = xin_tea.qry_to_generate_gift()
            to_generate_gift: list = [per_data['item_category'] for per_data in to_generate_gift_data]
            
            for per_detail in sq_form_detail:
                if per_detail.get('order_key') != per_sq.get('key'):
                    continue
                update_bpm_form_id: str = per_detail.get('bpm_generate_id')
                is_new_create: bool = False
                bom_data: list = []
                detail: list = []
                # 符合拋轉條件才可以拋轉(1筆訂單明細1張禮盒生產單)
                if per_detail.get('category') in to_generate_gift and per_detail.get('bom') not in [None, '']:
                    # 判斷是否已建立禮盒生產單
                    bpm_form_status: str = EIPService().get_subject_state(update_bpm_form_id).strip()
                    # 簽核通過不可產生或更新禮盒生產單
                    if bpm_form_status == '1':
                        error_msg += f"訂單編號【{per_detail.get('order_key')}】禮盒生產單已簽核通過，無法更新或重新產生<br>"
                        continue
                    if update_bpm_form_id == '' or bpm_form_status in ['-1', '']:
                        update_bpm_form_id = ''
                        is_new_create = True
                    
                    # 查詢該料件BOM(有客製用客製BOM,無則用標準BOM)
                    if per_detail.get('customize_bom'):
                        bom: str = per_detail.get('customize_bom')
                        bom_data = xin_tea.qry_customize_bom(bom)
                    else:
                        bom: str = per_detail.get('bom')
                        bom_data = xin_tea.qry_bom_detail(bom)
                    
                    # 處理廠商資料
                    vendor: list = xin_tea.qry_vendor_data(per_detail.get('generate_vendor_by_generate'))
                    for i, per_bom in enumerate(bom_data):
                        estimate_use_quantity: float = float(per_detail.get('quantity'))*float(per_bom.get('use_quantity'))
                        
                        customize_item: str = ''
                        if per_bom.get('customize_type') in ['外購品']:
                            average = per_bom.get('average', '')
                            if average:
                                try:
                                    avg_float = float(average)
                                    average = str(int(avg_float) if avg_float.is_integer() else avg_float)
                                except (ValueError, TypeError):
                                    average = ''
                            if average is None:
                                average = ''
                            customize_item_str: str = ''        
                            if per_bom.get('customize_item') is None:
                                customize_item_str = ''
                            else:
                                customize_item_str = per_bom.get('customize_item', '')
                            customize_item = f"每盒放{average}個，{customize_item_str}"
                        else:
                            if per_bom.get('customize_item') is None:
                                customize_item = ''
                            else:
                                customize_item = per_bom.get('customize_item', '')
                        detail.append(
                            {
                                'mItem': per_bom.get('item'), 'mItemName': per_bom.get('item_name'),
                                '母件預計生產數量': int(per_detail.get('quantity')), 'sItem': per_bom.get('s_item'),
                                'sItemName': per_bom.get('s_item_name'), 'sItemSpec': per_bom.get('s_item_spec'),
                                'unit': per_bom.get('unit'), 'sCategory': per_bom.get('category'),
                                'useQuantity': int(per_bom.get('use_quantity')), '預計耗用量': int(estimate_use_quantity+int(per_bom.get('adjustment_quantity'))),
                                '調整量': int(per_bom.get('adjustment_quantity')), '合計': int(estimate_use_quantity+int(per_bom.get('adjustment_quantity'))),
                                '客製化料件': customize_item, 'key1': f"{per_bom.get('s_item')}{vendor[0].get('consume_warehouse')}", 'uu1': f"{per_detail.get('order_key')}-{i+1}", 
                                '預計耗用量1': -int(estimate_use_quantity+int(per_bom.get('adjustment_quantity'))),
                                '耗料倉別1': vendor[0].get('consume_warehouse', '')
                            }
                        )
                    item_data: list = xin_tea.qry_item_by_item_id(per_detail.get('item'))
                    param: list = {
                        'version': '2020a', 'subject': '',
                        'content': '',
                        'contentFields': [
                            {
                                'fillDate': string_format.date_time_to_timestamp(str(datetime.now().strftime('%Y-%m-%d'))), 'filler': self.user_data['bpm_account'],
                                '生產廠商': f"{vendor[0].get('vendor_id')}{vendor[0].get('vendor_name')}({vendor[0].get('sys_id')})", '廠商名稱': vendor[0].get('vendor_name'),
                                '廠商統編': vendor[0].get('vendor_uniform_invoice_no'), '耗料倉別': vendor[0].get('consume_warehouse'), '委託人': vendor[0].get('client'), 
                                '委託人電話': vendor[0].get('client_phone'), '委託人地址': vendor[0].get('client_address'),
                                'sourceNo': per_detail.get('bpm_form_id'), 'customer': per_detail.get('customer_name'),
                                'orderNote': per_detail.get('order_remark'), 'dDate1': string_format.date_time_to_timestamp(str(per_detail.get('earliest_arrival_date_by_generate'))), 
                                'dDate2': string_format.date_time_to_timestamp(str(per_detail.get('latest_arrival_date_by_generate'))),
                                'standardCustomized': f"{per_detail.get('standard_or_customization')}({per_detail.get('standard_or_customization')}#unknown)",
                                '自製料號選擇': f"{per_detail.get('item')}{item_data[0].get('item_name')}({item_data[0].get('bpm_form_id')})",
                                'category': per_detail.get('category'), 'item': per_detail.get('item'),
                                'itemName': per_detail.get('item_name'), '圖片': '', 'itemSpec': '',
                                'customizedSpec': per_detail.get('customization_descript'), 'note2': per_detail.get('package_descript_file', ''),
                                'bomNo': per_detail.get('bom', ''), 'quantity': int(per_detail.get('quantity')), '完工入庫倉別': vendor[0].get('inventory_in_warehouse'),
                                'quantityCompleted': int(per_detail.get('quantity')), 'note1': '',
                                '每單位代工費': '', '其他費用': '', '代墊運費': '', '未稅總費用': '',
                                '含稅總費用': '', '入庫倉': vendor[0].get('inventory_in_warehouse'), 
                                '出庫倉': vendor[0].get('consume_warehouse'), 'key': f"{per_detail.get('item')}{vendor[0].get('inventory_in_warehouse')}", 'uu': per_detail.get('order_key')
                            }
                        ],
                        'dataFields': detail,
                        'countField': 'useQuantity'
                    }
                    
                    # 外部起單
                    new_form_id: str = EIPService().crt(self.user_data['bpm_account'], '心茶禮盒生產單_代開', param, to_be_modified_subject_id=update_bpm_form_id).strip()
                    form_id.append(new_form_id)
                    
                    # time.sleep(1)  # 避免EIP系統忙碌無法即時取得簽核狀態
            
                    sign_data: list = EIPService().get_sign_data(new_form_id)
                    level: list = sign_data.get('SignHistory')
                    # 取得當前關卡名稱
                    final_level: dict = level[-1]
                    
                    # 建立禮盒生產單狀態資料
                    if is_new_create:
                        crt_gift_box_status.append((new_form_id, '0'))
                    
                    # 更新訂單管理總表B2B新增的禮盒生產單號
                    upd_b_to_b_new_form_id.append((new_form_id, '0', final_level['stepName'], per_detail.get('order_key')))
                    
                    # 清除提醒
                    clear_update_remind.append((per_detail.get('order_key'),))
                    
                    # 更新2B訂單-禮盒生產單表單連結
                    EIPService().upd_data_form_V2(per_detail.get('bpm_form_id'), per_detail.get('order_seq'), 禮盒生產單=f"{new_form_id}【{new_form_id}】({new_form_id}#smartForm)]/n")
        result: bool = xin_tea.crt_or_update_gift_box_form_status(crt_gift_box_status, upd_b_to_b_new_form_id, clear_update_remind)
        if result:
            return {'new_form': form_id, 'status': 'success', 'message': f"BPM生產單新增/更新成功，BPM單號：{', '.join(form_id)}", 'error_msg': error_msg}
        return {'new_form': form_id, 'status': 'fail', 'message': '禮盒生產單產生失敗', 'error_msg': error_msg}