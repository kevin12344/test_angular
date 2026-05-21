import pandas as pd
import re
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea
from programs.core.db_process.jw_common import main as jw_common
from programs.core.work_day.work_day import next_working_day
from programs.core.round.round_v3 import round_v3
from datetime import datetime, timedelta
from flask import session

class UploadNewOrderChange:
    def __init__(self, new_order, e_commerce_platform: str, direct_data: bool = False):
        if not direct_data:
            self.new_order: list = pd.read_excel(new_order).fillna('').to_dict(orient='records')
        else:
            self.new_order: list = new_order
        self.e_commerce_platform = e_commerce_platform
        self.error_msg_for_error_arrival_area: str = ''
        self.error_num_for_error_arrival_area: int = 0
        self.error_order_no_for_error_arrival_area: list = []

    def change_data(self):
        """依電商平台決定轉換資料邏輯"""
        print('self.new_order', self.new_order)
        return self.__upload_new_order()

    def __upload_new_order(self) -> str:
        """新訂單處理"""
        result = self.__check_excel_column_correct()
        if result is True:
            message: str
            error_order_no: list
            no_import_num: int
            error_item_category: str
            repeat_upload_error: int
            item_exist_num: int
            item_must_bom_actual_no_bom_num: int
            item_no_set_reference_num: int
            no_currency_num: int
            split_order_error: int
            check_split_order_error: list 
            message, error_order_no, no_import_num, error_item_category, repeat_upload_error, item_exist_num, no_logistics_num, item_must_bom_actual_no_bom_num, item_no_set_reference_num, no_currency_num, split_order_error, check_split_order_error = self.__check_order_can_import()
            print('error_order_no', error_order_no)
            print('處理沒算到最原始拆單錯誤數量', check_split_order_error)

            # 檢查通過後，轉換訂單資料，並寫入資料庫
            exe_result: bool = self.__order_to_db(error_order_no)
            
            message = message + self.error_msg_for_error_arrival_area + f"請檢查訂單狀態\n{self.e_commerce_platform}其他訂單已上傳!"
 
            if message:
                # 將錯誤訊息寫入table
                error_message: list = [
                    (
                        self.e_commerce_platform, '新訂單上傳', message
                    )
                ]
                xin_tea.crt_upload_record(error_message)
            
            # 計算實際成功處理的明細筆數
            success_count = 0
            error_detail_count = 0

            order_amount: list = []
            for per_order in self.new_order:
                if self.e_commerce_platform == 'line 禮物':
                    order_no = str(per_order.get('訂單編號'))
                elif self.e_commerce_platform == 'shopline':
                    order_no = str(per_order.get('訂單號碼'))[:18]
                elif self.e_commerce_platform == 'pinkoi':
                    order_no = str(per_order.get('訂單編號'))

                if order_no in error_order_no:
                    error_detail_count += 1
                else:
                    success_count += 1
                
                # 找出發生問題前正確要變拆單錯誤的明細增加數量
                # 查找是否已存在該訂單號碼
                found_index = -1
                for i, item in enumerate(order_amount):
                    if item['order_no'] == order_no:
                        found_index = i
                        break
                
                if found_index == -1:
                    # 沒找到，新增
                    order_amount.append({'order_no': order_no, 'total': 1})
                else:
                    # 找到了，增加數量
                    order_amount[found_index]['total'] += 1

            for per_order in order_amount:
                order_no: str = per_order.get('order_no')
                total: int = per_order.get('total')
                
                # 計算該訂單號碼在 error_order_no 中出現的次數
                error_count = error_order_no.count(order_no)
                
                # 如果該訂單有錯誤，計算正常明細數量（總數 - 錯誤數）
                if error_count > 0:
                    normal_detail_count = total - error_count
                    # 將正常明細也視為拆單錯誤（因為同一母單有部分錯誤）
                    split_order_error += normal_detail_count
                    print(f"訂單 {order_no}: 總明細={total}, 錯誤明細={error_count}, 正常明細變拆單錯誤={normal_detail_count}")

            print(f"最終拆單錯誤筆數: {split_order_error}")
                

            error_detail_count += self.error_num_for_error_arrival_area

            success_count -= self.error_num_for_error_arrival_area

            error_order_no = error_order_no + self.error_order_no_for_error_arrival_area
            print('重複上傳筆數', repeat_upload_error)
            print('到貨區間異常筆數', self.error_num_for_error_arrival_area)
            print('總明細筆數:', len(self.new_order))
            print('錯誤訂單號碼數:', len(error_order_no))
            print('錯誤明細筆數:', error_detail_count)
            print('成功明細筆數:', success_count)
            final_error_count: int = no_import_num + error_item_category + self.error_num_for_error_arrival_area + repeat_upload_error + item_exist_num + no_logistics_num + item_must_bom_actual_no_bom_num + item_no_set_reference_num + no_currency_num + split_order_error
            if exe_result:
                return f"{self.e_commerce_platform}新訂單上傳成功筆數: {success_count}，錯誤筆數: {final_error_count}<br>狀態錯誤筆數: {no_import_num}, 料件類別錯誤筆數: {error_item_category}, \
                到貨區間異常筆數: {self.error_num_for_error_arrival_area}, 重複上傳筆數: {repeat_upload_error}, 料件不存在筆數: {item_exist_num}, 物流方式不存在筆數: {no_logistics_num}, 料件類別無BOM資料筆數: {item_must_bom_actual_no_bom_num}, \
                料號無參照表設定筆數: {item_no_set_reference_num}, 貨幣無資料筆數: {no_currency_num}, 拆單錯誤筆數: {split_order_error}"
            return f"{self.e_commerce_platform}新訂單上傳失敗!"
        return result

    def __check_excel_column_correct(self) -> bool | str:
        """
        檢查Excel欄位是否正確
        :return: True 如果欄位正確，否則返回錯誤訊息
        """
        try:
            # 取得上傳檔案的欄位名稱
            column_key = self.new_order[0].keys()
            
            # 從資料庫取得該平台需要的欄位設定
            check_column: list = xin_tea.qry_e_commerce_platform_column(self.e_commerce_platform)
            # 檢查是否有取得欄位設定
            if not check_column:
                return f'無法取得 {self.e_commerce_platform} 的欄位設定'
                
            # 檢查資料庫中必要的欄位是否在 Excel 中存在
            missing_columns: list = []
            for per_column in check_column:
                column_name = per_column.get('column_name')
                if column_name not in column_key:
                    missing_columns.append(column_name)
            
            # 如果有缺少的欄位，返回錯誤訊息
            if missing_columns:
                return f'檔案格式錯誤! 缺少以下欄位: {", ".join(missing_columns)}'
            return True
        except Exception as e:
            return f'檢查欄位時發生錯誤: {str(e)}'
    
    def __order_to_db(self, error_order_no: list):
        """
        將訂單資料寫入資料庫
        :param error_order_no: 錯誤的訂單號碼
        """
        import_order: list = []
        new_order: list = []
        qry_order: list = []
        now_date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        """LINE禮物"""
        if self.e_commerce_platform == 'line 禮物':
            """
            處理比對同一訂單處理
            """
            # 先找出所有訂單號碼之前編的最後一個數字
            check_order: list = []
            set_order_seq: list = []
            for per_new in self.new_order:
                order_no: str = str(per_new.get('訂單編號'))
                if order_no in error_order_no:
                    continue
                if order_no not in check_order:
                    # 查詢數據庫中已存在的訂單
                    order_data: list = xin_tea.qry_order_data(order_no)
                    check_order.append(order_no)
                    
                    # 找出該訂單的最大序號
                    max_seq = len(order_data)
                    
                    # 保存訂單編號和最大序號
                    set_order_seq.append(f"{order_no}:{max_seq}")
            # 建立順序號查詢字典，儲存每個訂單的最大序號
            order_seq_dict = {}
            for seq_str in set_order_seq:
                order_no, max_seq = seq_str.split(':')
                order_seq_dict[order_no] = int(max_seq)
            # 為每個訂單設置正確的序列號
            for per_new in self.new_order:
                order_no = str(per_new.get('訂單編號'))
                if order_no in error_order_no:
                    continue
                if order_no not in qry_order:
                    qry_order.append(str(order_no))
                
                # 處理到貨區間
                arrival_area_split: str = ''
                arrival_area_data: dict = self.__determined_arrival_area(per_new.get('規格設定'), '(')
                arrival_area_split = arrival_area_data.get('arrival_area_split')
                per_new['arrival_area_split'] = arrival_area_split
                
                # 增加計數並設置 xin_tea_key
                seq: int = order_seq_dict[order_no] + 1
                order_seq_dict[order_no] = seq  # 更新當前訂單的序列號
                per_new['xin_tea_key'] = f"{order_no}-{seq}"
               
                # 不考量子母單的_拋單生產日期
                order_generate_date: str = ''
                
            check_order_no: list = []
            for l, per_new in enumerate(self.new_order):
                white_list: str = ''
                order_no: str = str(per_new.get('訂單編號'))
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                item_data: list = xin_tea.qry_item_data(str(per_new.get('規格管理代碼', '')))
                bom: str = ''
                try:
                    bom = item_data[0]['bom']
                except:
                    pass
                # 處理到貨區間
                arrival_area_split: str = ''
                arrival_area_data: dict = self.__determined_arrival_area(per_new.get('規格設定'), '(')
                arrival_area_split = arrival_area_data.get('arrival_area_split')
                
                # 拋單生產日
                order_generate_date: str = ''
    
                # 是否檢查備註欄訊息
                is_check_remark: str = self.__determined_is_check_remark('', per_new.get('出貨訊息'), '', per_new.get('訂單狀態'))
               
                # 同訂單不同生產廠商
                is_common_order_diff_vendor: str = '一樣'
                if white_list == '例外白名單':
                    is_common_order_diff_vendor = '一樣'
                # 狀態
                status: str = self.__determined_status('', per_new.get('出貨訊息'), '', per_new.get('訂單狀態'))
                # 拆單前單號
                split_befor_order: str = order_no
                
                new_order.append(
                    ('', '', '', '', '', '', '', split_befor_order, is_common_order_diff_vendor, '', #is_common_order_diff_shipping_date, 
                     '',  # latest_arrival_date, 
                     white_list, is_check_remark,  # X欄
                     '',
                     '', #order_generate_date, 
                     '', #earliest_arrival_date, 
                     '', #generate_vendor, 
                     split_befor_order, 'LINE', per_new.get('訂單確認日期', None),
                     per_new.get('訂單狀態', ''), per_new.get('訂單狀態', ''), per_new.get('配送方式', ''),
                     per_new.get('出貨訊息', ''), per_new.get('規格管理代碼', ''), item_data[0]['item_name'], item_data[0]['category'], 
                     bom, per_new.get('商品名稱', ''),
                     per_new.get('規格設定', ''), float(per_new.get('數量') or 0), per_new.get('收件人姓名', ''),
                     per_new.get('收件人聯絡電話', ''), per_new.get('配送地址', ''), '',
                     per_new.get('付款方式', ''), float(per_new.get('商品總金額') or 0), '1', 'TWD', float(per_new.get('商品總金額') or 0), '',
                     '', '心茶', '03-8900198', per_new.get('xin_tea_key'), '', '', session['xin_tea_user_data']['name'], 
                     now_date, per_new.get('arrival_area_split'), status, item_data[0]['unit'], per_new.get('出貨訊息', '')
                    )
                )
                # 匯入資料寫入
                import_order.append(
                    (
                        per_new.get('訂單編號', ''), per_new.get('商品訂單編號', ''), per_new.get('訂單狀態', ''), per_new.get('商品名稱', ''),
                        per_new.get('規格設定', ''), per_new.get('客製刻印選項', ''), per_new.get('商品編號', ''),
                        per_new.get('賣家商品代碼', ''), per_new.get('規格管理代碼', ''), per_new.get('品牌編號', ''),
                        per_new.get('品牌名稱', ''), per_new.get('數量'), per_new.get('價格'), per_new.get('每個商品的折扣'),
                        per_new.get('成本', ''), per_new.get('商品總金額'), per_new.get('訂單優惠券折抵金額'), per_new.get('合計運費'),
                        per_new.get('訂單下載日期'), per_new.get('完成付款日'), per_new.get('地址填寫日'), per_new.get('訂單確認日期'),
                        per_new.get('出貨日期'), per_new.get('寄送完成日期'), per_new.get('配送方式', ''), per_new.get('貨運業者', ''),
                        per_new.get('物流單編號', ''), per_new.get('合併運送群組編號', ''),
                        per_new.get('運費類型', ''), per_new.get('收件人姓名', ''),
                        per_new.get('收件人聯絡電話'), per_new.get('配送地址', ''), per_new.get('郵遞區號', ''), per_new.get('出貨訊息', ''),
                        per_new.get('預設出貨地址', ''), per_new.get('購買類型', ''), per_new.get('付款方式', ''), per_new.get('訂購裝置', ''),
                        per_new.get('發票號碼', ''), per_new.get('開立人', ''), per_new.get('獲得點數', ''),
                        per_new.get('獎項預計發送日期', ''), per_new.get('訂單優惠券主編號', ''), per_new.get('訂單優惠券標題', '') 
                    )
                )
        elif self.e_commerce_platform == 'shopline':
            """
            處理比對同一訂單處理
            """
            # 先找出所有訂單號碼之前編的最後一個數字
            check_order: list = []
            set_order_seq: list = []
            for per_new in self.new_order:
                order_no: str = str(per_new.get('訂單號碼'))[:18]
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                if per_new.get('訂單號碼') not in check_order:
                    # 查詢數據庫中已存在的訂單
                    order_data: list = xin_tea.qry_order_data(per_new.get('訂單號碼'))
                    check_order.append(per_new.get('訂單號碼'))
                    
                    # 找出該訂單的最大序號
                    max_seq = len(order_data)
                    
                    # 保存訂單編號和最大序號
                    set_order_seq.append(f"{per_new.get('訂單號碼')}:{max_seq}")
            # 建立順序號查詢字典，儲存每個訂單的最大序號
            order_seq_dict = {}
            for seq_str in set_order_seq:
                order_no, max_seq = seq_str.split(':')
                order_seq_dict[order_no] = int(max_seq)

            # 為每個訂單設置正確的序列號
            for per_new in self.new_order:
                order_no = per_new.get('訂單號碼')[:18]
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                # shopline 的訂單號碼前 18 碼作為查詢條件
                if order_no[:18] not in qry_order:
                    qry_order.append(order_no[:18])
                
                # 處理到貨區間
                arrival_area_split: str = ''
                arrival_area_data: dict = self.__determined_arrival_area(per_new.get('選項'), '(') # 
                arrival_area_split = arrival_area_data.get('arrival_area_split')
                per_new['arrival_area_split'] = arrival_area_split
                
                # 增加計數並設置 xin_tea_key (使用 LINE 禮物的方式)
                seq: int = order_seq_dict[order_no] + 1
                order_seq_dict[order_no] = seq  # 更新當前訂單的序列號
                per_new['xin_tea_key'] = f"{order_no}-{seq}"
                
                
            check_order_no: list = []
            for k, per_new in enumerate(self.new_order):
                order_no: str = str(per_new.get('訂單號碼'))[:18]
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                item_id: str = per_new.get('商品貨號', '')
                # 特殊處理同訂單不同出貨日期
                if order_no not in check_order_no:
                    check_order_no.append(order_no)
                white_list: str = ''
                item_data: list = xin_tea.qry_item_data(str(per_new.get('商品貨號', '')))
                bom: str = ''
                try:
                    bom = item_data[0]['bom']
                except:
                    pass
                uniform_invoice_no: str = ''
                try:
                    uniform_invoice_no = str(int(float(per_new.get('統一編號'))))
                except:
                    uniform_invoice_no = ''
                if len(uniform_invoice_no) == 9:
                    uniform_invoice_no = f"0{uniform_invoice_no}"
                # 處理備註
                order_remark: str = f"【訂單備註】{per_new.get('訂單備註')}"
                shipping_remark: str = f"【出貨備註】{per_new.get('出貨備註')}" 
                cus1: str = ''
                if per_new.get('自訂訂單欄位 2 (出貨是否需要附上訂單明細)') == '不需要放訂單明細':
                    cus1 = '【送禮用】「不要」放訂單明細'
                remark: str = ''
                if len(str(per_new.get('訂單備註', ''))) > 0:
                    remark += order_remark
                if len(str(per_new.get('出貨備註', ''))) > 0:
                    remark += shipping_remark
                if per_new.get('自訂訂單欄位 2 (出貨是否需要附上訂單明細)') == '不需要放訂單明細':
                    remark += '【送禮用】「不要」放訂單明細'
                # 狀態
                status: str = ''
                # 特殊處理
                if remark:
                    # 抓是否備註欄判斷是否可不用需確認
                    allow_remark: list = xin_tea.qry_is_remark_check_condition()
                    allow_remark_texts = [per_allow.get('text') for per_allow in allow_remark]

                    # 清理remark，移除格式標籤
                    clean_remark = remark.replace('【訂單備註】', '').replace('【出貨備註】', '').strip()

                    # 如果清理後為空或只有 '-'，返回 '2'
                    if not clean_remark or clean_remark == '-':
                        return '2'
                    
                    # 複製一份用來檢查
                    remaining_remark = clean_remark
                    
                    # 移除所有允許的關鍵字
                    for allow_text in allow_remark_texts:
                        if allow_text in remaining_remark:
                            remaining_remark = remaining_remark.replace(allow_text, '')
                    
                    # 清理剩餘內容的空白字符
                    remaining_remark = remaining_remark.strip()

                    # 如果移除允許的關鍵字後還有其他內容，則需要確認
                    if remaining_remark:
                        status = '1'  # 待確認
                    else:
                        status = '2'  # 已確認可拋單
                else:
                    # 已確認可拋單
                    status = '2'
                # 處理到貨區間
                arrival_area_split: str = ''
                arrival_area_data: dict = self.__determined_arrival_area(str(per_new.get('選項')), '(') # 
                arrival_area_split = arrival_area_data.get('arrival_area_split')

                # 是否檢查備註欄訊息
                is_check_remark: str = self.__determined_is_check_remark(order_remark, shipping_remark, cus1, per_new.get('訂單狀態'))
               
                # 同訂單不同生產廠商
                is_common_order_diff_vendor: str = '一樣'
                
                # 拆單前單號(取電商平台訂單單號前18碼)shopline
                split_befor_order: str = order_no[:18]
                """
                # 包裝廠拋單標籤
                package_factory_label: str = ''
                if per_new.get('訂單狀態') == '已取消':
                    package_factory_label = '訂單已取消'
                elif per_new.get('訂單狀態') in ['處理中', '尚未付款']:
                    package_factory_label = '訂單待確認'
                else:
                """
                # 幣別處理
                currency: str = per_new.get('貨幣', '')
                if currency not in ['TWD', '']:
                    exchange: float = float(jw_common.qry_currency(currency)[0]['spot_exchange_rate_bank_selling_rate'])
                else:
                    exchange: float = 1
                origin_money: float = float(per_new.get('付款總金額') or 0)
                total_money: float = round_v3(origin_money * float(exchange), 0)
                new_order.append(
                    ('', '', '', '', '', '', '', split_befor_order, is_common_order_diff_vendor, '',#is_common_order_diff_shipping_date, 
                     '', #latest_arrival_date,
                     white_list, is_check_remark,  # X欄
                     '', #order_generate_date, 
                     '', #earliest_arrival_date, 
                     '', #generate_vendor, 
                     '', #consumer_warehouse
                     str(per_new.get('訂單號碼')), 'SHOPLINE', per_new.get('訂單日期', None),
                     per_new.get('訂單狀態', ''), per_new.get('付款狀態', ''), per_new.get('送貨方式', ''),
                     remark, item_id, item_data[0]['item_name'], item_data[0]['category'], 
                     bom, per_new.get('商品名稱', ''),
                     per_new.get('選項', ''), float(per_new.get('數量') or 0), per_new.get('收件人', ''),
                     per_new.get('收件人電話號碼', ''), per_new.get('完整地址', ''), per_new.get('電郵', ''),
                     per_new.get('付款方式', ''), origin_money, exchange, currency, total_money, per_new.get('發票抬頭', ''),
                     uniform_invoice_no, '心茶', '03-8900198', per_new.get('xin_tea_key'), '', '', session['xin_tea_user_data']['name'],
                     now_date, per_new.get('arrival_area_split'), status, item_data[0]['unit'], remark
                    )
                )
                # 匯入資料寫入
                import_order.append(
                    (
                        per_new.get('訂單號碼', ''), per_new.get('訂單狀態', ''), per_new.get('付款狀態', ''), per_new.get('訂單日期', ''),
                        per_new.get('送貨方式', ''), per_new.get('訂單備註', ''), per_new.get('出貨備註', ''), 
                        per_new.get('商品貨號', ''), per_new.get('商品名稱', ''), per_new.get('選項', ''),
                        per_new.get('數量', ''), per_new.get('收件人', ''), per_new.get('收件人電話號碼', ''), per_new.get('完整地址', ''),
                        per_new.get('電郵', ''), per_new.get('付款方式'), per_new.get('付款總金額'), per_new.get('發票抬頭', ''), uniform_invoice_no,
                        per_new.get('自訂訂單欄位 2 (出貨是否需要附上訂單明細)', ''), per_new.get('自訂訂單欄位 3 (送禮直寄，若需在外箱上註記送禮人，請於收件人名稱後方加上【訂購人名稱】)', '')
                    )
                )
        elif self.e_commerce_platform == 'pinkoi':
            """
            處理比對同一訂單處理
            """
            # 先找出所有訂單號碼之前編的最後一個數字
            check_order: list = []
            set_order_seq: list = []
            for per_new in self.new_order:
                order_no: str = str(per_new.get('訂單編號'))
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                if per_new.get('訂單編號') not in check_order:
                    # 查詢數據庫中已存在的訂單
                    order_data: list = xin_tea.qry_order_data(per_new.get('訂單編號'))
                    check_order.append(per_new.get('訂單編號'))
                    
                    # 找出該訂單的最大序號
                    max_seq = len(order_data)
                    
                    # 保存訂單編號和最大序號
                    set_order_seq.append(f"{per_new.get('訂單編號')}:{max_seq}")

            # 建立順序號查詢字典，儲存每個訂單的最大序號
            order_seq_dict = {}
            for seq_str in set_order_seq:
                order_no, max_seq = seq_str.split(':')
                order_seq_dict[order_no] = int(max_seq)

            # 為每個訂單設置正確的序列號
            for per_new in self.new_order:
                order_no = str(per_new.get('訂單編號'))
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                if order_no not in qry_order:
                    qry_order.append(order_no)
                
                # 處理到貨區間
                arrival_area_split: str = ''
                arrival_area_data: dict = self.__determined_arrival_area(per_new.get('商品規格'), '(')
                arrival_area_split = arrival_area_data.get('arrival_area_split')
                per_new['arrival_area_split'] = arrival_area_split
                
                # 增加計數並設置 xin_tea_key (使用 LINE 禮物的方式)
                seq: int = order_seq_dict[order_no] + 1
                order_seq_dict[order_no] = seq  # 更新當前訂單的序列號
                per_new['xin_tea_key'] = f"{order_no}-{seq}"
                
            check_order_no: list = []
            for i, per_new in enumerate(self.new_order):
                white_list: str = ''
                order_no: str = str(per_new.get('訂單編號'))
                # 不符合匯入條件的訂單編號跳過
                if order_no in error_order_no:
                    continue
                item_id: str = str(per_new.get('SKU'))
                item_data: list = xin_tea.qry_item_data(item_id)
                bom: str = ''
                try:
                    bom = item_data[0]['bom']
                except:
                    pass
                uniform_invoice_no: str = ''
                try:
                    uniform_invoice_no = str(int(per_new.get('統一編號')))
                except:
                    uniform_invoice_no = ''
                # 處理到貨區間
                arrival_area_split: str = ''
                arrival_area_data: dict = self.__determined_arrival_area(per_new.get('商品規格'), '(')
                arrival_area_split = arrival_area_data.get('arrival_area_split')
                
                generate_vendor: str = ''

                # 拋單生產日
                order_generate_date: str = ''
                # 是否檢查備註欄訊息
                is_check_remark: str = self.__determined_is_check_remark(per_new.get('購買人備註', ''), '', '', per_new.get('訂單類型'))
                # 狀態
                status: str = self.__determined_status(per_new.get('購買人備註', ''), '', '', per_new.get('訂單類型'))
                # 同訂單不同生產廠商
                is_common_order_diff_vendor: str = '一樣'
                
                # 拆單前單號
                split_befor_order: str = order_no
                
                # 幣別處理
                currency: str = per_new.get('貨幣別', '')
                if currency not in ['TWD', '']:
                    exchange: float = float(jw_common.qry_currency(currency)[0]['spot_exchange_rate_bank_selling_rate'])
                else:
                    exchange: float = 1
                origin_money: float = float(str(per_new.get('總金額')).replace(',', '') or 0)
                total_money: float = float(str(round_v3(origin_money * float(exchange), 0)))
                new_order.append(
                    ('', '', '', '', '', '', '', split_befor_order, is_common_order_diff_vendor, 
                     '',#is_common_order_diff_shipping_date, 
                     '',#latest_arrival_date, 
                     white_list, is_check_remark,  # X欄
                     order_generate_date, '',#earliest_arrival_date, 
                     generate_vendor, '', per_new.get('訂單編號'), 'PINKOI', per_new.get('訂單成立日期', None),
                     per_new.get('訂單類型', ''), per_new.get('訂單類型', ''), per_new.get('運送方式', ''),
                     f"{per_new.get('購買人備註', '')}", item_id, item_data[0]['item_name'], item_data[0]['category'], 
                     bom, per_new.get('購買品項', ''),
                     per_new.get('商品規格', ''), float(per_new.get('數量') or 0), per_new.get('收件人姓名', ''),
                     per_new.get('收件人電話', ''), per_new.get('收件人地址', ''), '',
                     per_new.get('付款方式', ''), origin_money, exchange, currency, total_money, '',
                     uniform_invoice_no, '心茶', '03-8900198', per_new.get('xin_tea_key'), '', '', session['xin_tea_user_data']['name'],
                     now_date, per_new.get('arrival_area_split'), status, item_data[0]['unit'], f"{per_new.get('購買人備註', '')}"
                    )
                )
                # 匯入資料寫入
                import_order.append(
                    (
                        per_new.get('訂單成立日期', ''), per_new.get('訂單類型'), per_new.get('訂單編號', ''),
                        per_new.get('購買人', ''), per_new.get('收件人姓名', ''), per_new.get('收件人地址', ''), 
                        per_new.get('收件人電話', ''), per_new.get('運送方式', ''), per_new.get('出貨單號', ''),
                        per_new.get('運送地區', ''), per_new.get('購買品項', ''), per_new.get('商品規格', ''),
                        item_id, per_new.get('數量'), per_new.get('商品單價'), per_new.get('小計'),
                        per_new.get('運費'), per_new.get('金流手續費'), per_new.get('折抵'), per_new.get('總金額'),
                        per_new.get('付款方式', ''), per_new.get('貨幣別', ''), per_new.get('退款商品數量'),
                        per_new.get('退款商品金額'), per_new.get('全額退款'), per_new.get('已完成退款'), per_new.get('退款總金額'),
                        per_new.get('購買人非收件人', ''), per_new.get('購買人姓名', ''), per_new.get('購買人地址', ''),
                        per_new.get('購買人電話', ''), per_new.get('發票抬頭', ''), uniform_invoice_no, per_new.get('購買人備註', ''),
                        per_new.get('訂單出貨日期', ''), per_new.get('追蹤單號', ''), per_new.get('Paid At'), per_new.get('電子發票載具', ''),
                        per_new.get('發票號碼', ''), per_new.get('發票日期', ''), per_new.get('折讓號碼', ''), per_new.get('折讓日期', '')
                    )
                )
        # 寫入資料庫
        result: bool = xin_tea.crt_order_manage_summary_b_to_c_and_update_import_data(new_order, import_order, self.e_commerce_platform)
        delete_param: list = []
        if result: 
            upd_data: list = []
            error_order: list = []
            for per_qry in qry_order:
                if per_qry in error_order_no:
                    continue
                # 查詢該筆訂單的所有資料
                order_data: list = xin_tea.qry_order_data(per_qry)
                # 處理訂單最早到貨日
                order_earliest_date: str = ''
                has_any_arrival_area: bool = False
                if len(order_data) > 0:
                    for per_order in order_data:
                        compare_date = per_order.get('arrival_area_split')
                        # 記錄是否有明細包含到貨區間
                        if compare_date != '':
                            has_any_arrival_area = True
                            
                            # 第一筆有到貨區間的直接帶入當比較對象
                            if order_earliest_date == '':
                                order_earliest_date = compare_date
                            else:
                                # 將字串轉換為 datetime 物件
                                # 判斷日期格式是 MM/DD 還是 YYYY/MM/DD
                                if compare_date.count('/') == 1:  # MM/DD 格式
                                    # 轉換為當年的完整日期
                                    current_year = datetime.now().year
                                    compare_month, compare_day = map(int, compare_date.split('/'))
                                    compare_date_obj = datetime(current_year, compare_month, compare_day)
                                else:  # YYYY/MM/DD 格式
                                    compare_date_obj = datetime.strptime(compare_date, "%Y/%m/%d")
                                
                                # 將當前最早日期轉換為 datetime 物件
                                if order_earliest_date.count('/') == 1:  # MM/DD 格式
                                    current_year = datetime.now().year
                                    earliest_month, earliest_day = map(int, order_earliest_date.split('/'))
                                    earliest_date_obj = datetime(current_year, earliest_month, earliest_day)
                                else:  # YYYY/MM/DD 格式
                                    earliest_date_obj = datetime.strptime(order_earliest_date, "%Y/%m/%d")
                                
                                # 直接比較 datetime 物件
                                if compare_date_obj < earliest_date_obj:
                                    order_earliest_date = compare_date
                    
                    # 處理生產廠商
                    generate_vendor_data: dict = self.__determined_generate_vendor_v2(order_data, order_earliest_date)
                    generate_vendor: str = generate_vendor_data.get('vendor')
                    print('generate_vendor', generate_vendor)
                    # 處理耗料倉別
                    consume_warehouse: str = self.__determined_consume_warehouse(generate_vendor_data.get('row_number'))
                    # 製作許可日/最早到貨日/最早出廠日
                    order_generate_date_data: dict = self.__determined_order_generate_date(generate_vendor, order_earliest_date, order_data[0].get('arrival_area_split'), 
                                                                                        order_data[0].get('order_status'), order_data[0].get('order_remark_or_shipping_remark'),
                                                                                        order_data[0].get('logistics_method'))
                    
                    order_generate_date: str = order_generate_date_data.get('order_generate_date')
                    earliest_arrival_date: str = order_generate_date_data.get('earliest_arrival_date')
                    earliest_factory_date: str = order_generate_date_data.get('earliest_factory_date')
                    print('order_generate_date', order_generate_date)
                    print('earliest_arrival_date', earliest_arrival_date)
                    print('earliest_factory_date', earliest_factory_date)
                    to_generate_vendor: str = order_generate_date_data.get('to_generate_vendor')
                    upd_data.append(
                        (
                            generate_vendor, consume_warehouse, order_generate_date, earliest_arrival_date,
                            earliest_factory_date, '一樣', to_generate_vendor, generate_vendor, per_qry
                        )
                    )
                    
                    # 修改錯誤判斷邏輯：只有當該母單有到貨區間但查不到對應資料時才算錯誤
                    if has_any_arrival_area and earliest_arrival_date == '':
                        # 只有當母單中有明細包含到貨區間，但最終查不到最早到貨日時，才算錯誤
                        delete_param.append(
                            (
                                per_qry,
                            )
                        )
                        b_to_c_data: list = xin_tea.qry_order_b_to_c_count_by_split_before_order_no(per_qry)
                        self.error_num_for_error_arrival_area += len(b_to_c_data)
                        self.error_msg_for_error_arrival_area += f"訂單編號: {per_qry}該明細之生產廠商【{generate_vendor}】和到貨區間關鍵字【{order_earliest_date}】無到貨區間資料\n"
                        self.error_order_no_for_error_arrival_area.append(per_qry)
            result: bool = xin_tea.upd_order_manage_summary_b_to_c_and_delete_error_arrival_area(upd_data, delete_param)
            return result
    
    def __determined_arrival_area(self, column: str, split_string: str) -> dict:
        """
        處理到貨區間
        :param column: 到貨區間
        """
        arrival_area_split: str = ''
        if '到貨區間' in column:
            # 代表有到貨區間要處理(切出平台規格第一個日期)
            arrival_area_split: str = column.split('到貨區間')[1].split(split_string)[0].strip()
            # 只保留數字、英文字母、斜線、減號和中文字
            arrival_area_split = re.sub(r'[^A-Za-z0-9\u4e00-\u9fff/-]', '', arrival_area_split)
            # 如果是區間格式(例如: 1/1-1/3)，則取出第一個日期
            if '-' in arrival_area_split:
                arrival_area_split = arrival_area_split.split('-')[0].strip()
            # 去除特殊字元，只保留數字、字母、斜線和中文字元
            arrival_area_split = re.sub(r'[^\w\u4e00-\u9fff/]', '', arrival_area_split)
        print('arrival_area_split', arrival_area_split)
        return {'arrival_area_split': arrival_area_split}
    
    
    def __determined_generate_vendor_v2(self, order_data: list, order_date: str) -> dict:
        """
        處理生產廠商(版本2)
        :param order_data: list 訂單資料
        :param order_date: str 訂單日期
        """
        # 先查詢所有廠商條件(以優先權最大的廠商為主)
        vendor_condition: list = xin_tea.qry_vendor_condition()
        vendor: str = ''
        can_generate_vendor: list = []
        
        # 先計算各母單的總金額
        order_totals = {}
        for per_order in order_data:
            split_order = per_order.get('split_berfore_order_no')
            if split_order not in order_totals:
                order_money = 0
                for per_sub_order in order_data:
                    if per_sub_order.get('split_berfore_order_no') == split_order:
                        # 貨幣處理
                        currency = 'TWD'  # 預設值
                        if self.e_commerce_platform == 'shopline':
                            currency = per_sub_order.get('貨幣', 'TWD')
                        elif self.e_commerce_platform == 'pinkoi':
                            currency = per_sub_order.get('貨幣別', 'TWD')
                        elif self.e_commerce_platform == 'line 禮物':
                            currency = 'TWD'
                        
                        unit_price = 1
                        if currency not in ['TWD', None]:
                            currency_data = jw_common.qry_currency(currency)
                            unit_price = float(currency_data[0]['spot_exchange_rate_bank_selling_rate'])
                        
                        order_money += round_v3(float(per_sub_order.get('order_money') or 0) * unit_price, 0)
                
                order_totals[split_order] = order_money
        print('order_totals', order_totals)
        # 檢查每個廠商條件
        for per_vendor in vendor_condition:
            print('per_vendor', per_vendor)
            if per_vendor.get('pri_seq') == 0:
                can_generate_vendor.append({'vendor': per_vendor.get('vendor'), 'row_number': per_vendor.get('row_number')})
                continue
            
            vendor_matches = True
            checked_split_orders = set()  # 避免重複檢查同一母單
            
            for per_order in order_data:
                split_order = per_order.get('split_berfore_order_no')
                
                # 如果這個母單已經檢查過，跳過
                if split_order in checked_split_orders:
                    continue
                checked_split_orders.add(split_order)
                # 1. 物流方式檢查（檢查該母單下所有明細的物流方式）
                logistics_match = True
                for per_sub_order in order_data:
                    if per_sub_order.get('split_berfore_order_no') == split_order:
                        logistics_method = per_sub_order.get('logistics_method')
                        # 清除所有首尾空白（包含全形空格、tab、換行）
                        logistics_method = re.sub(r'[\s\u3000]+', '', str(logistics_method))
                        logistics_list_ch = per_vendor.get('logistics_list_ch', '')
                        # 清除所有首尾空白（包含全形空格、tab、換行）
                        logistics_list_ch = re.sub(r'[\s\u3000]+', '', str(logistics_list_ch))
                        print('logistics_method', logistics_method)
                        print('logistics_list_ch', logistics_list_ch)
                        if logistics_method not in logistics_list_ch:
                            logistics_match = False
                            break
                print('logistics_match', logistics_match)
                if not logistics_match:
                    vendor_matches = False
                    break
                
                # 2. 訂單金額符合標準
                order_money = order_totals[split_order]
                money_condition = per_vendor.get('order_money')
                money_match = False
                print('money_match', money_condition)
                # 解析條件並進行判斷
                if money_condition:
                    money_condition = money_condition.strip()
                    
                    # 情況1: 上下限 <99,>5000
                    if ('<' in money_condition and '>' in money_condition and ',' in money_condition):
                        print('情況1: 上下限')
                        conditions = money_condition.split(',')
                        
                        for condition in conditions:
                            condition = condition.strip()
                            
                            if '<' in condition:
                                threshold = float(condition.replace('<', '').strip())
                                if order_money < threshold:
                                    money_match = True
                            elif '>' in condition:
                                threshold = float(condition.replace('>', '').strip())
                                if order_money > threshold:
                                    money_match = True
                    # 情況2: 小於某金額 (<5000)
                    elif '<' in money_condition and '>' not in money_condition:
                        print('情況2: 小於某金額')
                        threshold = float(money_condition.replace('<', '').strip())
                        money_match = order_money < threshold
                    
                    # 情況3: 大於某金額 (>5000)
                    elif '>' in money_condition and '<' not in money_condition:
                        print('情況3: 大於某金額')
                        threshold = float(money_condition.replace('>', '').strip())
                        money_match = order_money > threshold
                    
                    # 情況4: 金額範圍 (5000-10000)
                    elif '-' in money_condition and '<' not in money_condition and '>' not in money_condition:
                        print('情況4: 金額範圍')
                        min_val, max_val = map(float, money_condition.split('-'))
                        money_match = min_val <= order_money <= max_val
                    
                    # 情況5: 精確金額
                    else:
                        print('情況5: 精確金額')
                        try:
                            threshold = float(money_condition)
                            money_match = order_money == threshold
                        except ValueError:
                            money_match = False
                else:
                    money_match = True
                
                if not money_match:
                    vendor_matches = False
                    break
                
                # 3. 檢查該母單下所有明細的料件是否都在廠商的料件對照表中
                item_matches = True
                for per_sub_order in order_data:
                    if per_sub_order.get('split_berfore_order_no') == split_order:
                        item_exist = xin_tea.qry_vendor_item(per_vendor.get('vendor'), per_sub_order.get('item'))
                        if not item_exist:
                            item_matches = False
                            break
                print('item_matches', item_matches)
                if not item_matches:
                    vendor_matches = False
                    break
                
                # 4. 啟用日檢查
                start_date_str = per_vendor.get('start_date')
                if isinstance(start_date_str, str):
                    if '-' in start_date_str:
                        start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d")
                    elif '/' in start_date_str:
                        start_date_obj = datetime.strptime(start_date_str, "%Y/%m/%d")
                    else:
                        raise ValueError(f"無法識別的日期格式: {start_date_str}")
                
                # 檢查該母單是否有到貨區間
                has_arrival_area = False
                for per_sub_order in order_data:
                    if per_sub_order.get('split_berfore_order_no') == split_order:
                        arrival_area_split = per_sub_order.get('arrival_area_split')
                        print('arrival_area_split', arrival_area_split)
                        if arrival_area_split and len(arrival_area_split) > 0:
                            has_arrival_area = True
                            
                            order_date_obj = per_sub_order.get('e_commerce_platform_order_date')
                            if '/' in str(order_date_obj):
                                order_date_obj = datetime.strptime(str(order_date_obj), "%Y/%m/%d")
                            elif '-' in str(order_date_obj):
                                order_date_obj = datetime.strptime(str(order_date_obj), "%Y-%m-%d")
                            
                            order_month = order_date_obj.month
                            order_day = order_date_obj.day
                            current_year = datetime.now().year
                            
                            arrival_month, arrival_day = map(int, arrival_area_split.split('/'))
                            
                            if (arrival_month > order_month) or (arrival_month == order_month and arrival_day >= order_day):
                                arrival_date_obj = datetime(current_year, arrival_month, arrival_day)
                            else:
                                arrival_date_obj = datetime(current_year + 1, arrival_month, arrival_day)
                            
                            print('start_date_obj', start_date_obj)
                            print('arrival_date_obj', arrival_date_obj)
                            # 如果啟用日大於該訂單到貨區間日期，因為還沒啟用所以不能給該廠商處理
                            if start_date_obj > arrival_date_obj:
                                vendor_matches = False
                                break
                    
                    if not vendor_matches:
                        break
            
            # 所有條件都符合
            if vendor_matches:
                can_generate_vendor.append({'vendor': per_vendor.get('vendor'), 'row_number': per_vendor.get('row_number')})
        print('can_generate_vendor', can_generate_vendor)
        # 根據優先順序選擇廠商
        if can_generate_vendor:
            vendor = can_generate_vendor[0]  # 第一個就是優先順序最高的
        else:
            vendor = {'vendor': '', 'row_number': ''}
        print('order_data', order_data[0]['split_berfore_order_no'])
        print('vendor', vendor)
        return vendor
                
    @staticmethod
    def __determined_consume_warehouse(vendor_id: str) -> list:
        """
        處理耗料倉別
        :param vendor_id: 生產廠商代碼
        """
        vendor_data: list = xin_tea.qry_vendor_consume_warehouse(vendor_id)
        consume_warehouse: str = ''
        try:
            consume_warehouse = vendor_data[0]['consume_warehouse']
        except:
            pass
        return consume_warehouse
    
    def __determined_order_generate_date(self, generate_vendor: str, arrival_area_split: str, order_no: str, order_status: str, remark: str,
                                         logistics_method: str):
        """
        處理製作許可日/最早到貨日/最早出廠日
        :param generate_vendor: 生產廠商
        :param arrival_area_split: 到貨區間
        :param order_no: 訂單號碼
        :param remark: 備註
        :param order_status: 訂單狀態
        :param logistics_method: 物流方式
        """
        datetime_now: datetime = datetime.now()
        today = datetime_now.strftime("%Y/%m/%d")
        today_date = datetime.strptime(today, "%Y/%m/%d")
        order_generate_date: str = ''
        earliest_arrival_date: str = ''
        earliest_factory_date: str = ''
        to_generate_vendor: str = ''
        #if order_status in ['已取消', '確認中', '尚未付款']:
        #    cal_order_generate_date = '先不用填'
        #else:
        if arrival_area_split:
            # 預購商品(依廠商+到貨區間+物流找出最早到貨日)
            # 清除所有空白（包含中間、首尾、全形空格、tab、換行）
            logistics_method = re.sub(r'[\s\u3000]+', '', str(logistics_method))
            print('logistics_method', logistics_method)
            vendor_arrival_area: list = xin_tea.qry_vendor_earliest_arrival_date(generate_vendor, arrival_area_split, logistics_method)
            # 如果沒有找到改用無物流方式重新找一次
            #if not vendor_arrival_area:
            #    vendor_arrival_area: list = xin_tea.qry_vendor_earliest_arrival_date(generate_vendor, arrival_area_split, '')
            if vendor_arrival_area:
                to_generate_vendor = vendor_arrival_area[0]['to_generate_vendor']
                print('製作許可日', vendor_arrival_area[0]['to_order_generate_date'])
                print('最早可出廠日', vendor_arrival_area[0]['earliest_factory_date'])
                print('最早到貨日', vendor_arrival_area[0]['earliest_arrival_date'])
                # 3個狀況 依現在時間比對
                # 1. 製作許可日,出廠日跟最早到貨日之前
                if datetime_now < datetime.strptime(vendor_arrival_area[0]['to_order_generate_date'], "%Y/%m/%d"):
                    print('1. 製作許可日之前')
                    order_generate_date = vendor_arrival_area[0]['to_order_generate_date']
                    earliest_arrival_date = vendor_arrival_area[0]['earliest_arrival_date']
                    earliest_factory_date = vendor_arrival_area[0]['earliest_factory_date']
                # 2. 製作許可日之後，但在最早到貨日之前
                elif datetime_now >= datetime.strptime(vendor_arrival_area[0]['to_order_generate_date'], "%Y/%m/%d") and \
                datetime_now <= datetime.strptime(vendor_arrival_area[0]['earliest_arrival_date'], "%Y/%m/%d"):
                    print('2. 製作許可日之後，最早到貨日之前')
                    order_generate_date = datetime_now.strftime("%Y/%m/%d")
                    # 如果製作許可日為假日，則順延下一個工作天
                    is_holiday = jw_common.qry_is_holiday(order_generate_date)
                    if is_holiday:
                        order_generate_date = next_working_day(order_generate_date)
                    earliest_arrival_date = vendor_arrival_area[0]['earliest_arrival_date']
                    earliest_factory_date = vendor_arrival_area[0]['earliest_factory_date']
                # 3. 最早到貨日之後
                else:
                    print('3. 最早到貨日之後')
                    order_generate_date = datetime_now.strftime("%Y/%m/%d")
                    # 如果製作許可日為假日，則順延下一個工作天
                    is_holiday = jw_common.qry_is_holiday(order_generate_date)
                    if is_holiday:
                        order_generate_date = next_working_day(order_generate_date)
                    
                    # 將字串轉回 datetime 物件來計算
                    order_generate_date_obj = datetime.strptime(order_generate_date, "%Y/%m/%d")
                    earliest_arrival_date = (order_generate_date_obj + timedelta(days=1)).strftime("%Y/%m/%d")
                    earliest_factory_date = order_generate_date
                print('預購商品到貨區間')
                print(str({'order_generate_date': order_generate_date, 'earliest_arrival_date': earliest_arrival_date,
                            'earliest_factory_date': earliest_factory_date, 'to_generate_vendor': to_generate_vendor}))
            """
            else:
                # 找不到對應的廠商到貨區間也視為非預購商品
                order_generate_date = str(today_date.strftime("%Y/%m/%d"))
                if order_generate_date != '':
                    try:
                        order_generate_date_date = datetime.strptime(order_generate_date, "%Y/%m/%d")
                    except:
                        order_generate_date_date = datetime.strptime(order_generate_date, "%Y-%m-%d %H:%M:%S")
                    
                    # 直接加一天
                    next_day = (order_generate_date_date + timedelta(days=1)).strftime("%Y/%m/%d")
                    earliest_arrival_date: str = str(next_day)
                try:
                    earliest_factory_date = next_working_day(datetime.strptime(earliest_arrival_date, "%Y/%m/%d"), 2)
                except:
                    earliest_factory_date = next_working_day(datetime.strptime(earliest_arrival_date, "%Y-%m-%d %H:%M:%S"), 2)
                earliest_factory_date = earliest_factory_date.strftime("%Y/%m/%d")
            """
        else:
            # 非預購商品
            # today(今天日期)
            order_generate_date = str(today_date.strftime("%Y/%m/%d"))
            # 最早可出廠日改為今天
            earliest_factory_date = order_generate_date
            if order_generate_date != '':
                try:
                    order_generate_date_date = datetime.strptime(order_generate_date, "%Y/%m/%d")
                except:
                    order_generate_date_date = datetime.strptime(order_generate_date, "%Y-%m-%d %H:%M:%S")
                
                # 直接加一天
                next_day = (order_generate_date_date + timedelta(days=1)).strftime("%Y/%m/%d")
                earliest_arrival_date: str = str(next_day)

        print(str({'order_generate_date': order_generate_date, 'earliest_arrival_date': earliest_arrival_date,
                    'earliest_factory_date': earliest_factory_date, 'to_generate_vendor': to_generate_vendor}))
        return {'order_generate_date': order_generate_date, 'earliest_arrival_date': earliest_arrival_date,
                'earliest_factory_date': earliest_factory_date, 'to_generate_vendor': to_generate_vendor}
        
    def __determined_is_check_remark(self, order_remark: str, shipping_remark: str, cus1: str, order_status: str) -> str:
        """
        處理是否檢查備註欄訊息
        :param order_remark: 訂單備註
        :param shipping_remark: 出貨備註
        :param cus1: 自訂訂單欄位 2 (出貨是否需要附上訂單明細)
        """
        is_check_remark: str = ''
        remark: str = str(order_remark) + str(shipping_remark) + str(cus1)
        if len(remark) > 0:
            if (remark == '-' or remark == '【訂單備註】【出貨備註】' or remark == '【訂單備註】' or remark == '【出貨備註】'):
                is_check_remark = ''
            else:
                # 抓是否備註欄判斷是否可不用需確認
                allow_remark: list = xin_tea.qry_is_remark_check_condition()
                allow_remark_texts = [per_allow.get('text') for per_allow in allow_remark]

                # 清理remark，移除格式標籤
                clean_remark = remark.replace('【訂單備註】', '').replace('【出貨備註】', '').strip()

                if clean_remark and clean_remark != '-':
                    # 複製一份用來檢查
                    remaining_remark = clean_remark
                    
                    # 移除所有允許的關鍵字
                    for allow_text in allow_remark_texts:
                        if allow_text in remaining_remark:
                            remaining_remark = remaining_remark.replace(allow_text, '')
                    
                    # 清理剩餘內容的空白字符
                    remaining_remark = remaining_remark.strip()
                    
                    # 如果移除允許的關鍵字後還有其他內容，則需要確認
                    if remaining_remark:
                        is_check_remark = '需確認'
                    else:
                        is_check_remark = ''
                else:
                    is_check_remark = ''
            #if order_status in ['已取消', '處理中', '尚未付款']:
            #    is_check_remark = '暫不處理'
            #else:
            #    is_check_remark = '需確認'
        else:
            is_check_remark = ''
        return is_check_remark
    
    def __check_order_can_import(self) -> str | list:
        """檢查是否可以匯入"""
        error_message: str = ''
        check_order_no: list = []
        error_order_no: list = []
        check_split_order_error: list = []
        check_status_error: list = []
        no_import_num: int = 0
        item_exist_num: int = 0
        error_item_category: int = 0
        repeat_upload_error: int = 0
        no_logistics_num: int = 0
        item_must_bom_actual_no_bom_num: int = 0
        item_no_set_reference_num: int = 0
        no_currency_num: int = 0
        split_order_error: int = 0
        # 先檢查訂單號碼資料是否已存在(判斷是否是新資料)
        for per_detail in self.new_order:
            # 是否為新增
            if self.e_commerce_platform == 'line 禮物':
                order_no: str = str(per_detail.get('訂單編號'))
                new_data: list = xin_tea.qry_order_no(str(order_no))
                # 有資料檢查
                if len(new_data) != 0:
                    if order_no not in check_order_no:
                        import_data: list = xin_tea.qry_order_no_can_import(order_no)
                        # 當前訂單管理總表的訂單狀態不符合可重新匯入的狀態
                        if import_data:
                            # 特殊處理失效狀態(2.0, 3.1, 4.1)，需該平台訂單單號整批明細皆是失效(2.0, 3.1, 4.1)才可以重新匯入
                            if import_data[0]['status'] in ['2.0', '3.1', '4.1']:
                                check_order_status: list = xin_tea.qry_order_no(order_no)
                                check_two_can_import: bool = True
                                for per_check in check_order_status:
                                    if per_check.get('status') not in ['2.0', '3.1', '4.1']:
                                        check_two_can_import = False
                                        break
                                if not check_two_can_import:
                                    error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                                    error_order_no.append(order_no)
                                    repeat_upload_error += 1
                                    check_status_error.append(order_no)
                                    continue
                            #else:
                            #    error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                            #    error_order_no.append(order_no)
                        else:
                            # 無資料代表為不符合可重新匯入的狀態
                            error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                            error_order_no.append(order_no)
                            check_status_error.append(order_no)
                            repeat_upload_error += 1
                            continue
                        check_order_no.append(order_no) 
                # 匯入excel的訂單狀態需符合可匯入的狀態
                status: str = per_detail.get('訂單狀態')
                if status != '已付款':
                    error_message += f"訂單號碼：【{order_no}】狀態為【{status}】不符合可匯入的狀態\n"
                    check_status_error.append(order_no)
                    error_order_no.append(order_no)
                    no_import_num += 1
                    continue
                if (status == '已付款' and (len(str(per_detail.get('訂單確認日期'))) == 0 or str(per_detail.get('訂單確認日期')) == '-')):
                    error_message += f"訂單號碼：【{order_no}】狀態為【{status}】但訂單確認日期為空值\n" 
                    error_order_no.append(order_no)
                    no_import_num += 1
                    continue
                # 檢查料件的料件類別是否符合
                item_id: str = str(per_detail.get('規格管理代碼'))
                item_data: list = xin_tea.qry_item_data(item_id)
                if len(item_data) == 0:
                    error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】不存在於料件主檔\n"
                    error_order_no.append(order_no)
                    item_exist_num += 1
                    continue
                else:
                    # 檢查料件類別是否符合
                    item_category: list = xin_tea.qry_item_category_can_import(item_data[0]['category'])
                    if not item_category:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_data[0]['category']}】不符合可匯入的類別\n"
                        error_order_no.append(order_no)
                        error_item_category += 1
                        continue
                    # 檢查料號是否有設定料號參照表
                    item_reference: list = xin_tea.qry_item_reference(item_id)
                    if not item_reference:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】無料號參照表設定\n"
                        error_order_no.append(order_no)
                        item_no_set_reference_num += 1
                        continue
                # 料件類別為需要BOM的料件，則需檢查是否有BOM
                item_category: str = item_data[0]['category']
                # 查詢是否為需要BOM的料件類別
                must_bom: list = xin_tea.qry_item_category_must_bom(item_category)
                if must_bom:
                    # 需要BOM的料件，則需檢查是否有BOM
                    bom: str = item_data[0]['bom']
                    if len(bom) == 0:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_category}】為需要BOM的料件，但無BOM資料\n"
                        error_order_no.append(order_no)
                        item_must_bom_actual_no_bom_num += 1
                        continue
                # 檢查物流名單是否存在於物流名單
                logistics_method: str = per_detail.get('配送方式')
                # 清除所有空白（包含中間、首尾、全形空格、tab、換行）
                logistics_method = re.sub(r'[\s\u3000]+', '', str(logistics_method))
                exist_logistics: list = xin_tea.qry_logistics_method_exist(logistics_method)
                if not exist_logistics:
                    error_message += f"訂單號碼：【{order_no}】物流方式：【{logistics_method}】不存在於物流名單\n"
                    error_order_no.append(order_no)
                    no_logistics_num += 1
                    continue
                # 拆單錯誤
                if order_no in error_order_no:
                    error_message += f"訂單號碼：【{order_no}】拆單錯誤\n"
                    error_order_no.append(order_no)
                    split_order_error += 1
                    if order_no not in check_split_order_error:
                        check_split_order_error.append(order_no)
                    continue
            elif self.e_commerce_platform == 'shopline':
                order_no: str = per_detail.get('訂單號碼')[:18]
                new_data: list = xin_tea.qry_order_no(order_no)
                # 無資料代表為新資料
                if len(new_data) != 0:
                    if order_no not in check_order_no:
                        import_data: list = xin_tea.qry_order_no_can_import(order_no)
                        # 當前訂單管理總表的訂單狀態不符合可重新匯入的狀態
                        if not import_data:
                            # 無資料代表為不符合可重新匯入的狀態
                            error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                            error_order_no.append(order_no)
                            check_status_error.append(order_no)
                            repeat_upload_error += 1
                            continue
                        else:
                            # 特殊處理(2.0, 3.1, 4.1)狀態，需該平台訂單單號整批明細皆是(2.0, 3.1, 4.1)才可以重新匯入
                            if import_data[0]['status'] in ['2.0', '3.1', '4.1']:
                                check_order_status: list = xin_tea.qry_order_no(order_no)
                                check_two_can_import: bool = True
                                for per_check in check_order_status:
                                    if per_check.get('status') not in ['2.0', '3.1', '4.1']:
                                        check_two_can_import = False
                                        break
                                if not check_two_can_import:
                                    error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                                    error_order_no.append(order_no)
                                    check_status_error.append(order_no)
                                    repeat_upload_error += 1
                                    continue
                            else:
                                error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                                error_order_no.append(order_no)
                                check_status_error.append(order_no)
                                repeat_upload_error += 1
                                continue
                        check_order_no.append(order_no)
                # 匯入excel的訂單狀態需符合可匯入的狀態
                status: str = per_detail.get('訂單狀態')
                if status not in ['已確認']:
                    error_message += f"訂單號碼：【{order_no}】狀態為【{status}】不符合可匯入的狀態\n"
                    error_order_no.append(order_no)
                    check_status_error.append(order_no)
                    no_import_num += 1
                    continue
                # 檢查料件的料件類別是否符合
                item_id: str = str(per_detail.get('商品貨號'))
                item_data: list = xin_tea.qry_item_data(item_id)
                if len(item_data) == 0:
                    error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】不存在於料件主檔\n"
                    error_order_no.append(order_no)
                    item_exist_num += 1
                    continue
                else:
                    # 檢查料件類別是否符合
                    item_category: list = xin_tea.qry_item_category_can_import(item_data[0]['category'])
                    if not item_category:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_data[0]['category']}】不符合可匯入的類別<br>"
                        error_order_no.append(order_no)
                        error_item_category += 1
                        continue
                    # 檢查料號是否有設定料號參照表
                    item_reference: list = xin_tea.qry_item_reference(item_id)
                    if not item_reference:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】無料號參照表設定\n"
                        error_order_no.append(order_no)
                        item_no_set_reference_num += 1
                        continue
                # 料件類別為需要BOM的料件，則需檢查是否有BOM
                item_category: str = item_data[0]['category']
                # 查詢是否為需要BOM的料件類別
                must_bom: list = xin_tea.qry_item_category_must_bom(item_category)
                if must_bom:
                    # 需要BOM的料件，則需檢查是否有BOM
                    bom: str = item_data[0]['bom']
                    if len(bom) == 0:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_category}】為需要BOM的料件，但無BOM資料\n"
                        error_order_no.append(order_no)
                        item_must_bom_actual_no_bom_num += 1
                        continue
                # 檢查物流名單是否存在於物流名單
                logistics_method: str = per_detail.get('送貨方式')
                # 清除所有空白（包含中間、首尾、全形空格、tab、換行）
                logistics_method = re.sub(r'[\s\u3000]+', '', str(logistics_method))
                exist_logistics: list = xin_tea.qry_logistics_method_exist(logistics_method)
                if not exist_logistics:
                    error_message += f"訂單號碼：【{order_no}】物流方式：【{logistics_method}】不存在於物流名單\n"
                    error_order_no.append(order_no)
                    no_logistics_num += 1
                    continue
                # 檢查貨幣是否有值
                currency: str = per_detail.get('貨幣')
                if len(currency) == 0 or currency == '-':
                    error_message += f"訂單號碼：【{order_no}】貨幣為空值\n"
                    error_order_no.append(order_no)
                    no_currency_num += 1
                    continue
                # 拆單錯誤
                if order_no in error_order_no:
                    error_message += f"訂單號碼：【{order_no}】拆單錯誤\n"
                    error_order_no.append(order_no)
                    if order_no not in check_split_order_error:
                        check_split_order_error.append(order_no)
                    split_order_error += 1
                    continue
            elif self.e_commerce_platform == 'pinkoi':
                order_no: str = per_detail.get('訂單編號')
                new_data: list = xin_tea.qry_order_no(order_no)
                # 無資料代表為新資料
                #if len(new_data) == 0:
                #    continue
                if len(new_data) != 0:
                    if order_no not in check_order_no:
                        import_data: list = xin_tea.qry_order_no_can_import(order_no)
                        # 當前訂單管理總表的訂單狀態不符合可重新匯入的狀態
                        if import_data:
                            # 特殊處理失效狀態(2.0, 3.1, 4.1)，需該平台訂單單號整批明細皆是2.0才可以重新匯入
                            if import_data[0]['status'] in ['2.0', '3.1', '4.1']:
                                check_order_status: list = xin_tea.qry_order_no(order_no)
                                check_two_can_import: bool = True
                                for per_check in check_order_status:
                                    if per_check.get('status') not in ['2.0', '3.1', '4.1']:
                                        check_two_can_import = False
                                        break
                                if not check_two_can_import:
                                    error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                                    error_order_no.append(order_no)
                                    check_status_error.append(order_no)
                                    repeat_upload_error += 1
                                    continue
                            else:
                                error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                                error_order_no.append(order_no)
                                check_status_error.append(order_no)
                                repeat_upload_error += 1
                                continue
                        else:
                            # 無資料代表為不符合可重新匯入的狀態
                            error_message += f"訂單號碼：【{order_no}】不符合可重新匯入狀態\n"
                            error_order_no.append(order_no)
                            check_status_error.append(order_no)
                            repeat_upload_error += 1
                            continue
                        check_order_no.append(order_no)
                # 匯入excel的訂單狀態需符合可匯入的狀態
                status: str = per_detail.get('訂單類型')
                if status not in ['待出貨', '尚未付款']:
                    error_message += f"訂單號碼：【{order_no}】狀態為【{status}】不符合可匯入的狀態\n"
                    check_status_error.append(order_no)
                    error_order_no.append(order_no)
                    no_import_num += 1
                    continue
                # 檢查料件的料件類別是否符合
                item_id: str = str(per_detail.get('SKU'))
                item_data: list = xin_tea.qry_item_data(item_id)
                if len(item_data) == 0:
                    error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】不存在於料件主檔\n"
                    error_order_no.append(order_no)
                    item_exist_num += 1
                    continue
                else:
                    # 檢查料件類別是否符合
                    item_category: list = xin_tea.qry_item_category_can_import(item_data[0]['category'])
                    if not item_category:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_data[0]['category']}】不符合可匯入的類別<br>"
                        error_order_no.append(order_no)
                        error_item_category += 1
                        continue
                    # 檢查料號是否有設定料號參照表
                    item_reference: list = xin_tea.qry_item_reference(item_id)
                    if not item_reference:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】無料號參照表設定\n"
                        error_order_no.append(order_no)
                        item_no_set_reference_num += 1
                        continue
                """
                料件類別為需要BOM的料件，則需檢查是否有BOM
                """
                item_category: str = item_data[0]['category']
                # 查詢是否為需要BOM的料件類別
                must_bom: list = xin_tea.qry_item_category_must_bom(item_category)
                if must_bom:
                    # 需要BOM的料件，則需檢查是否有BOM
                    bom: str = item_data[0]['bom']
                    if len(bom) == 0:
                        error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_category}】為需要BOM的料件，但無BOM資料\n"
                        error_order_no.append(order_no)
                        item_must_bom_actual_no_bom_num += 1
                        continue
                # 檢查物流名單是否存在於物流名單
                logistics_method: str = per_detail.get('運送方式')
                # 清除所有空白（包含中間、首尾、全形空格、tab、換行）
                logistics_method = re.sub(r'[\s\u3000]+', '', str(logistics_method))
                exist_logistics: list = xin_tea.qry_logistics_method_exist(logistics_method)
                if not exist_logistics:
                    error_message += f"訂單號碼：【{order_no}】物流方式：【{logistics_method}】不存在於物流名單\n"
                    error_order_no.append(order_no)
                    no_logistics_num += 1
                    continue
                # 檢查貨幣是否有值
                currency: str = per_detail.get('貨幣別')
                if len(currency) == 0 or currency == '-':
                    error_message += f"訂單號碼：【{order_no}】貨幣為空值\n"
                    error_order_no.append(order_no)
                    no_currency_num += 1
                    continue
                # 拆單錯誤
                if order_no in error_order_no:
                    error_message += f"訂單號碼：【{order_no}】拆單錯誤\n"
                    error_order_no.append(order_no)
                    if order_no not in check_split_order_error:
                        check_split_order_error.append(order_no)
                    split_order_error += 1
                    continue
        return error_message, error_order_no, no_import_num, error_item_category, repeat_upload_error, item_exist_num, no_logistics_num, item_must_bom_actual_no_bom_num, item_no_set_reference_num, no_currency_num, split_order_error, check_split_order_error

    def __determined_status(self, order_remark: str, shipping_remark: str, cus1: str, order_status: str) -> str:
        """
        處理狀態
        :param order_remark: 訂單備註
        :param shipping_remark: 出貨備註
        :param cus1: 自訂訂單欄位 2 (出貨是否需要附上訂單明細)
        """
        remark: str = str(order_remark) + str(shipping_remark) + str(cus1)       
        # 如果備註為空或只有 '-'，直接返回 '2'
        if not remark or remark == '-':
            return '2'
        
        # 抓是否備註欄判斷是否可不用需確認
        allow_remark: list = xin_tea.qry_is_remark_check_condition()
        allow_remark_texts = [per_allow.get('text') for per_allow in allow_remark]

        # 清理remark，移除格式標籤
        clean_remark = remark.replace('【訂單備註】', '').replace('【出貨備註】', '').strip()

        # 如果清理後為空或只有 '-'，返回 '2'
        if not clean_remark or clean_remark == '-':
            return '2'
        
        # 複製一份用來檢查
        remaining_remark = clean_remark
        
        # 移除所有允許的關鍵字
        for allow_text in allow_remark_texts:
            if allow_text in remaining_remark:
                remaining_remark = remaining_remark.replace(allow_text, '')
        
        # 清理剩餘內容的空白字符
        remaining_remark = remaining_remark.strip()
        
        # 如果移除允許的關鍵字後還有其他內容，則需要確認
        if remaining_remark:
            return '1'  # 待確認
        else:
            return '2'  # 已確認可拋單
        
    def previous_working_day(self, date_obj):
        """
        取得前一個工作日
        """
        previous_day = date_obj - timedelta(days=1)
        
        # 如果是週末，繼續往前推
        while previous_day.weekday() in [5, 6]:  # 5=週六, 6=週日
            previous_day = previous_day - timedelta(days=1)
        
        return previous_day