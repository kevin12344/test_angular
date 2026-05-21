from openpyxl import Workbook
from datetime import datetime


def crt_vendor_order_check_xlsx(data: list) -> str:
    """
    產生廠商訂單確認excel
    :param data: 廠商訂單確認資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        "廠商訂單確認", "訂單狀態", "訂單key值", "拋轉時間",
        "分線", "心茶備註", "製作許可日(實際給包裝廠的日期)",
        "最早可出廠日", "電商平台訂單單號", "生產廠商", 
        "出庫倉別", "配送廠商", "物流方式", 
        "收件人", "收件人電話", "收件人地址", "數量", "料號",
        "EIP品名", "拋轉人員"
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('vendor_check', ''),
                per.get('vendor_order_status', ''),
                per.get('order_key', ''),
                per.get('import_date', ''),
                per.get('branch_line', ''),
                per.get('xin_tea_remark', ''),
                per.get('to_order_generate_date', ''),
                per.get('earliest_arrival_date', ''),
                per.get('e_commerce_platform_order_no'),
                per.get('generate_vendor', ''),
                per.get('shipping_out_warehouse', ''),
                per.get('delivery_vendor', ''),
                per.get('logistics_method', ''),
                per.get('recipient', ''),
                per.get('receipient_phone', ''),
                per.get('recipient_address', ''),
                per.get('quantity', ''),
                per.get('item', ''),
                per.get('product_name', ''),
                per.get('importer', '')
            ])
    file_name: str = f"廠商訂單確認_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name