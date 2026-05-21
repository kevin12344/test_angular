import pandas as pd
import time, math
import gspread.exceptions
from datetime import datetime
from google.api_core import exceptions as google_exceptions
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.db_process.xin_tea.order_import import main as xin_tea
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea_order_manage_summary_b_to_c

class UpdateBtoBGsSq:
    def __init__(self, sq_gs_url: str, user_name: str):
        self.sq_gs_url: str = sq_gs_url
        self.user_name: str = user_name
        self.order: list = []
        self.company_title: str = ''
        self.project_name: str = ''
        self.customer_data: list = []
        self.order_check_date: str = ''
        self.earliest_arrival_date: str = ''
        self.latest_arrival_date: str = ''
        self.sleep: int = 0
    
    def process_data(self):
        # 1. 檢查規則
        error_msg: str = self.__check_rule()
        if error_msg:
            return error_msg
        # 2. 新增B2B訂單資料
        result: bool = self.__crt_order_manage_summary_b_to_b()
        if result:
            return 'B2B報價單匯入成功'
        return 'B2B報價單匯入失敗'

    def __crt_order_manage_summary_b_to_b(self):
        """新增B2B訂單資料"""
        customer_data: list = self.customer_data
        # 處理成訂單明細
        new_quotation_detail: list = []
        now_date_str: str = datetime.now().strftime("%Y-%m-%d")
        now_date: str = datetime.now().strftime("%Y%m%d")
        customize_bom: list = []
        # 查詢報價單單號處理(抓該gs原有的報價單重新建立序號)
        sq_data: list = xin_tea.qry_order_exist(self.sq_gs_url)
        sq_no: str = sq_data[0]['sq_form_id']
        sq_num = 1
        seq: int = 1
        customize_bom_change: list = []
        spare_item: list = []
        for per_order in self.order:
            quantity: float = 0
            try:
                quantity = float(per_order.get('報價數量') or 0)
            except ValueError:
                pass
            if quantity > 0:
                customized_options = [per_order.get(f'客製化方案#{i}', '') for i in range(1, 9)]
                item_id: str = str(per_order.get('禮盒料號', ''))
                if len(item_id) == 0:
                    continue
                # 新增
                bom: str = ''
                try:
                    bom: str = xin_tea.qry_bom_by_item(item_id)[0]['bom']
                except Exception as e:
                    pass
                item_data: list = xin_tea.qry_item_data_in_item([item_id])
                # 檢查客製化方案#1~#8，只要其中一個不為空值
                customize: str = ''
                is_customize: str = '0'
                has_customized = any(opt for opt in customized_options if opt)
                customize_bom_str: str = ''
                if has_customized:
                    customize = '客製化禮盒' 
                    is_customize = '1'
                    customize_bom_str = f"{sq_no}-{seq}"
                new_quotation_detail.append(
                    (
                        f"{sq_no}-{seq}", '2', '', now_date_str, '', # 客戶窗口慣用聯繫方式 
                        self.sq_gs_url, '', self.order_check_date, self.earliest_arrival_date, self.latest_arrival_date, customer_data[0]['customer_name'], # 客戶簡稱 
                        customer_data[0]['customer_name'], customer_data[0]['customer_uniform_invoice_no'], # 客戶統編
                        customer_data[0]['customer_address'], customer_data[0]['customer_window'], # 客戶窗口
                        customer_data[0]['customer_phone'], customer_data[0]['customer_email'], # 客戶信箱
                        customer_data[0]['payment_term'], customer_data[0]['payment_type'], # 付款方式
                        '', '', '', '', '','', is_customize, '', '', 
                        '', '', '', '', '', '', '', '', '', '', 
                        '', '', '',
                        # 明細
                        item_id, item_data[0]['category'],
                        item_data[0]['item_name'], per_order.get('規格', ''), '', 
                        per_order.get('零售訂價 \n(含稅)'), quantity, 
                        per_order.get('優惠折數'), per_order.get('單件優惠價\n(含稅)'), 
                        per_order.get('小計\n(含稅)'), customize,
                        bom, '', '', '', '', '', '', '', '', '',
                        f"{sq_no}", self.user_name,
                        customize_bom_str, seq, is_customize, '', '0'
                    )
                )
                bom_data: list = []
                if customize == '客製化禮盒':
                    # 查詢原始BOM
                    bom_data = xin_tea.qry_bom_detail_by_item(item_id, bom)
                    for per_pus in customized_options:
                        # 查詢對應之替換料件
                        check_replace: list = xin_tea.qry_customize_item_replace_by_item(str(per_pus))
                        if check_replace:
                            # 替換料件為空值，代表是新增料件
                            origin_customize_item: list = xin_tea.qry_item_data_in_item([str(per_pus)])
                            if check_replace[0]['replace_item'] == '':
                                # 將客製化欄位改為客戶名稱
                                origin_customize_item_name: str = origin_customize_item[0]['item_name']
                                if '此欄位改成客戶名稱' in origin_customize_item_name:
                                    origin_customize_item_name = origin_customize_item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
                                bom_data.append(
                                    {
                                        "item": item_id,
                                        "item_name": item_data[0]['item_name'],
                                        "m_item": item_data[0]['item'],
                                        "m_item_name": item_data[0]['item_name'],
                                        "s_item": origin_customize_item[0]['item'],
                                        "s_item_name": origin_customize_item_name,
                                        "s_item_spec": "",
                                        "origin_use_quantity": 1,
                                        "use_quantity": 1,
                                        "customize_item": '替換料件(純新增)',
                                        "customize_type": '替換料件',
                                    }
                                )
                                # 替換之後的客製料件要再外面訂單增加明細新增(避免展算錯誤)
                                customize_bom_change.append(
                                    (
                                        '', '2', '', now_date_str, '', # 客戶窗口慣用聯繫方式 
                                        self.sq_gs_url, '', self.order_check_date, self.earliest_arrival_date, self.latest_arrival_date, 
                                        customer_data[0]['customer_name'], # 客戶簡稱 
                                        customer_data[0]['customer_name'], customer_data[0]['customer_uniform_invoice_no'], # 客戶統編
                                        customer_data[0]['customer_address'], customer_data[0]['customer_window'], # 客戶窗口
                                        customer_data[0]['customer_phone'], customer_data[0]['customer_email'], # 客戶信箱
                                        customer_data[0]['payment_term'], customer_data[0]['payment_type'], # 付款方式
                                        '', '', '', '', '','', is_customize, '', '', 
                                        '', '', '', '', '', '', '', '', '', '', 
                                        '', '', '',
                                        # 明細
                                        origin_customize_item[0]['item'], origin_customize_item[0]['category'],
                                        origin_customize_item_name, '', '', 
                                        0, quantity, 
                                        '', '', 
                                        '', '',
                                        origin_customize_item[0]['bom'], '', '', '', '', '', '', '', '', '',
                                        f"{sq_no}", self.user_name,
                                        '', '', '0', '', '1'
                                    )
                                )
                            else:
                                # 有替換料件，要將被替換的料件的子件用量(use_quantity)歸0
                                print('有替換料件')
                                origin_customize_item: list = xin_tea.qry_item_data_in_item([str(per_pus)])
                                # 將客製化欄位改為客戶名稱
                                origin_customize_item_name: str = origin_customize_item[0]['item_name']
                                if '此欄位改成客戶名稱' in origin_customize_item_name:
                                    origin_customize_item_name = origin_customize_item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
                                bom_data.append(
                                    {
                                        "item": item_id,
                                        "item_name": item_data[0]['item_name'],
                                        "m_item": item_data[0]['item'],
                                        "m_item_name": item_data[0]['item_name'],
                                        "s_item": origin_customize_item[0]['item'],
                                        "s_item_name": origin_customize_item_name,
                                        "s_item_spec": "",
                                        "customize_item": f"{check_replace[0]['replace_item']}替換料件",
                                        "origin_use_quantity": 1,
                                        "use_quantity": 1,
                                        "customize_type": '替換料件'
                                    }
                                )
                                # 將被替換的料件的子件用量歸0
                                for per_bom in bom_data:
                                    if per_bom.get('s_item') == check_replace[0]['replace_item']:
                                        per_bom['use_quantity'] = 0
                                        per_bom['customize_item'] = f"被料件{check_replace[0]['customize_item']}替換，刪除料件"
                                        per_bom['customize_type'] = '被替換料件'
                                # 替換之後要再外面訂單增加明細扣掉(避免重複展算錯誤)
                                customize_bom_change.append(
                                    (
                                        '', '2', '', now_date_str, '', # 客戶窗口慣用聯繫方式 
                                        self.sq_gs_url, '', self.order_check_date, self.earliest_arrival_date, self.latest_arrival_date,
                                        customer_data[0]['customer_name'], # 客戶簡稱 
                                        customer_data[0]['customer_name'], customer_data[0]['customer_uniform_invoice_no'], # 客戶統編
                                        customer_data[0]['customer_address'], customer_data[0]['customer_window'], # 客戶窗口
                                        customer_data[0]['customer_phone'], customer_data[0]['customer_email'], # 客戶信箱
                                        customer_data[0]['payment_term'], customer_data[0]['payment_type'], # 付款方式
                                        '', '', '', '', '','', is_customize, '', '', 
                                        '', '', '', '', '', '', '', '', '', '', 
                                        '', '', '',
                                        # 明細
                                        origin_customize_item[0]['item'], origin_customize_item[0]['category'],
                                        origin_customize_item_name, '', '', 
                                        0, quantity, 
                                        '', '', 
                                        '', '',
                                        origin_customize_item[0]['bom'], '', '', '', '', '', '', '', '', '',
                                        f"{sq_no}", self.user_name,
                                        '', '', '0', '', '1'
                                    )
                                )
                                replace_item: list = xin_tea.qry_item_data_in_item([str(check_replace[0]['replace_item'])])
                                # 被替換掉的要在外面訂單明細新增一筆數量為負的
                                customize_bom_change.append(
                                    (
                                        '', '2', '', now_date_str, '', # 客戶窗口慣用聯繫方式 
                                        self.sq_gs_url, '', self.order_check_date, self.earliest_arrival_date, self.latest_arrival_date, 
                                        customer_data[0]['customer_name'], # 客戶簡稱 
                                        customer_data[0]['customer_name'], customer_data[0]['customer_uniform_invoice_no'], # 客戶統編
                                        customer_data[0]['customer_address'], customer_data[0]['customer_window'], # 客戶窗口
                                        customer_data[0]['customer_phone'], customer_data[0]['customer_email'], # 客戶信箱
                                        customer_data[0]['payment_term'], customer_data[0]['payment_type'], # 付款方式
                                        '', '', '', '', '','', is_customize, '', '', 
                                        '', '', '', '', '', '', '', '', '', '', 
                                        '', '', '',
                                        # 明細
                                        replace_item[0]['item'], replace_item[0]['category'],
                                        replace_item[0]['item_name'], '', '', 
                                        0, -quantity, 
                                        '', '', 
                                        '', '',
                                        replace_item[0]['bom'], '', '', '', '', '', '', '', '', '',
                                        f"{sq_no}", self.user_name,
                                        '', '', '0', '', '1'
                                    )
                                )
                # 產生客製化BOM
                for j, per_bom in enumerate(bom_data):
                    customize_bom.append(
                        (
                            f"{sq_no}-{seq}-{j+1}", per_bom.get('item'),
                            per_bom.get('m_item'), 
                            per_bom.get('s_item'), per_bom.get('s_item_name'), per_bom.get('s_item_spec'),
                            '', per_bom.get('customize_item'), per_bom.get('origin_use_quantity'), per_bom.get('use_quantity'), 
                            0, f"{sq_no}-{seq}",
                            j+1, per_bom.get('customize_type')
                        )
                    )
                
                # 產生備用料件明細
                customize_qry: str = '客製'
                if customize == '':
                    customize_qry = '標準'
                spare_item_data: list = xin_tea.qry_spare_item(item_id, customize_qry)
                if spare_item_data:
                    for per_spare in spare_item_data:
                        # 依數量決定多幾個備用料件
                        additional_add: float = per_spare.get('full_num_additional_add')
                        additional_num: int = int(quantity // additional_add)
                        spare_item_name: str = per_spare.get('spare_item_name')
                        if '此欄位改成客戶名稱' in spare_item_name:
                            spare_item_name = spare_item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
                        if additional_num > 0:
                            spare_item.append(
                                (
                                    '', '2', '', now_date_str, '', # 客戶窗口慣用聯繫方式 
                                    self.sq_gs_url, '', self.order_check_date, self.earliest_arrival_date, self.latest_arrival_date,
                                    customer_data[0]['customer_name'], # 客戶簡稱 
                                    customer_data[0]['customer_name'], customer_data[0]['customer_uniform_invoice_no'], # 客戶統編
                                    customer_data[0]['customer_address'], customer_data[0]['customer_window'], # 客戶窗口
                                    customer_data[0]['customer_phone'], customer_data[0]['customer_email'], # 客戶信箱
                                    customer_data[0]['payment_term'], customer_data[0]['payment_type'], # 付款方式
                                    '', '', '', '', '','', is_customize, '', '', 
                                    '', '', '', '', '', '', '', '', '', '', 
                                    '', '', '',
                                    # 明細
                                    per_spare.get('spare_item'), per_spare.get('spare_item_category'),
                                    spare_item_name, '', '', 
                                    0, additional_num, 
                                    '', '', 
                                    '', '',
                                    per_spare.get('bom'), '', '', '', '', '', '', '', '', '',
                                    f"{sq_no}", self.user_name,
                                    '', '', '0', item_id, '1'
                                )
                            )
                            # 備用料件也需要加進客製化BOM(子件用量預設1)(客製才需要)
                            if customize_qry == '客製':
                                spare_item_name: str = per_spare.get('spare_item_name')
                                if '此欄位改成客戶名稱' in spare_item_name:
                                    spare_item_name = spare_item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
                                customize_bom.append(
                                    (
                                        f"{sq_no}-{seq}-{len(bom_data)+1}", bom_data[0].get('item'),
                                        bom_data[0].get('m_item'), 
                                        per_spare.get('spare_item'), spare_item_name, '',
                                        '', '備用料件，額外備用量', 0, 0, additional_num,
                                        f"{sq_no}-{seq}",
                                        len(bom_data)+1, '備用料件'
                                    )
                                )
                seq += 1           
        # 客製品訂單明細合併(將同料號資料的數量做加總)
        detail_dicts = []
        if len(customize_bom_change) > 0:
            for detail in customize_bom_change:
                detail_dict = {
                    'order_no': detail[0], 'type': detail[1], 'field2': detail[2], 'date_str': detail[3], 'field4': detail[4],
                    'url': detail[5], 'field6': detail[6], 'field7': detail[7], 'field8': detail[8], 'field9': detail[9],
                    'customer_name': detail[10], 'customer_name2': detail[11], 'uniform_no': detail[12], 'address': detail[13],
                    'window': detail[14], 'phone': detail[15], 'email': detail[16], 'payment_term': detail[17], 'payment_type': detail[18],
                    'field19': detail[19], 'field20': detail[20], 'field21': detail[21], 'field22': detail[22], 'field23': detail[23],
                    'field24': detail[24], 'is_customize': detail[25], 'field26': detail[26], 'field27': detail[27], 'field28': detail[28],
                    'field29': detail[29], 'field30': detail[30], 'field31': detail[31], 'field32': detail[32], 'field33': detail[33],
                    'field34': detail[34], 'field35': detail[35], 'field36': detail[36], 'field37': detail[37], 'field38': detail[38],
                    'field39': detail[39], 'field40': detail[40],
                    # 明細欄位
                    'item': detail[41], 'category': detail[42], 'item_name': detail[43], 'field44': detail[44], 'field45': detail[45],
                    'unit_price': detail[46], 'quantity': detail[47], 'field48': detail[48], 'field49': detail[49], 'field50': detail[50],
                    'customize': detail[51], 'bom': detail[52], 'field53': detail[53], 'field54': detail[54], 'field55': detail[55],
                    'field56': detail[56], 'field57': detail[57], 'field58': detail[58], 'field59': detail[59], 'field60': detail[60],
                    'field61': detail[61], 'sq_no': detail[62], 'user_name': detail[63], 'customize_bom_str': detail[64], 
                    'seq': detail[65], 'is_customize_end': detail[66] if len(detail) > 66 else '0',  # 新增的欄位
                    'spare_item': detail[67] if len(detail) > 67 else '',  # 新增的 spare_item 欄位
                    'field68': detail[68] if len(detail) > 68 else ''  # 新增的第68個欄位
                }
                detail_dicts.append(detail_dict)

            # 建立 DataFrame
            df = pd.DataFrame(detail_dicts)

            # 按料號(item)分組，對數量(quantity)做加總，其餘欄位取第一個值
            grouped_df = df.groupby('item').agg({
                'quantity': 'sum',  # 數量加總
                # 其餘欄位都取第一個值
                'order_no': 'first', 'type': 'first', 'field2': 'first', 'date_str': 'first', 'field4': 'first',
                'url': 'first', 'field6': 'first', 'field7': 'first', 'field8': 'first', 'field9': 'first',
                'customer_name': 'first', 'customer_name2': 'first', 'uniform_no': 'first', 'address': 'first',
                'window': 'first', 'phone': 'first', 'email': 'first', 'payment_term': 'first', 'payment_type': 'first',
                'field19': 'first', 'field20': 'first', 'field21': 'first', 'field22': 'first', 'field23': 'first',
                'field24': 'first', 'is_customize': 'first', 'field26': 'first', 'field27': 'first', 'field28': 'first',
                'field29': 'first', 'field30': 'first', 'field31': 'first', 'field32': 'first', 'field33': 'first',
                'field34': 'first', 'field35': 'first', 'field36': 'first', 'field37': 'first', 'field38': 'first',
                'field39': 'first', 'field40': 'first', 'category': 'first', 'item_name': 'first', 'field44': 'first',
                'field45': 'first', 'unit_price': 'first', 'field48': 'first', 'field49': 'first', 'field50': 'first',
                'customize': 'first', 'bom': 'first', 'field53': 'first', 'field54': 'first', 'field55': 'first',
                'field56': 'first', 'field57': 'first', 'field58': 'first', 'field59': 'first', 'field60': 'first',
                'field61': 'first', 'sq_no': 'first', 'user_name': 'first', 'customize_bom_str': 'first', 
                'seq': 'first', 'is_customize_end': 'first',  # 新增的欄位
                'spare_item': 'first',  # 新增的 spare_item 欄位
                'field68': 'first'  # 新增的第68個欄位
            }).reset_index()

            # 轉回 tuple 格式
            customize_bom_change = []
            for _, row in grouped_df.iterrows():
                detail_tuple = (
                    row['order_no'], row['type'], row['field2'], row['date_str'], row['field4'],
                    row['url'], row['field6'], row['field7'], row['field8'], row['field9'],
                    row['customer_name'], row['customer_name2'], row['uniform_no'], row['address'],
                    row['window'], row['phone'], row['email'], row['payment_term'], row['payment_type'],
                    row['field19'], row['field20'], row['field21'], row['field22'], row['field23'],
                    row['field24'], row['is_customize'], row['field26'], row['field27'], row['field28'],
                    row['field29'], row['field30'], row['field31'], row['field32'], row['field33'],
                    row['field34'], row['field35'], row['field36'], row['field37'], row['field38'],
                    row['field39'], row['field40'],
                    # 明細欄位
                    row['item'], row['category'], row['item_name'], row['field44'], row['field45'],
                    row['unit_price'], row['quantity'], row['field48'], row['field49'], row['field50'],
                    row['customize'], row['bom'], row['field53'], row['field54'], row['field55'],
                    row['field56'], row['field57'], row['field58'], row['field59'], row['field60'],
                    row['field61'], row['sq_no'], row['user_name'], row['customize_bom_str'], 
                    row['seq'], row['is_customize_end'], row['spare_item'], row['field68']  # 新增的 field68 欄位
                )
                customize_bom_change.append(detail_tuple)

        # 合併客製化BOM變更與備用料件(訂單明細)
        if len(customize_bom_change) > 0:
            new_quotation_detail.extend(customize_bom_change)
        if len(spare_item) > 0:
            new_quotation_detail.extend(spare_item)

        # 重新處理訂單明細序號
        if len(new_quotation_detail) > 0:
            for i, per_new in enumerate(new_quotation_detail):
                # 轉成 list，修改第一個欄位，再轉回 tuple
                per_new_list = list(per_new)
                per_new_list[0] = f"{sq_no}-{i+1}"
                # 確保有足夠的元素來設定 seq
                if len(per_new_list) > 65:
                    per_new_list[65] = i+1  # seq 欄位
                else:
                    # 如果元素不足，補足到正確長度
                    while len(per_new_list) <= 65:
                        per_new_list.append('')
                    per_new_list[65] = i+1
                new_quotation_detail[i] = tuple(per_new_list)

        # 刪除原本的訂單明細&bom
        delete_order_detail: list = [
            (
                self.sq_gs_url,
            )
        ]
        delete_bom: list = [
            (
                self.sq_gs_url,
            )
        ]
        result: bool = xin_tea.crt_or_update_order_manage_summary_b_to_b_and_update_import_num(new_quotation_detail, customize_bom, delete_order_detail, delete_bom)
        return result
    

    def __check_rule(self) -> str:
        """檢查規則+讀取報價單資料"""
        # 檢查是否存在
        for _ in (0, 10):
            try:
                exist: list = xin_tea.qry_order_exist(self.sq_gs_url)
                if not exist:
                    return '此報價單尚未匯入，無法進行更新'
                # 檢查是否符合更新(未手動調整過任一張客製BOM)
                check_bom: list = xin_tea.qry_order_manage_summary_b_to_b_is_manual_update(self.sq_gs_url)
                if check_bom:
                    return '此報價單有訂單明細已手動調整過BOM，無法進行更新，請使用規格更新功能。'
                # 確認是否讀取的到Google Sheet
                try:
                    sheet = google_certificate(self.sq_gs_url)
                except Exception as e:
                    print(f"無法開啟 Google Sheet，請確認連結是否正確: {e}")
                    return 'Google Sheet網址異常'

                worksheet = sheet.get_worksheet(0)
                for i in range(0, len(sheet.worksheets())):
                    title = sheet.get_worksheet(i).title
                    if title == '報價單':
                        quotation_worksheet = sheet.get_worksheet(i)
                        
                        # Q2 公司抬頭 C1 專案名稱 D3 訂單確認日(客戶預計決策日) D4 最早到貨日 D5 最晚到貨日
                        cell_range = quotation_worksheet.batch_get(['Q2', 'C1', 'D3', 'D4', 'D5'])
                        q2_value = cell_range[0][0][0] if cell_range[0] and cell_range[0][0] else None
                        c1_value = cell_range[1][0][0] if cell_range[1] and cell_range[1][0] else None
                        d3_value = cell_range[2][0][0] if cell_range[2] and cell_range[2][0] else None
                        d4_value = cell_range[3][0][0] if cell_range[3] and cell_range[3][0] else None
                        d5_value = cell_range[4][0][0] if cell_range[4] and cell_range[4][0] else None
                        self.company_title = q2_value
                        self.project_name = c1_value
                        self.order_check_date = d3_value
                        self.earliest_arrival_date = d4_value
                        self.latest_arrival_date = d5_value
                        # 查詢客戶主檔
                        self.customer_data = xin_tea.qry_customer_data(self.company_title)
                        # 是否有該客戶主檔
                        if not self.customer_data:
                            return '無此客戶，請先建立客戶主檔'
                        # 是否有料件主檔
                        item_detail: list = []
                        for per_order in self.order: 
                            item_id = per_order.get('item')
                            if item_id:  # 確保料件號不是空值
                                item_detail.append(item_id)
                            # 料件類別為需要BOM的料件，則需檢查是否有BOM
                            item_category: str = per_order.get('category', '')
                            # 查詢是否為需要BOM的料件類別
                            must_bom: list = xin_tea_order_manage_summary_b_to_c.qry_item_category_must_bom(item_category)
                            if must_bom:
                                # 需要BOM的料件，則需檢查是否有BOM
                                bom: str = per_order.get('用料清單單號')
                                if len(bom) == 0:
                                    #error_message += f"訂單號碼：【{order_no}】料件：【{item_id}】類別：【{item_category}】為需要BOM的料件，但無BOM資料\n"
                                    #error_order_no.append(order_no)
                                    #item_must_bom_actual_no_bom_num += 1
                                    #continu
                                    pass

                        if item_detail:  # 如果有料件需要檢查
                            item_exist: list = xin_tea.qry_item_data_in_item(item_detail)
                            
                            # 取得存在的料件清單
                            existing_items = [item['item'] for item in item_exist] if item_exist else []
                            
                            # 找出不存在的料件
                            missing_items = [item for item in item_detail if item not in existing_items]
                            
                            if missing_items:
                                missing_items_str = ', '.join(missing_items)
                                return f'料件主檔有誤，以下料件不存在: {missing_items_str}，請確認料件主檔是否建立完整'
                    elif title == '系統用':
                        # 訂單明細
                        worksheet = sheet.get_worksheet(i)
                        order_df = pd.DataFrame(worksheet.get_all_records())
                        self.order = order_df.to_dict(orient='records')
                        for per_order in self.order:
                            check_item: list = xin_tea.qry_item_data_in_item([str(per_order.get('禮盒料號'))])
                            if not check_item:
                                return f"禮盒料號【{per_order.get('禮盒料號')}】不存在，請確認主檔是否建立"
                return ''
            except (gspread.exceptions.APIError, google_exceptions.QuotaExceeded):
                self.__sleep()
    

    def __sleep(self):
        # 指數退避法 暫停時間
        sleep = math.pow(2, self.sleep)
        print(f"時間暫停秒數: ", sleep)
        time.sleep(sleep)
        if self.sleep < 6:
            self.sleep += 1


if __name__ == '__main__':
    UpdateBtoBGsSq('https://docs.google.com/spreadsheets/d/14kRyrny6deOfYUGbsjnLZUzXRrt2hvaF2GpgDaF0R7s/edit?gid=487771632#gid=487771632').process_data()   