from openpyxl import Workbook
from datetime import datetime
from openpyxl.styles import NamedStyle

def crt_order_delivery_detail_xlsx(data: list) -> str:
    """
    產生訂單配送明細excel
    :param data: 訂單配送明細資料
    """
    workbook = Workbook()
    
    # 定義文字格式樣式
    text_style = NamedStyle(name="text_style")
    text_style.number_format = "@"

    sheet1 = workbook.active
    sheet1.append([
        "廠商訂單確認", "訂單狀態", "訂單key值", "拋轉時間",
        "分線", "心茶備註", "拋單生產日期(實際給包裝廠的日期)",
        "最早到貨日(異動訂單也要更新)(客戶的需求)", "生產廠商", "出庫倉別",  
        "配送廠商", "電商平台訂單單號", "物流方式",
        "收件人", "收件人電話", "收件人地址", "數量", "料號", "EIP品名", "拋轉人員"
    ])
    if len(data) > 0:
        for per in data:
            row = [
                per.get('vendor_check', ''),
                per.get('vendor_order_status', ''),
                per.get('order_key', ''),
                per.get('import_date', ''),
                per.get('branch_line', ''),
                per.get('xin_tea_remark', ''),
                per.get('to_order_generate_date', ''),
                per.get('earliest_arrival_date', ''),
                per.get('generate_vendor', ''),
                per.get('shipping_out_warehouse', ''),
                per.get('delivery_vendor', ''),
                per.get('e_commerce_platform_order_no'),
                per.get('logistics_method', ''),
                per.get('recipient', ''),
                str(per.get('recipient_phone', '')),  # 確保電話號碼是字串
                per.get('recipient_address', ''),
                per.get('quantity', ''),
                per.get('item', ''),
                per.get('product_name', ''),
                per.get('importer', '')
            ]
            sheet1.append(row)

    # 將「收件人電話」欄位設為文字格式
    for row in sheet1.iter_rows(min_row=2, min_col=15, max_col=15):
        for cell in row:
            cell.number_format = "@"

    file_name: str = f"訂單配送明細_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name