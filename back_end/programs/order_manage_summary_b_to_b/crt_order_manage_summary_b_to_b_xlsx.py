from openpyxl import Workbook
from datetime import datetime


def crt_order_manage_summary_b_to_b_xlsx(data: list) -> str:
    """
    產生訂單管理總表(B to B)excel
    :param data: 訂單管理總表資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        '報價名稱', '客戶簡稱',
         # '規格調整', '訂單更新提醒', 
        'BPM訂單單號',
        'BPM訂單狀態', 'BPM生產單號', 'BPM生產單狀態', '分線',
        '生產廠商(生產單用)', '出庫倉別(生產單用)', '最早到貨日(生產單用)',
        '最晚到貨日(生產單用)', '包裝說明連結(生產單用)',
        '配送批次', '訂單數量', '已分配量', '差異數',
        #'生產廠商', '出庫倉別', 
        '料號', '料件類別', '品名', '規格',
        '客製規格描述(給包裝單位看的訊息)', '單價原價', 
        '優惠折數%(100以內數字)', '單件優惠價(含稅)', '訂單金額 (含稅)',
        '標準/客製', '用料清單單號', '採購單連接', '產品說明1', '產品說明2',
        '備註', '心茶備註', '訂單開立日期', '客戶窗口慣用聯繫方式',
        '報價單連結', '下訂憑證連結', '客戶預計決策日', '最早到貨日',
        '最晚到貨日', '公司抬頭', '客戶統編', '客戶地址含郵遞區號',
        '客戶窗口', '客戶電話', '客戶信箱', '付款條件', '付款方式',
        '電子發票', '配送方式', '訂單備註', '心茶聯絡人', '心茶聯絡電話',
        '心茶聯絡信箱', '是否為客製化訂單', '商品與客製服務金額',
        '訂單金額取值', '運費單件金額', '運費數量', '優惠折數',
        '運費優惠價', '總運費', '總運費+商品與客製服務金額',
        '付款手續費(%)(100以內數字)', '付款手續費優惠(%)(100以內數字)',
        '付款手續費小計金額', '總運費+商品與客製服務金額+付款手續費',
        '配送單', '訂單數量(全部總計)', '訂單類別', '心茶訂單key值', '訂單更新時間',
        '訂單匯入時間', 'BPM訂單更新時間', 'BPM生產單更新時間'
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('sales_quotation_name', ''), per.get('customer_name', ''), per.get('bpm_form_id', ''),
                per.get('bpm_form_status', ''), per.get('bpm_generate_id'),
                per.get('bpm_generate_status', ''), per.get('branch_line', ''),
                per.get('generate_vendor_by_generate', ''), per.get('shipping_out_warehouse_by_generate', ''),
                per.get('earliest_arrival_date_by_generate', ''), per.get('latest_arrival_date_by_generate', ''),
                per.get('package_descript_file', ''),
                per.get('item_batch', ''), float(per.get('quantity') or 0),
                per.get('different', ''), float(per.get('quantity') or 0)-float(per.get('different') or 0),
                # per.get('generate_vendor', ''), per.get('shipping_out_warehouse'),
                per.get('item', ''), per.get('category', ''),
                per.get('item_name', ''), per.get('item_specific', ''),
                per.get('customization_descript', ''), per.get('unit_price', ''),
                per.get('discount1', ''), per.get('one_discount', ''),
                per.get('order_money', ''), per.get('standard_or_customization', ''),
                per.get('bom', ''), per.get('purchase_connect', ''), per.get('product_descript_one', ''),
                per.get('product_descript_two', ''), per.get('detail_remark', ''),
                per.get('xin_tea_remark', ''), per.get('order_issue_date', ''),
                per.get('customer_contact', ''), per.get('sales_quotation_url', ''),
                per.get('order_invoice_url', ''), per.get('customer_estimate_decide_date', ''),
                per.get('earliest_arrival_date', ''), per.get('latest_arrival_date', ''),
                per.get('company_title', ''),
                per.get('uniform_invoice_no', ''), per.get('address', ''),
                per.get('customer_window', ''), per.get('customer_phone', ''),
                per.get('customer_email', ''), per.get('payment_term', ''),
                per.get('payment', ''), per.get('ele_invoice', ''), per.get('delivery_method', ''),
                per.get('order_remark', ''), per.get('xin_tea_connector', ''),
                per.get('xin_tea_connect_phone', ''), per.get('xin_tea_connect_email', ''),
                per.get('customization_order', ''), per.get('product_and_customization_money', ''),
                per.get('check_money', ''), per.get('freight_per_piece_money', ''), per.get('freight_amount', ''),
                per.get('discount', ''), per.get('freight_discount', ''), per.get('total_freight', ''),
                per.get('product_and_customization_and_freight_money', ''), per.get('payment_processing_fee', ''),
                per.get('payment_processing_fee_discount', ''),
                per.get('total_payment_processing_fee', ''), per.get('final_total', ''), 
                per.get('delivery_order', ''), per.get('total_order_num', ''), per.get('order_type', ''), per.get('order_key', ''), 
                per.get('modify_time', ''), per.get('import_time', ''), per.get('generate_bpm_form', ''),
                per.get('generate_bpm_generate', '')
            ])
    file_name: str = f"訂單管理總表B2B_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name