from openpyxl import Workbook
from datetime import datetime


def crt_order_manage_summary_b_to_c_xlsx(data: list) -> str:
    """
    產生訂單管理總表excel
    :param data: 訂單管理總表資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        "心茶訂單key值", "狀態", "廠商訂單狀態", "廠商確認", "完成訂單匯入異常", 
        "新訂單訂單狀態", "分線", "電商平台", "檢查結果", 
        "白名單管理同單號不同生產廠商同單號不同出貨日", "是否檢查備註欄訊息", 
        "心茶備註", "訂單備註和出貨備註客服後勤出貨溝通管控表",  
        "製作許可日(實際給包裝廠的日期)", "最早可出廠日", "最早到貨日(異動訂單也要更新)(客戶的需求)", 
        "生產廠商", "出庫倉別", "配送廠商", "數量", "拆單前單號", 
        "電商平台訂單單號", "電商平台訂單日期", "新訂單_付款狀態", "物流方式", 
        "料號", "EIP品名", "料件類別", "用料清單單號", "各平台品名", "各平台規格", 
        "收件人", "收件人電話", "收件人地址", "收件人Email", "付款方式", "原幣金額", 
        "匯率", "幣別", "訂單金額", "發票抬頭", "統一編號", "到貨區間", 
        "最後修改人員", "最後修改時間", "最後展算時間", "最後拋轉廠商時間"
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('order_key', ''),
                per.get('status', ''),
                per.get('vendor_order_status', ''),
                per.get('vendor_check', ''),
                per.get('complete_order_error', ''),
                per.get('new_order_order_status', ''),
                per.get('branch_line', ''),
                per.get('e_commerce_platform', ''),
                per.get('check_message', ''),
                per.get('white_list_process', ''),
                per.get('is_check_remark_message', ''),
                per.get('xin_tea_remark', ''),
                per.get('order_remark_or_shipping_remark', ''),
                per.get('to_order_generate_date', ''),
                per.get('latest_arrival_date', ''),
                per.get('earliest_arrival_date', ''),
                per.get('generate_vendor', ''),
                per.get('shipping_out_warehouse', ''),
                per.get('delivery_vendor', ''),
                per.get('quantity', ''),
                per.get('split_berfore_order_no', ''),
                per.get('e_commerce_platform_order_no', ''),
                per.get('e_commerce_platform_order_date', ''),
                per.get('new_order_payment_status', ''),
                per.get('logistics_method', ''),
                per.get('item', ''),
                per.get('product_name', ''),
                per.get('item_category', ''),
                per.get('bom_bpm_form_id', ''),
                per.get('platform_product_name', ''),
                per.get('platform_specific', ''),
                per.get('recipient', ''),
                per.get('recipient_phone', ''),
                per.get('recipient_address', ''),
                per.get('recipient_email', ''),
                per.get('payment_term', ''),
                per.get('original_money', ''),
                per.get('exchange', ''),
                per.get('currency_type', ''),
                per.get('order_money', ''),
                per.get('invoice_title', ''),
                per.get('uniform_invoice_no', ''),
                per.get('arrival_area', ''),
                per.get('importer', ''),
                per.get('import_date', ''),
                per.get('spread_calculate_time', ''),
                per.get('to_vendor_time', '')
            ])
    file_name: str = f"訂單管理總表B2C_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name