import pandas as pd
import time, math
import gspread.exceptions
from datetime import datetime
from google.api_core import exceptions as google_exceptions
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.db_process.xin_tea.order_import import main as xin_tea
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea_order_manage_summary_b_to_c
from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea_b_to_b
from programs.core.cloud_eip.web_service import EIPService
from typing import Optional, Dict, Tuple


class UpdateSpecificBtoBGsSqV2:
    def __init__(self, sq_gs_url: str, user_name: str):
        self.error_message: str = ''
        self.sq_gs_url: str = sq_gs_url
        self.user_name: str = user_name
        self.order: list = []
        self.company_title: str = ''
        self.project_name: str = ''
        self.customer_data: list = []
        self.order_check_date: str = ''
        self.earliest_arrival_date: str = ''
        # self.latest_arrival_date: str = ''
        self.ele_invoice: str = ''
        self.delivery_method: str = ''
        self.xin_tea_connector: str = ''
        self.xin_tea_connect_phone: str = ''
        self.xin_tea_connect_email: str = ''
        self.sleep: int = 0
        self.sales_quotation_type: str = ''
        self.freight_unit_price: float = 0.0
        self.freight_quantity: int = 0
        self.freight_discount_rate: float = 0.0
        self.freight_discount_price: float = 0.0
        self.total_freight: float = 0.0
        self.payment_charge: float = 0.0
        self.payment_charge_discount: float = 0.0
        self.total_payment_charge: float = 0.0
        self.customer_contact: str = ''
        self.is_direct_from_oem: str = ''
        self.order_invoice_url: str = ''
        self.order_type: str = '' # 訂單類別
        self.payment_type: str = '' # 付款方式
        self.payment_condition: str = '' # 付款條件
        self.order_remark: str = '' # 訂單備註
        self.sales_quotation_name: str = '' # 報價名稱
        self.customer_uniform_invoice: str = '' # 客戶統編
        self.customer_address: str = '' # 客戶地址
        self.customer_window: str = '' # 客戶窗口
        self.customer_phone: str = '' # 客戶電話
        self.customer_email: str = '' # 客戶信箱
        self.prompt_message: str = ''  # 提示訊息
    
    def process_data(self):
        # 1. 檢查規則
        error_msg: str = self.__check_rule()
        if error_msg:
            xin_tea.crt_order_import_record_b_to_b([('B2B規格更新', 'Google Sheet', error_msg)])
            return error_msg
        if self.error_message:
            xin_tea.crt_order_import_record_b_to_b([('B2B規格更新', 'Google Sheet', self.error_message)])
            return self.error_message
        # 2. 新增B2B訂單資料
        result: bool = self.__crt_order_manage_summary_b_to_b()
        if result:
            if self.prompt_message:
                return f'B2B報價單規格更新成功<br>提示訊息：{self.prompt_message}'
            return 'B2B報價單規格更新成功'
        return 'B2B報價單規格更新失敗'

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

        # 取得原始報價單號(all_seq 最小的那筆)而非最新的
        sq_no: str =  sq_data[0]['sq_form_id']
        seq: int = 1
        customize_bom_change: list = []
        spare_item: list = []
        bom_and_gs_url: list = []
        upd_bom_and_gs_url: list = []
        order_and_gs_url: list = []
        upd_order_and_gs_url: list = []
        sales_quotataion_data: list = []
        
        # 計算total
        total_amount: float = 0
        total_order_num: float = 0
        
        # 第一次遍歷:計算總金額和總訂單數量
        for per_order in self.order:
            quantity: float = 0
            try:
                quantity = float(str(per_order.get('報價數量')).replace(',', '') or 0)
            except ValueError:
                pass
            
            if quantity > 0:
                total_amount += float(per_order.get('小計\n(含稅)').split('$')[1].replace(',', ''))
                total_order_num += quantity
                
                customized_options = [per_order.get(f'客製化方案料件#{i}', '') for i in range(1, 9)]
                item_id: str = str(per_order.get('料號', ''))
                
                if not item_id:
                    continue
                
                # 處理客製化對總數的影響
                for per_pus in customized_options:
                    if not per_pus:
                        continue
                    
                    check_replace: list = xin_tea.qry_customize_item_replace_by_item(str(per_pus))
                    if not check_replace:
                        continue
                    
                    is_many_check_replace: bool = len(check_replace) > 1
                    is_add_to_total: bool = False
                    is_first_replace: bool = True
                    
                    for per_check in check_replace:
                        if per_check.get('replace_item') == '':
                            # 新增料件
                            if not is_many_check_replace or (is_many_check_replace and not is_add_to_total):
                                total_order_num += int(quantity)
                                is_add_to_total = True
                        else:
                            # 替換料件
                            if is_many_check_replace and not is_first_replace:
                                total_order_num -= int(quantity)
                            is_first_replace = False
                
                # 處理備用料件對總數的影響
                has_customized = any(opt for opt in customized_options if opt)
                customize_qry: str = '客製' if has_customized else '標準'
                
                # 檢查客製化料件中是否有料件名稱包含「提袋」
                is_customize_spare: str = '標準'  # 預設為標準
                for opt in customized_options:
                    if opt:  # 確保不是空字串
                        try:
                            # 查詢料件名稱
                            opt_item_data = xin_tea.qry_item_data_in_item([str(opt)])
                            if opt_item_data:
                                item_name = opt_item_data[0].get('item_name', '')
                                # 檢查料件名稱是否包含「提袋」
                                if '提袋' in item_name:
                                    is_customize_spare = '客製'
                                    print(f'客製化料件 {opt} 名稱包含「提袋」: {item_name}')
                                    break
                        except Exception as e:
                            print(f'查詢料件 {opt} 時發生錯誤: {e}')
                            pass

                print('is_customize_spare: ', is_customize_spare)
                spare_item_data: list = xin_tea.qry_spare_item(item_id, is_customize_spare)
                if spare_item_data:
                    for per_spare in spare_item_data:
                        additional_add: float = per_spare.get('full_num_additional_add')
                        additional_num: int = int(quantity // additional_add)
                        if additional_num > 0:
                            total_order_num += additional_num
        
        print('total_order_num:', total_order_num)
        
        # 第二次遍歷:收集禮盒和外購品資訊
        additional_bom: list = []
        additional_data: list = []
        gift_boxes: list = []
        
        for per_order in self.order:
            quantity: float = 0
            try:
                quantity = float(str(per_order.get('報價數量')).replace(',', '') or 0)
            except ValueError:
                pass
            
            if quantity > 0:
                item_id: str = str(per_order.get('料號', ''))
                item_batch: str = per_order.get('同料號\n第幾批次生產\n(公式不能動)', '')
                
                if not item_id:
                    continue
                
                item_data: list = xin_tea.qry_item_data_in_item([item_id])
                
                # 收集禮盒資訊
                if item_data[0]['category'] == 'A':
                    item_name: str = item_data[0]['item_name']
                    if '此欄位改成客戶名稱' in item_name:
                        item_name = item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
                    
                    gift_boxes.append({
                        'item_id': item_id,
                        'item_batch': item_batch,
                        'item_name': item_name,
                        'quantity': int(quantity)
                    })
                
                # 收集外購品資訊
                if item_data[0]['category'] != 'A' and item_id != '3300003':
                    item_name: str = item_data[0]['item_name']
                    if '此欄位改成客戶名稱' in item_name:
                        item_name = item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
                    
                    additional_data.append({
                        'item_id': item_id,
                        'item_batch': item_batch,
                        'item_name': item_name,
                        'quantity': int(quantity)
                    })
        
        # 計算外購品分配
        box_num: int = len(gift_boxes)
        print(f"\n========== 外購品依數量比例分配計算 ==========")
        print(f"禮盒種類數量(含批次): {box_num}")
        print(f"外購品種類數量(含批次): {len(additional_data)}")
        
        if box_num > 0 and len(additional_data) > 0:
            total_gift_box_qty: int = sum(gift_box['quantity'] for gift_box in gift_boxes)
            print(f"禮盒總數量: {total_gift_box_qty}")
            
            for ext_product in additional_data:
                total_ext_qty = ext_product['quantity']
                print(f"\n外購品: {ext_product['item_id']} 批次:{ext_product['item_batch']} ({ext_product['item_name']})")
                print(f"總數量: {total_ext_qty}")
                
                allocated_quantities = []
                total_allocated = 0
                
                for gift_box in gift_boxes:
                    allocated_qty = (total_ext_qty * gift_box['quantity']) // total_gift_box_qty
                    ratio = gift_box['quantity'] / total_gift_box_qty
                    
                    allocated_quantities.append({
                        'gift_box': gift_box,
                        'allocated_qty': allocated_qty,
                        'ratio': ratio
                    })
                    total_allocated += allocated_qty
                
                # 處理餘數
                remainder = total_ext_qty - total_allocated
                if remainder > 0:
                    sorted_allocations = sorted(allocated_quantities, key=lambda x: x['ratio'], reverse=True)
                    for i in range(remainder):
                        sorted_allocations[i]['allocated_qty'] += 1
                
                # 產生BOM明細
                for allocation in allocated_quantities:
                    gift_box = allocation['gift_box']
                    allocated_qty = allocation['allocated_qty']
                    
                    additional_bom.append({
                        'gift_box_item': gift_box['item_id'],
                        'gift_box_batch': gift_box['item_batch'],
                        'gift_box_name': gift_box['item_name'],
                        'external_item': ext_product['item_id'],
                        'external_batch': ext_product['item_batch'],
                        'external_name': ext_product['item_name'],
                        'allocated_quantity': allocated_qty
                    })
        
        print(f"\n總共產生 {len(additional_bom)} 筆外購品 BOM 明細")
        
        # 第三次遍歷:處理訂單明細
        additional_product_bom: list = []
        
        for per_order in self.order:
            quantity: float = 0
            try:
                quantity = float(str(per_order.get('報價數量')).replace(',', '') or 0)
            except ValueError:
                pass
            
            if quantity <= 0:
                continue
            
            item_id: str = str(per_order.get('料號', ''))
            if not item_id:
                continue
            
            # 處理訂單與GS URL的關聯
            order_detail_exist: list = xin_tea.qry_order_detail_and_gs_url_exist(self.sq_gs_url, item_id)
            if order_detail_exist:
                upd_order_and_gs_url.append((item_id, self.sq_gs_url))
            else:
                order_and_gs_url.append((self.sq_gs_url, item_id))
            
            # 取得料件資料
            customized_options = [per_order.get(f'客製化方案料件#{i}', '') for i in range(1, 9)]
            bom: str = ''
            try:
                bom = xin_tea.qry_bom_by_item(item_id)[0]['bom']
            except Exception as e:
                pass
            
            item_data: list = xin_tea.qry_item_data_in_item([item_id])
            
            # 判斷是否客製化
            has_customized = any(opt for opt in customized_options if opt)
            customize: str = '客製化禮盒' if has_customized else '標準禮盒'
            is_customize: str = '1' if has_customized else '0'
            # A料件才需要產生BOM
            customize_bom_str: str = ''
            if item_data[0]['category'] in ['A']:
                customize_bom_str = f"{sq_no}-{seq}"

            # 料件類型 (修正: category != 'A' 才是外購品)
            different: int = int(quantity)
            item_type: str = '外購品' if item_data[0]['category'] != 'A' else ''
            if item_type == '外購品':
                customize = ''
            item_name: str = item_data[0]['item_name']
            if '此欄位改成客戶名稱' in item_name:
                item_name = item_name.replace('此欄位改成客戶名稱', customer_data[0]['customer_name'])
            
            # 記錄原始報價單資料
            if item_id != '3300003':
                sales_quotataion_data.append((
                    self.sq_gs_url, item_id, quantity,
                    per_order.get('同料號\n第幾批次生產\n(公式不能動)', '')
                ))
            
            # 建立訂單明細
            new_quotation_detail.append((
                f"{sq_no}-{seq}", '2', '', now_date_str, self.customer_contact,
                self.sq_gs_url, self.order_invoice_url, self.order_check_date,
                self.earliest_arrival_date, customer_data[0]['customer_name'],
                customer_data[0]['customer_name'], self.customer_uniform_invoice_no,
                self.customer_address, self.customer_window,
                self.customer_phone, self.customer_email,
                self.payment_term, self.payment_type,
                self.ele_invoice, self.delivery_method, self.order_remark,
                self.xin_tea_connector, self.xin_tea_connect_phone, self.xin_tea_connect_email,
                is_customize, total_amount, '',
                self.freight_unit_price, self.freight_quantity, self.freight_discount_rate,
                self.freight_discount_price, self.total_freight, total_amount + self.total_freight,
                self.payment_charge, self.payment_charge_discount, self.total_payment_charge,
                total_amount + self.total_freight + self.total_payment_charge,
                total_order_num, '', self.order_type,
                item_id, item_data[0]['category'], item_name,
                per_order.get('規格_HTML', ''), per_order.get('客製化方案', ''),
                per_order.get('零售訂價 \n(含稅)', '$0').split('$')[1].replace(',', ''),
                quantity,
                per_order.get('優惠折數', '0%').replace('%', ''),
                per_order.get('單件優惠價\n(含稅)', '$0').split('$')[1].replace(',', ''),
                per_order.get('小計\n(含稅)', '$0').split('$')[1].replace(',', ''),
                customize, bom, '', '', '', '', '', '', '', '', '',
                f"{sq_no}", self.user_name, customize_bom_str, seq, is_customize, '', '0',
                per_order.get('同料號\n第幾批次生產\n(公式不能動)', ''),
                item_type, quantity, self.is_direct_from_oem,
                self.sales_quotation_type, self.sales_quotation_name,
                self.latest_arrival_date
            ))
            
            # 處理BOM與GS URL的關聯
            exist_data: list = xin_tea.qry_customize_bom_and_gs_url_exist(f"{sq_no}-{seq}", self.sq_gs_url)
            if exist_data:
                upd_bom_and_gs_url.append((self.sq_gs_url, f"{sq_no}-{seq}"))
            else:
                bom_and_gs_url.append((f"{sq_no}-{seq}", self.sq_gs_url))
            
            # 處理客製化BOM
            bom_data = xin_tea.qry_bom_detail_by_item(item_id, bom)
            
            for per_pus in customized_options:
                if not per_pus:
                    continue
                
                check_replace: list = xin_tea.qry_customize_item_replace_by_item(str(per_pus))
                if not check_replace:
                    continue
                
                is_many_check_replace: bool = len(check_replace) > 1
                is_add_item: bool = False
                
                for per_check in check_replace:
                    origin_customize_item: list = xin_tea.qry_item_data_in_item([str(per_pus)])
                    origin_customize_item_name: str = origin_customize_item[0]['item_name']
                    
                    if '此欄位改成客戶名稱' in origin_customize_item_name:
                        origin_customize_item_name = origin_customize_item_name.replace(
                            '此欄位改成客戶名稱', customer_data[0]['customer_name']
                        )
                    
                    if per_check.get('replace_item') == '':
                        # 純新增料件
                        if not is_many_check_replace or (is_many_check_replace and not is_add_item):
                            bom_data.append({
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
                            })
                            
                            customize_bom_change.append((
                                '', '2', '', now_date_str, self.customer_contact,
                                self.sq_gs_url, self.order_invoice_url, self.order_check_date,
                                self.earliest_arrival_date, customer_data[0]['customer_name'],
                                customer_data[0]['customer_name'], self.customer_uniform_invoice_no,
                                self.customer_address, self.customer_window,
                                self.customer_phone, self.customer_email,
                                self.payment_term, self.payment_type,
                                self.ele_invoice, self.delivery_method, self.order_remark,
                                self.xin_tea_connector, self.xin_tea_connect_phone, self.xin_tea_connect_email,
                                is_customize, total_amount, '',
                                self.freight_unit_price, self.freight_quantity, self.freight_discount_rate,
                                self.freight_discount_price, self.total_freight, total_amount + self.total_freight,
                                self.payment_charge, self.payment_charge_discount, self.total_payment_charge,
                                total_amount + self.total_freight + self.total_payment_charge,
                                total_order_num, '', self.order_type,
                                origin_customize_item[0]['item'], origin_customize_item[0]['category'],
                                origin_customize_item_name, '', '', 0, quantity, '', '', '', '',
                                origin_customize_item[0]['bom'], '', '', '', '', '', '', '', '', '',
                                f"{sq_no}", self.user_name, '', '', '0', '', '1', '', '',
                                quantity, self.is_direct_from_oem, self.sales_quotation_type,
                                self.sales_quotation_name, self.latest_arrival_date
                            ))
                            is_add_item = True
                    else:
                        # 替換料件
                        if not is_many_check_replace or (is_many_check_replace and not is_add_item):
                            bom_data.append({
                                "item": item_id,
                                "item_name": item_data[0]['item_name'],
                                "m_item": item_data[0]['item'],
                                "m_item_name": item_data[0]['item_name'],
                                "s_item": origin_customize_item[0]['item'],
                                "s_item_name": origin_customize_item_name,
                                "s_item_spec": "",
                                "customize_item": f"{per_check.get('replace_item')}替換料件",
                                "origin_use_quantity": 1,
                                "use_quantity": 1,
                                "customize_type": '替換料件'
                            })
                            
                            customize_bom_change.append((
                                '', '2', '', now_date_str, self.customer_contact,
                                self.sq_gs_url, self.order_invoice_url, self.order_check_date,
                                self.earliest_arrival_date, customer_data[0]['customer_name'],
                                customer_data[0]['customer_name'], self.customer_uniform_invoice_no,
                                self.customer_address, self.customer_window,
                                self.customer_phone, self.customer_email,
                                self.payment_term, self.payment_type,
                                self.ele_invoice, self.delivery_method, self.order_remark,
                                self.xin_tea_connector, self.xin_tea_connect_phone, self.xin_tea_connect_email,
                                is_customize, total_amount, '',
                                self.freight_unit_price, self.freight_quantity, self.freight_discount_rate,
                                self.freight_discount_price, self.total_freight, total_amount + self.total_freight,
                                self.payment_charge, self.payment_charge_discount, self.total_payment_charge,
                                total_amount + self.total_freight + self.total_payment_charge,
                                total_order_num, '', self.order_type,
                                origin_customize_item[0]['item'], origin_customize_item[0]['category'],
                                origin_customize_item_name, '', '', 0, quantity, '', '', '', '',
                                origin_customize_item[0]['bom'], '', '', '', '', '', '', '', '', '',
                                f"{sq_no}", self.user_name, '', '', '0', '', '1', '', '',
                                quantity, self.is_direct_from_oem, self.sales_quotation_type,
                                self.sales_quotation_name, self.latest_arrival_date
                            ))
                            is_add_item = True
                        
                        # 將被替換的料件用量歸0
                        for per_bom in bom_data:
                            if per_bom.get('s_item') == per_check.get('replace_item'):
                                per_bom['use_quantity'] = 0
                                per_bom['customize_item'] = f"被料件{per_check.get('customize_item')}替換，刪除料件"
                                per_bom['customize_type'] = '被替換料件'
                        
                        # 被替換料件的負數明細
                        replace_item: list = xin_tea.qry_item_data_in_item([str(per_check.get('replace_item'))])
                        customize_bom_change.append((
                            '', '2', '', now_date_str, self.customer_contact,
                            self.sq_gs_url, self.order_invoice_url, self.order_check_date,
                            self.earliest_arrival_date, customer_data[0]['customer_name'],
                            customer_data[0]['customer_name'], self.customer_uniform_invoice_no,
                            self.customer_address, self.customer_window,
                            self.customer_phone, self.customer_email,
                            self.payment_term, self.payment_type,
                            self.ele_invoice, self.delivery_method, self.order_remark,
                            self.xin_tea_connector, self.xin_tea_connect_phone, self.xin_tea_connect_email,
                            is_customize, total_amount, '',
                            self.freight_unit_price, self.freight_quantity, self.freight_discount_rate,
                            self.freight_discount_price, self.total_freight, total_amount + self.total_freight,
                            self.payment_charge, self.payment_charge_discount, self.total_payment_charge,
                            total_amount + self.total_freight + self.total_payment_charge,
                            total_order_num, '', self.order_type,
                            replace_item[0]['item'], replace_item[0]['category'],
                            replace_item[0]['item_name'], '', '', 0, -quantity, '', '', '', '',
                            replace_item[0]['bom'], '', '', '', '', '', '', '', '', '',
                            f"{sq_no}", self.user_name, '', '', '0', '', '1', '', '',
                            -quantity, self.is_direct_from_oem, self.sales_quotation_type,
                            self.sales_quotation_name, self.latest_arrival_date
                        ))
            
            # 產生客製化BOM
            seq_counter: int = 1
            for j, per_bom in enumerate(bom_data):
                customize_bom.append((
                    f"{sq_no}-{seq}-{j+1}", per_bom.get('item'), per_bom.get('m_item'),
                    per_bom.get('s_item'), per_bom.get('s_item_name'), per_bom.get('s_item_spec'),
                    '', per_bom.get('customize_item'), per_bom.get('origin_use_quantity'),
                    per_bom.get('use_quantity'), 0, f"{sq_no}-{seq}",
                    j + 1, per_bom.get('customize_type')
                ))
                seq_counter += 1
            
            # 處理備用料件
            customize_qry: str = '客製' if customize else '標準'
            # 檢查客製化料件中是否有料件名稱包含「提袋」
            is_customize_spare: str = '標準'  # 預設為標準
            for opt in customized_options:
                if opt:  # 確保不是空字串
                    try:
                        # 查詢料件名稱
                        opt_item_data = xin_tea.qry_item_data_in_item([str(opt)])
                        if opt_item_data:
                            item_name = opt_item_data[0].get('item_name', '')
                            # 檢查料件名稱是否包含「提袋」
                            if '提袋' in item_name:
                                is_customize_spare = '客製'
                                print(f'客製化料件 {opt} 名稱包含「提袋」: {item_name}')
                                break
                    except Exception as e:
                        print(f'查詢料件 {opt} 時發生錯誤: {e}')
                        pass

            spare_item_data: list = xin_tea.qry_spare_item(item_id, is_customize_spare)
            if spare_item_data:
                for per_spare in spare_item_data:
                    additional_add: float = per_spare.get('full_num_additional_add')
                    additional_num: int = int(quantity // additional_add)
                    
                    if additional_num > 0:
                        spare_item_name: str = per_spare.get('spare_item_name')
                        if '此欄位改成客戶名稱' in spare_item_name:
                            spare_item_name = spare_item_name.replace(
                                '此欄位改成客戶名稱', customer_data[0]['customer_name']
                            )
                        
                        spare_item.append((
                            '', '2', '', now_date_str, self.customer_contact,
                            self.sq_gs_url, self.order_invoice_url, self.order_check_date,
                            self.earliest_arrival_date, customer_data[0]['customer_name'],
                            customer_data[0]['customer_name'], self.customer_uniform_invoice_no,
                            self.customer_address, self.customer_window,
                            self.customer_phone, self.customer_email,
                            self.payment_term, self.payment_type,
                            self.ele_invoice, self.delivery_method, self.order_remark,
                            self.xin_tea_connector, self.xin_tea_connect_phone, self.xin_tea_connect_email,
                            is_customize, total_amount, '',
                            self.freight_unit_price, self.freight_quantity, self.freight_discount_rate,
                            self.freight_discount_price, self.total_freight, total_amount + self.total_freight,
                            self.payment_charge, self.payment_charge_discount, self.total_payment_charge,
                            total_amount + self.total_freight + self.total_payment_charge,
                            total_order_num, '', self.order_type,
                            per_spare.get('spare_item'), per_spare.get('spare_item_category'),
                            spare_item_name, '', '', 0, additional_num, '', '', '', '',
                            per_spare.get('bom'), '', '', '', '', '', '', '', '', '',
                            f"{sq_no}", self.user_name, '', '', '0', item_id, '1', '', '',
                            additional_num, self.is_direct_from_oem, self.sales_quotation_type,
                            self.sales_quotation_name, self.latest_arrival_date
                        ))
                        
                        if bom_data:
                            customize_bom.append((
                                f"{sq_no}-{seq}-{seq_counter}", bom_data[0].get('item'),
                                bom_data[0].get('m_item'), per_spare.get('spare_item'),
                                spare_item_name, '', '', '備用料件，額外備用量',
                                0, 0, additional_num, f"{sq_no}-{seq}",
                                seq_counter, '備用料件'
                            ))
                            seq_counter += 1
            
            # 處理外購品BOM
            item_batch_current: str = per_order.get('同料號\n第幾批次生產\n(公式不能動)', '')
            bom_id: str = f"{sq_no}-{seq}"
            
            for per_add in additional_bom:
                if (per_add.get('gift_box_item') == item_id and
                    per_add.get('gift_box_batch') == item_batch_current):
                    
                    additional_product_bom.append((
                        f"{bom_id}-{seq_counter}", item_id, item_id,
                        per_add.get('external_item'), per_add.get('external_name'),
                        '', '', '外購品', 0, 0, per_add.get('allocated_quantity'),
                        bom_id, seq_counter, '外購品',
                        float(per_add.get('allocated_quantity'))/float(quantity)
                    ))
                    seq_counter += 1
            
            # 處理手動增加的項目
            manually_item: list = xin_tea.qry_add_manually_item(
                self.sq_gs_url, item_id, item_batch_current
            )
            for per_manual in manually_item:
                additional_product_bom.append((
                    f"{bom_id}-{seq_counter}", item_id, item_id,
                    per_manual.get('s_item'), per_manual.get('s_item_name'),
                    '', '', '手動增加', 0, per_manual.get('use_quantity'),
                    per_manual.get('adjustment_quantity'),
                    bom_id, seq_counter, '手動增加', None
                ))
                seq_counter += 1
            
            seq += 1
        
        # 合併客製化BOM變更
        if len(customize_bom_change) > 0:
            detail_dicts = []
            for detail in customize_bom_change:
                detail_dict = {
                    'order_no': detail[0], 'type': detail[1], 'field2': detail[2],
                    'date_str': detail[3], 'field4': detail[4], 'url': detail[5],
                    'field6': detail[6], 'field7': detail[7], 'field8': detail[8],
                    'customer_name': detail[9], 'customer_name2': detail[10],
                    'uniform_no': detail[11], 'address': detail[12], 'window': detail[13],
                    'phone': detail[14], 'email': detail[15], 'payment_term': detail[16],
                    'payment_type': detail[17], 'field19': detail[18], 'field20': detail[19],
                    'field21': detail[20], 'field22': detail[21], 'field23': detail[22],
                    'field24': detail[23], 'is_customize': detail[24], 'field26': detail[25],
                    'field27': detail[26], 'field28': detail[27], 'field29': detail[28],
                    'field30': detail[29], 'field31': detail[30], 'field32': detail[31],
                    'field33': detail[32], 'field34': detail[33], 'field35': detail[34],
                    'field36': detail[35], 'field37': detail[36], 'field38': detail[37],
                    'field39': detail[38], 'field40': detail[39], 'item': detail[40],
                    'category': detail[41], 'item_name': detail[42], 'field44': detail[43],
                    'field45': detail[44], 'unit_price': detail[45], 'quantity': detail[46],
                    'field48': detail[47], 'field49': detail[48], 'field50': detail[49],
                    'customize': detail[50], 'bom': detail[51], 'field53': detail[52],
                    'field54': detail[53], 'field55': detail[54], 'field56': detail[55],
                    'field57': detail[56], 'field58': detail[57], 'field59': detail[58],
                    'field60': detail[59], 'field61': detail[60], 'sq_no': detail[61],
                    'user_name': detail[62], 'customize_bom_str': detail[63],
                    'seq': detail[64], 'is_customize_end': detail[65] if len(detail) > 65 else '0',
                    'spare_item': detail[66] if len(detail) > 66 else '',
                    'field68': detail[67] if len(detail) > 67 else '0',
                    'item_batch': detail[68] if len(detail) > 68 else '',
                    'item_type': detail[69] if len(detail) > 69 else '',
                    'different': detail[70] if len(detail) > 70 else '0',
                    'is_direct_from_oem': detail[71] if len(detail) > 71 else '0',
                    'sales_quotation_type': detail[72] if len(detail) > 72 else '',
                    'sales_quotation_name': detail[73] if len(detail) > 73 else '',
                    'latest_arrival_date_by_generate': detail[74] if len(detail) > 74 else ''
                }
                detail_dicts.append(detail_dict)
            
            df = pd.DataFrame(detail_dicts)
            
            grouped_df = df.groupby('item').agg({
                'quantity': 'sum',
                'order_no': 'first', 'type': 'first', 'field2': 'first',
                'date_str': 'first', 'field4': 'first', 'url': 'first',
                'field6': 'first', 'field7': 'first', 'field8': 'first',
                'customer_name': 'first', 'customer_name2': 'first',
                'uniform_no': 'first', 'address': 'first', 'window': 'first',
                'phone': 'first', 'email': 'first', 'payment_term': 'first',
                'payment_type': 'first', 'field19': 'first', 'field20': 'first',
                'field21': 'first', 'field22': 'first', 'field23': 'first',
                'field24': 'first', 'is_customize': 'first', 'field26': 'first',
                'field27': 'first', 'field28': 'first', 'field29': 'first',
                'field30': 'first', 'field31': 'first', 'field32': 'first',
                'field33': 'first', 'field34': 'first', 'field35': 'first',
                'field36': 'first', 'field37': 'first', 'field38': 'first',
                'field39': 'first', 'field40': 'first', 'category': 'first',
                'item_name': 'first', 'field44': 'first', 'field45': 'first',
                'unit_price': 'first', 'field48': 'first', 'field49': 'first',
                'field50': 'first', 'customize': 'first', 'bom': 'first',
                'field53': 'first', 'field54': 'first', 'field55': 'first',
                'field56': 'first', 'field57': 'first', 'field58': 'first',
                'field59': 'first', 'field60': 'first', 'field61': 'first',
                'sq_no': 'first', 'user_name': 'first', 'customize_bom_str': 'first',
                'seq': 'first', 'is_customize_end': 'first', 'spare_item': 'first',
                'field68': 'first', 'item_batch': 'first', 'item_type': 'first',
                'different': 'first', 'is_direct_from_oem': 'first',
                'sales_quotation_type': 'first', 'sales_quotation_name': 'first',
                'latest_arrival_date_by_generate': 'first'
            }).reset_index()
            
            customize_bom_change = []
            for _, row in grouped_df.iterrows():
                detail_tuple = (
                    row['order_no'], row['type'], row['field2'], row['date_str'], row['field4'],
                    row['url'], row['field6'], row['field7'], row['field8'],
                    row['customer_name'], row['customer_name2'], row['uniform_no'], row['address'],
                    row['window'], row['phone'], row['email'], row['payment_term'], row['payment_type'],
                    row['field19'], row['field20'], row['field21'], row['field22'], row['field23'],
                    row['field24'], row['is_customize'], row['field26'], row['field27'], row['field28'],
                    row['field29'], row['field30'], row['field31'], row['field32'], row['field33'],
                    row['field34'], row['field35'], row['field36'], row['field37'], row['field38'],
                    row['field39'], row['field40'], row['item'], row['category'], row['item_name'],
                    row['field44'], row['field45'], row['unit_price'], row['quantity'], row['field48'],
                    row['field49'], row['field50'], row['customize'], row['bom'], row['field53'],
                    row['field54'], row['field55'], row['field56'], row['field57'], row['field58'],
                    row['field59'], row['field60'], row['field61'], row['sq_no'], row['user_name'],
                    row['customize_bom_str'], row['seq'], row['is_customize_end'], row['spare_item'],
                    row['field68'], row['item_batch'], row['item_type'], row['different'],
                    row['is_direct_from_oem'], row['sales_quotation_type'], row['sales_quotation_name'],
                    row['latest_arrival_date_by_generate']
                )
                customize_bom_change.append(detail_tuple)
        
        # 合併所有明細
        if len(customize_bom_change) > 0:
            new_quotation_detail.extend(customize_bom_change)
        if len(spare_item) > 0:
            new_quotation_detail.extend(spare_item)
        
        # 重新編號
        if len(new_quotation_detail) > 0:
            for i, per_new in enumerate(new_quotation_detail):
                per_new_list = list(per_new)
                per_new_list[0] = f"{sq_no}-{i+1}"
                
                if len(per_new_list) > 65:
                    per_new_list[65] = i + 1
                else:
                    while len(per_new_list) <= 65:
                        per_new_list.append('')
                    per_new_list[65] = i + 1
                
                new_quotation_detail[i] = tuple(per_new_list)
        
        # 準備儲存參數
        delete_order_detail: list = [(self.sq_gs_url,)]
        delete_bom: list = [(self.sq_gs_url,)]
        copy_bom: list = [(self.sq_gs_url,)]
        origin_bom_to_new_bom: list = [(self.sq_gs_url,)]
        origin_add_manual_item_to_new_bom: list = [(self.sq_gs_url,)]
        origin_manual_customize_bom_to_new_bom: list = [(self.sq_gs_url,)]
        origin_bom_delete: list = [(self.sq_gs_url,)]
        copy_order_detail: list = [(self.sq_gs_url,)]
        origin_order_detail_to_new_order_detail: list = [(self.sq_gs_url,)]
        origin_generate_to_new_generate: list = [(self.sq_gs_url,)]
        origin_add_manual_item_order_detail_to_new_bom: list = [(self.sq_gs_url, self.sq_gs_url)]
        origin_order_detail_delete: list = [(self.sq_gs_url,)]
        upd_spare_item_detail_latest_arrival_date: list = [(self.sq_gs_url,)]
        update_order_manage_summary_b_to_b_different: list = [(self.sq_gs_url,)]
        
        if order_and_gs_url:
            order_and_gs_url = list(dict.fromkeys(order_and_gs_url))
        
        # 儲存資料
        result: bool = xin_tea.crt_or_update_order_manage_summary_b_to_b_and_update_import_num(
            new_quotation_detail, customize_bom, delete_order_detail, delete_bom, copy_bom,
            origin_bom_to_new_bom, bom_and_gs_url, upd_bom_and_gs_url, origin_bom_delete,
            copy_order_detail, origin_order_detail_to_new_order_detail, origin_order_detail_delete,
            origin_generate_to_new_generate, order_and_gs_url, upd_order_and_gs_url,
            origin_add_manual_item_to_new_bom, origin_add_manual_item_order_detail_to_new_bom,
            origin_manual_customize_bom_to_new_bom, upd_spare_item_detail_latest_arrival_date,
            update_order_manage_summary_b_to_b_different, additional_product_bom,
            sales_quotataion_data
        )
        
        return result
    

    def __check_rule(self) -> str:
        """檢查規則+讀取報價單資料"""
        exist: list = xin_tea.qry_order_exist(self.sq_gs_url)
        if not exist:
            return '此報價單尚未匯入，無法進行規格更新'
        """
        # 檢查該報價單是否有正在進行中的訂單或是生產單
        check_data: list = xin_tea.qry_sales_quotation_is_alrady_have_bpm_form_bpm_generate(self.sq_gs_url)
        if check_data:
            return '此報價單已有正在進行中的訂單或生產單，無法進行規格更新'
        """
        # 確認是否讀取的到Google Sheet
        for _ in range(0, 10):
            try:
                sheet = google_certificate(self.sq_gs_url)
                quotation_worksheet = self._find_quotation_worksheet(sheet)
                
                if not quotation_worksheet:
                    continue
                
                # 讀取並設定表頭欄位
                self._load_header_fields(quotation_worksheet)
                
                # 驗證客戶資料
                customer_error = self._validate_customer_data()
                if customer_error:
                    return customer_error
                
                # 讀取訂單資料
                order_data_error = self._load_order_data(sheet, quotation_worksheet)
                if order_data_error:
                    return order_data_error
                
                # 檢查禮盒是否有對應備用提袋資料
                self._check_item_spare_data()
                
                # 驗證料件資料
                self._validate_items()
                
                break
                
            except (gspread.exceptions.APIError, google_exceptions.TooManyRequests, 
                    google_exceptions.ResourceExhausted) as e:
                if 'exceeds grid limits.' in str(e):
                    return 'Google Sheet 資料格式不符合,請調整後再匯入'
                self.__sleep()
        """
        檢查此次匯入報價單內容與既有報價單是否有被刪除之料號
        """
        origin_data: list = xin_tea.qry_order_manage_summary_b_to_b_different(self.sq_gs_url)

        # 建立既有資料的 (item_id, item_batch) 集合
        origin_items = {}
        for origin in origin_data:
            item_id = str(origin.get('item', '')).strip()
            item_batch = str(origin.get('item_batch', '')).strip()
            key = (item_id, item_batch)
            origin_items[key] = origin

        # 建立新訂單的 (item_id, item_batch) 集合
        new_items = {}
        for per_order in self.order:
            quantity: float = 0
            try:
                quantity = float(str(per_order.get('報價數量')).replace(',', '') or 0)
            except ValueError:
                pass
            
            if quantity > 0:
                item_id: str = str(per_order.get('料號', '')).strip()
                item_batch: str = str(per_order.get('同料號\n第幾批次生產\n(公式不能動)', '')).strip()
                
                item_data: list = xin_tea.qry_item_data_in_item([item_id])
                if item_data:
                    key = (item_id, item_batch)
                    new_items[key] = per_order

        # 檢查被刪除的項目 (在原始資料中,但不在新訂單中)
        print('origin_items:', origin_items.keys())
        print('new_items:', new_items.keys())
        delete_message: str = ''
        for key in origin_items:
            if key not in new_items:
                item_id, item_batch = key
                origin_item = origin_items[key]
                item_name = origin_item.get('item_name', '')
                print(f'檢查刪除的料號:{item_id} 批次:{item_batch} ({item_name})')
                # 檢查此料號+批次組合是否有進行中或簽核通過的表單
                has_active_form = xin_tea.qry_item_batch_has_active_bpm_form(
                    self.sq_gs_url, item_id, item_batch
                )
                
                if has_active_form:
                    print(f'料號:{item_id} 批次:{item_batch} ({item_name}) 有進行中的表單，無法刪除')
                    # 有進行中的表單,需要阻止刪除
                    bpm_form_id = origin_item.get('bpm_form_id', '')
                    bpm_generate_id = origin_item.get('bpm_generate_id', '')
                    print('bpm_form_id:', bpm_form_id)
                    print('bpm_generate_id:', bpm_generate_id)
                    # 抓取表單API確認是否為進行中或簽核通過
                    bpm_form_status: str = EIPService().get_subject_state(bpm_form_id).strip()
                    bpm_generate_status: str = EIPService().get_subject_state(bpm_generate_id).strip()    
                    print('bpm_form_status:', bpm_form_status)
                    print('bpm_generate_status:', bpm_generate_status)
                    if bpm_form_status in ['0', '1'] or bpm_generate_status in ['0', '1']:
                        delete_message += f"料號:{item_id} 批次:{item_batch} ({item_name}) 有進行中或簽核通過的表單，無法刪除<br>"
        if delete_message:
            return delete_message
        return ''


    def _find_quotation_worksheet(self, sheet):
        """尋找報價單工作表"""
        for i in range(len(sheet.worksheets())):
            worksheet = sheet.get_worksheet(i)
            if worksheet.title == '報價單':
                return worksheet
        return None


    def _extract_cell_value(self, cell_data):
        """提取儲存格值的輔助函數"""
        return cell_data[0][0] if cell_data and cell_data[0] else None


    def _load_header_fields(self, quotation_worksheet):
        """讀取並設定表頭欄位"""
        # 定義要讀取的儲存格
        cells_to_read = [
            'Q2', 'C1', 'D3', 'D4', 'D5', 'Q3', 'Q4', 'H111', 'H112', 'H113', 'K3',
            'G101', 'H101', 'I101', 'J101', 'K101', 'G102', 'K102', 'J102', 'S3',
            'S4', 'S5', 'E102', 'D104', 'D107', 'B2', 'C1', 'D109', 'D110', 'D111', 
            'D112', 'D113'
        ]
        
        cell_range = quotation_worksheet.batch_get(cells_to_read)
        
        # 提取所有儲存格值
        values = [self._extract_cell_value(cell) or '' for cell in cell_range]
        
        # 映射到對應的屬性
        (q2, c1, d3, d4, d5, q3, q4, h111, h112, h113, k3,
        g101, h101, i101, j101, k101, g102, k102, j102, s3,
        s4, s5, e102, d104, d107, b2, c1_dup, d109, d110, d111, 
        d112, d113) = values
        
        # 基本資訊
        self.company_title = q2
        self.sales_quotation_name = c1
        self.order_check_date = d3
        self.earliest_arrival_date = d4
        self.latest_arrival_date = d5
        self.ele_invoice = str(q3)
        self.delivery_method = q4
        self.xin_tea_connector = h111
        self.xin_tea_connect_phone = h112
        self.xin_tea_connect_email = h113
        self.sales_quotation_type = k3
        
        # 費用相關 (處理數字格式)
        self.freight_unit_price = self._parse_currency(g101)
        self.freight_quantity = self._parse_integer(h101)
        self.freight_discount_rate = self._parse_percentage(i101)
        self.freight_discount_price = self._parse_currency(j101)
        self.total_freight = self._parse_currency(k101)
        self.payment_charge = self._parse_percentage(g102)
        self.payment_charge_discount = self._parse_percentage(j102)
        self.total_payment_charge = self._parse_currency(k102)
        
        # 其他資訊
        self.customer_contact = s3
        self.is_direct_from_oem = s4
        self.order_invoice_url = s5
        self.payment_type = e102
        self.payment_term = d104
        self.order_remark = d107

        # 客戶窗口慣用聯繫方式
        if self.customer_contact is None:
            self.customer_contact = ''

        # 下訂憑證連結
        if self.order_invoice_url is None:
            self.order_invoice_url = ''

        # 是否代工廠直出處理
        if self.is_direct_from_oem is None:
            self.is_direct_from_oem = ''

        # 訂單備註
        if self.order_remark is None:
            self.order_remark = ''
        
        # 訂單類別處理
        try:
            self.order_type = b2.split('：')[0] if b2 else ''
        except:
            self.order_type = ''
        
        self.saels_quotation_name = c1_dup
        
        # 客戶資訊
        self.customer_uniform_invoice_no = self._normalize_invoice_no(d109)
        self.customer_address = d110
        self.customer_window = d111
        self.customer_phone = d112
        self.customer_email = d113


    def _parse_currency(self, value) -> float:
        """解析貨幣格式"""
        if not value:
            return 0.0
        return float(str(value).replace('NT$', '').replace(',', ''))


    def _parse_integer(self, value) -> int:
        """解析整數格式"""
        if not value:
            return 0
        return int(str(value).replace('NT$', '').replace(',', ''))


    def _parse_percentage(self, value) -> float:
        """解析百分比格式"""
        if not value:
            return 0.0
        return float(str(value).replace('%', ''))


    def _normalize_invoice_no(self, invoice_no) -> str:
        """正規化統一編號(處理0開頭的7位數統編)"""
        try:
            if invoice_no and len(invoice_no) == 7:
                return invoice_no.zfill(8)
            return invoice_no if invoice_no else ''
        except:
            return ''


    def _validate_customer_data(self) -> str:
        """驗證客戶資料"""
        if self.customer_uniform_invoice_no:
            self.customer_data = xin_tea.qry_customer_data(self.customer_uniform_invoice_no)
            if not self.customer_data:
                return '無此客戶,請先建立客戶主檔'
        else:
            # 無統編用客戶抬頭查詢
            self.customer_data = xin_tea.qry_customer_data_by_company_title(self.company_title)
        
        return ''


    def _load_order_data(self, sheet, quotation_worksheet) -> str:
        """讀取訂單資料"""
        start_row = 6
        end_row = 100
        data_range = quotation_worksheet.get(f'A{start_row}:AD{end_row}')
        
        if not data_range or len(data_range) <= 1:
            self.order = []
            return ''
        
        headers = data_range[0]
        data_rows = data_range[1:]
        
        # 正規化資料列
        normalized_rows = self._normalize_data_rows(data_rows, headers, start_row)
        
        # 建立 DataFrame
        order_df = pd.DataFrame(normalized_rows, columns=headers)
        
        # 記錄原始列號
        order_df = self._add_original_row_numbers(order_df, data_rows, start_row)
        
        # 清理資料
        order_df = self._clean_dataframe(order_df)
        
        # 轉換為字典格式
        self.order = order_df.to_dict(orient='records')
        
        # 處理規格欄位的富文本格式
        self._process_rich_text_specs(sheet, quotation_worksheet, headers)
        
        return ''


    def _normalize_data_rows(self, data_rows, headers, start_row) -> list:
        """正規化資料列(補齊或截斷欄位)"""
        normalized_rows = []
        expected_columns = len(headers)
        
        for idx, row in enumerate(data_rows):
            # 跳過空白列
            if self._is_empty_row(row):
                print(f"第 {start_row + 1 + idx} 列是空白列,跳過")
                continue
            
            # 補齊或截斷欄位
            if len(row) < expected_columns:
                print(f"第 {start_row + 1 + idx} 列欄位不足: {len(row)} < {expected_columns},自動補齊")
                row.extend([''] * (expected_columns - len(row)))
            elif len(row) > expected_columns:
                print(f"第 {start_row + 1 + idx} 列欄位過多: {len(row)} > {expected_columns},自動截斷")
                row = row[:expected_columns]
            
            normalized_rows.append(row)
        
        return normalized_rows


    def _is_empty_row(self, row) -> bool:
        """檢查是否為空白列"""
        return all(not cell or str(cell).strip() == '' for cell in row)


    def _add_original_row_numbers(self, order_df, data_rows, start_row):
        """記錄原始列號"""
        actual_row_numbers = []
        for idx, row in enumerate(data_rows):
            if not self._is_empty_row(row):
                actual_row_numbers.append(start_row + 1 + idx)
        
        order_df['__original_row__'] = actual_row_numbers
        return order_df


    def _clean_dataframe(self, order_df):
        """清理 DataFrame"""
        # 移除完全空白的列
        order_df = order_df.dropna(how='all')
        
        # 移除所有欄位都是空字串的列
        order_df = order_df[order_df.apply(
            lambda row: row.astype(str).str.strip().ne('').any(), axis=1
        )]
        
        # 過濾報價數量大於0的資料
        if '報價數量' in order_df.columns:
            order_df['報價數量'] = order_df['報價數量'].astype(str).str.replace(',', '')
            order_df['報價數量'] = pd.to_numeric(order_df['報價數量'], errors='coerce').fillna(0)
            order_df = order_df[order_df['報價數量'] > 0]
        
        print(f"過濾後剩餘 {len(order_df)} 筆訂單")
        
        return order_df


    def _process_rich_text_specs(self, sheet, worksheet, headers):
        """處理規格欄位的富文本格式"""
        if '規格' not in headers:
            return
        
        spec_column_index = headers.index('規格')
        
        import string
        spec_column_letter = string.ascii_uppercase[spec_column_index]
        
        spreadsheet_id = sheet.id
        sheet_name = worksheet.title
        client = sheet.client
        
        for row_data in self.order:
            row_number = int(row_data['__original_row__'])
            cell_a1 = f'{spec_column_letter}{row_number}'
            
            # 取得富文本格式
            complete_text, text_runs = get_cell_rich_text_format(
                client, spreadsheet_id, sheet_name, cell_a1
            )
            
            # 轉換為 HTML 格式
            html_text = process_rich_text_with_styles_html(text_runs)
            
            # 儲存格式化文字
            row_data['規格_HTML'] = html_text
            row_data['規格_純文字'] = complete_text
            
            # 移除臨時欄位
            del row_data['__original_row__']


    def _validate_items(self):
        """驗證料件資料"""
        item_detail = []
        
        # 收集料件並檢查 BOM
        for per_order in self.order:
            item_id = per_order.get('item')
            if item_id:
                item_detail.append(item_id)
            
            # 檢查是否需要 BOM
            self._check_bom_requirement(per_order, item_id)
        
        if not item_detail:
            return
        
        # 檢查料件是否存在
        self._check_items_exist(item_detail)
        
        # 檢查客製化料件
        self._check_customized_items(item_detail)


    def _check_bom_requirement(self, per_order, item_id):
        """檢查料件是否需要 BOM"""
        item_category = per_order.get('category', '')
        must_bom = xin_tea_order_manage_summary_b_to_c.qry_item_category_must_bom(item_category)
        
        if must_bom:
            bom = per_order.get('用料清單單號', '')
            if not bom:
                self.error_message += (
                    f"料件:【{item_id}】類別:【{item_category}】"
                    f"為需要BOM的料件,但無BOM資料\n"
                )


    def _check_items_exist(self, item_detail):
        """檢查料件是否存在於主檔"""
        item_exist = xin_tea.qry_item_data_in_item(item_detail)
        existing_items = [item['item'] for item in item_exist] if item_exist else []
        missing_items = [item for item in item_detail if item not in existing_items]
        
        if missing_items:
            missing_items_str = ', '.join(missing_items)
            self.error_message += (
                f'料件主檔有誤,以下料件不存在: {missing_items_str},'
                f'請確認料件主檔是否建立完整\n'
            )


    def _check_customized_items(self, item_detail):
        """檢查客製化料件替換設定"""
        for per_order in self.order:
            customized_options = [
                per_order.get(f'客製化方案料件#{i}', '') 
                for i in range(1, 9)
            ]
            
            for per_item in item_detail:
                for per_cus in customized_options:
                    if not per_cus or not per_item:
                        continue
                    
                    check_replace = xin_tea.qry_customize_item_and_replace_item_in_bom(
                        per_cus, per_item
                    )
                    
                    if not check_replace:
                        self.error_message += (
                            f'客製料件替換料件有誤,客製料件:【{per_cus}】'
                            f'無法在BOM:【{per_item}】中找到對應被替換料件,'
                            f'請確認客製料件替換料件設定是否正確\n'
                        )

    def _check_item_spare_data(self):
        """檢查禮盒備用提袋資料"""
        for per_order in self.order:
            item_id = per_order.get('料號', '')
            print('檢查禮盒備用提袋資料: ', item_id)
            if item_id:
                item_exist = xin_tea.qry_item_data_in_item([item_id])
                print('料件資料: ', item_exist)
                if item_exist[0]['category'] == 'A':
                    spare_data = xin_tea.qry_item_spare_data_exist(item_id)
                    if not spare_data:
                        self.prompt_message += (
                            f'禮盒:【{item_id}】無對應備用提袋資料<br>'
                        )
    
    def __sleep(self):
        # 指數退避法 暫停時間
        sleep = math.pow(2, self.sleep)
        print(f"時間暫停秒數: ", sleep)
        time.sleep(sleep)
        if self.sleep < 6:
            self.sleep += 1


    def __choose_generate_vendor(self) -> str:
        """選擇生產廠商"""
        generate_vendor: list = xin_tea.qry_generate_vendor()
        can_generate_vendor: list = []
        
        total_amount: float = 0
        for per_order in self.order:
            total_amount += float(per_order.get('小計\n(含稅)').split('$')[1].replace(',', '') or 0)


        for per_vendor in generate_vendor:
            # 先取出優先權0廠商
            if per_vendor.get('pri_seq') == 0:
                can_generate_vendor.append({'vendor': per_vendor.get('vendor'), 'row_number': per_vendor.get('row_number')})
                continue
            # 判斷其他廠商是否可以作生產資格

            # 1. 金額
            money_condition = per_vendor.get('order_money').strip()
            money_match: bool = False
            # 情況1: 上下限 <99,>5000
            if ('<' in money_condition and '>' in money_condition and ',' in money_condition):
                print('情況1: 上下限')
                conditions = money_condition.split(',')
                
                for condition in conditions:
                    condition = condition.strip()
                    
                    if '<' in condition:
                        threshold = float(condition.replace('<', '').strip())
                        if total_amount < threshold:
                            money_match = True
                    elif '>' in condition:
                        threshold = float(condition.replace('>', '').strip())
                        if total_amount > threshold:
                            money_match = True
            # 情況2: 小於某金額 (<5000)
            elif '<' in money_condition and '>' not in money_condition:
                print('情況2: 小於某金額')
                threshold = float(money_condition.replace('<', '').strip())
                money_match = total_amount < threshold
            
            # 情況3: 大於某金額 (>5000)
            elif '>' in money_condition and '<' not in money_condition:
                print('情況3: 大於某金額')
                threshold = float(money_condition.replace('>', '').strip())
                money_match = total_amount > threshold
            
            # 情況4: 金額範圍 (5000-10000)
            elif '-' in money_condition and '<' not in money_condition and '>' not in money_condition:
                print('情況4: 金額範圍')
                min_val, max_val = map(float, money_condition.split('-'))
                money_match = min_val <= total_amount <= max_val
            
            # 情況5: 精確金額
            else:
                print('情況5: 精確金額')
                try:
                    threshold = float(money_condition)
                    money_match = total_amount == threshold
                except ValueError:
                    money_match = False
            if not money_match:
                # 金額不符合，跳下一個廠商
                continue
            # 2. 啟用日
            start_date: str = per_vendor.get('start_date')
            # 抓訂單確定日
            order_check_date: str = self.order_check_date
            order_check_date = order_check_date.replace('/', '-')
            # 加上調試輸出
            print(f"檢查廠商: {per_vendor.get('vendor')}")
            print(f"  start_date: {start_date} (type: {type(start_date)})")
            print(f"  order_check_date: {order_check_date} (type: {type(order_check_date)})")

            date_match: bool = False
            if start_date and order_check_date:
                try:
                    # 清理可能的空白
                    start_date_clean = str(start_date).strip()
                    order_check_date_clean = str(order_check_date).strip()
                    
                    start_date_obj = datetime.strptime(start_date_clean, '%Y-%m-%d').date()
                    order_check_date_obj = datetime.strptime(order_check_date_clean, '%Y-%m-%d').date()
                    
                    date_match = order_check_date_obj >= start_date_obj
                    
                    print(f"  日期解析成功:")
                    print(f"    start_date_obj: {start_date_obj}")
                    print(f"    order_check_date_obj: {order_check_date_obj}")
                    print(f"    date_match: {date_match}")
                    
                except ValueError as e:
                    print(f"  日期格式錯誤: {e}")
                    print(f"    start_date={start_date}, order_check_date={order_check_date}")
                    date_match = False
            else:
                print(f"  日期資料不完整 (start_date or order_check_date is empty)")

            if not date_match:
                # 啟用日不符合，跳下一個廠商
                print(f"  --> 跳過此廠商 (日期不符)")
                continue
            # 3. 料件是否都在該廠商料件對照表
            item_match: bool = True
            for per_order in self.order:
                item_id: str = str(per_order.get('禮盒料號')).strip()
                check_item_vendor: list = xin_tea.qry_item_vendor_reference(item_id, per_vendor.get('vendor'))
                if not check_item_vendor:
                    item_match = False
                    break
            if not item_match:
                # 料件不符合，跳下一個廠商
                continue
            # 全部條件符合，加入可生產廠商清單
            can_generate_vendor.append({'vendor': per_vendor.get('vendor'), 'row_number': per_vendor.get('row_number')})
        # 反向排序，優先權高的在前面
        can_generate_vendor = sorted(can_generate_vendor, key=lambda x: x['row_number'])
        return can_generate_vendor[0]['vendor']
    

def get_cell_format_native(client: gspread.Client, spreadsheet_id: str, sheet_id: int, cell_a1: str) -> Tuple[Optional[str], bool, Dict[str, float]]:
    """
    直接使用 gspread client 發送原生 HTTP 請求到 Sheets API，獲取格式資訊。
    
    Args:
        client: gspread.Client 物件。
        spreadsheet_id: 試算表 ID。
        sheet_id: 工作表 ID (gid)。
        cell_a1: 儲存格的 A1 表示法，例如 'E20'。

    Returns:
        (value, is_strikethrough, font_color_rgb)
    """
    
    base_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}'
    
    params = {
        'includeGridData': 'true', 
        'ranges': cell_a1,
        'fields': 'sheets(data(rowData(values(effectiveFormat,formattedValue))))'
    }

    try:
        # 使用 gspread 客戶端發送 GET 請求
        raw_response = client.request(
            'GET', 
            base_url, 
            params=params
        )

        if raw_response.status_code != 200:
             # 如果狀態碼不是 200，打印錯誤信息並返回空值
             print(f"原生 API 請求失敗，狀態碼: {raw_response.status_code}，響應內容: {raw_response.text}")
             return None, False, {}
             
        response_data = raw_response.json() # 使用 .json() 獲取 JSON 字典

        # 檢查是否存在數據
        if not response_data.get('sheets') or not response_data['sheets'][0].get('data'):
             return None, False, {}

        # 解析原生 API 響應結構：sheets[0].data[0].rowData[0].values[0]
        cell_data = response_data['sheets'][0]['data'][0]['rowData'][0]['values'][0]

        # 提取純文字值 (formattedValue)
        value = cell_data.get('formattedValue')

        # 提取格式資訊 (effectiveFormat)
        effective_format = cell_data.get('effectiveFormat', {})
        text_format = effective_format.get('textFormat', {})

        # 刪除線 (strikethrough): True/False
        is_strikethrough = text_format.get('strikethrough', False)

        # 文字顏色 (foregroundColor): RGB 字典 { 'red': float, 'green': float, 'blue': float }
        font_color_rgb = text_format.get('foregroundColor', {})

        return value, is_strikethrough, font_color_rgb

    except Exception as e:
        print(f"原生 API 請求發生錯誤: {e}")
        return None, False, {}
    

def process_rich_text_with_styles(text_runs: list) -> str:
    """
    處理富文本,保留所有文字內容
    
    Args:
        text_runs: 文字格式分段列表
        
    Returns:
        完整的文字字串(包含所有樣式的文字)
    """
    result_parts = []
    
    for run in text_runs:
        text = run['text']
        format_info = run['format']
        
        # 記錄格式資訊(用於除錯)
        is_strikethrough = format_info.get('strikethrough', False)
        fg_color = format_info.get('foregroundColor', {})
        
        if is_strikethrough:
            print(f"[包含刪除線]: {text[:50]}...")
        
        if fg_color:
            r = int(fg_color.get('red', 0) * 255)
            g = int(fg_color.get('green', 0) * 255)
            b = int(fg_color.get('blue', 0) * 255)
            print(f"[顏色 RGB({r},{g},{b})]: {text[:50]}...")
        
        # 保留所有文字,不做任何過濾
        result_parts.append(text)
    
    return ''.join(result_parts)

def get_cell_rich_text_format(
    client: gspread.Client, 
    spreadsheet_id: str, 
    sheet_name: str,
    cell_a1: str
) -> Tuple[Optional[str], list]:
    """
    取得儲存格的富文本格式（包含部分文字的樣式）
    
    Returns:
        (complete_text, text_runs)
        text_runs 格式: [
            {
                'text': '文字內容',
                'format': {
                    'bold': True/False,
                    'strikethrough': True/False,
                    'foregroundColor': {'red': 0-1, 'green': 0-1, 'blue': 0-1}
                }
            },
            ...
        ]
    """
    
    base_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}'
    range_notation = f"'{sheet_name}'!{cell_a1}"
    
    params = {
        'includeGridData': 'true', 
        'ranges': range_notation,
        # 關鍵：要取得 textFormatRuns（富文本格式）
        'fields': 'sheets(data(rowData(values(formattedValue,textFormatRuns,effectiveFormat))))'
    }

    try:
        raw_response = client.request('GET', base_url, params=params)

        if raw_response.status_code != 200:
            print(f"API 請求失敗: {raw_response.status_code}")
            print(f"響應內容: {raw_response.text}")
            return None, []
             
        response_data = raw_response.json()
        
        # 檢查資料結構
        if not (response_data.get('sheets') and 
                response_data['sheets'][0].get('data') and
                response_data['sheets'][0]['data'][0].get('rowData') and
                response_data['sheets'][0]['data'][0]['rowData'][0].get('values')):
            print("找不到儲存格資料")
            return None, []

        cell_data = response_data['sheets'][0]['data'][0]['rowData'][0]['values'][0]
        
        # 完整文字
        complete_text = cell_data.get('formattedValue', '')
        
        # 富文本格式（textFormatRuns）
        text_format_runs = cell_data.get('textFormatRuns', [])
        
        # 如果沒有 textFormatRuns，表示整個儲存格使用相同格式
        if not text_format_runs:
            effective_format = cell_data.get('effectiveFormat', {})
            text_format = effective_format.get('textFormat', {})
            
            return complete_text, [{
                'text': complete_text,
                'format': {
                    'bold': text_format.get('bold', False),
                    'italic': text_format.get('italic', False),
                    'strikethrough': text_format.get('strikethrough', False),
                    'underline': text_format.get('underline', False),
                    'foregroundColor': text_format.get('foregroundColor', {})
                }
            }]
        
        # 解析 textFormatRuns
        parsed_runs = []
        for i, run in enumerate(text_format_runs):
            start_index = run.get('startIndex', 0)
            
            # 計算結束位置
            if i + 1 < len(text_format_runs):
                end_index = text_format_runs[i + 1].get('startIndex')
            else:
                end_index = len(complete_text)
            
            # 提取該段文字
            text_segment = complete_text[start_index:end_index]
            
            # 提取格式
            text_format = run.get('format', {})
            
            parsed_runs.append({
                'text': text_segment,
                'format': {
                    'bold': text_format.get('bold', False),
                    'italic': text_format.get('italic', False),
                    'strikethrough': text_format.get('strikethrough', False),
                    'underline': text_format.get('underline', False),
                    'foregroundColor': text_format.get('foregroundColor', {}),
                    'fontSize': text_format.get('fontSize'),
                    'fontFamily': text_format.get('fontFamily')
                }
            })
        
        return complete_text, parsed_runs

    except Exception as e:
        print(f"API 請求錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None, []
    

def process_rich_text_with_styles_html(text_runs: list) -> str:
    """
    處理富文本，輸出為 HTML 格式（保留所有樣式）
    
    Args:
        text_runs: 文字格式分段列表
        
    Returns:
        HTML 格式的文字字串
    """
    html_parts = []
    
    for run in text_runs:
        text = run['text']
        format_info = run['format']
        
        # 取得樣式
        is_bold = format_info.get('bold', False)
        is_italic = format_info.get('italic', False)
        is_strikethrough = format_info.get('strikethrough', False)
        is_underline = format_info.get('underline', False)
        fg_color = format_info.get('foregroundColor', {})
        
        # 建立 CSS 樣式
        styles = []
        
        # 處理文字（換行符號轉為 <br>）
        text = text.replace('\n', '<br>')
        
        # 顏色
        if fg_color and any(fg_color.values()):
            r = int(fg_color.get('red', 0) * 255)
            g = int(fg_color.get('green', 0) * 255)
            b = int(fg_color.get('blue', 0) * 255)
            styles.append(f'color: rgb({r}, {g}, {b})')
        
        # 字體大小
        font_size = format_info.get('fontSize')
        if font_size:
            styles.append(f'font-size: {font_size}pt')
        
        # 組合樣式
        style_str = '; '.join(styles) if styles else ''
        
        # 套用 HTML 標籤
        if is_bold:
            text = f"<strong>{text}</strong>"
        if is_italic:
            text = f"<em>{text}</em>"
        if is_strikethrough:
            text = f"<del>{text}</del>"
        if is_underline:
            text = f"<u>{text}</u>"
        if style_str:
            text = f'<span style="{style_str}">{text}</span>'
        
        html_parts.append(text)
    
    return ''.join(html_parts)



if __name__ == '__main__':
    UpdateSpecificBtoBGsSqV2('https://docs.google.com/spreadsheets/d/14kRyrny6deOfYUGbsjnLZUzXRrt2hvaF2GpgDaF0R7s/edit?gid=487771632#gid=487771632').process_data()   