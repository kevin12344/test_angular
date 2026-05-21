from openpyxl import Workbook
from datetime import datetime

def crt_use_item_detail_xlsx(data: list) -> str:
    """
    產出用料明細excel
    :param data: 用料明細資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        "生產單號", "訂單完成時間", "最早到貨日", "最晚到貨日",
        "出貨日期", "生產料號", "生產品名", "預計生產數量",
        "客製或標準", "客製規格描述", "訂單備註", "母件料號",
        "母件品名", "子件用料", "子件品名", "子件用量", "預計耗用量",
        "客製化料件", "uu1", "訂單單號", "客戶簡稱", "生產廠商",
        "生產狀態", "每單位代工費未稅", "其他費用未稅", "代墊運費含稅",
        "總費用未稅", "完工數量"
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('order_key', ''), per.get('complete_time', ''),
                per.get('earliest_arrival_date', ''), per.get('latest_arrival_date', ''),
                per.get('shipping_date', ''), per.get('item', ''), per.get('item_name', ''),
                per.get('estimate_generate', ''), per.get('customize_or_normal', ''), per.get('customize_specific', ''),
                per.get('order_remark', ''), per.get('m_item', ''), per.get('m_item_name', ''),
                per.get('s_item', ''), per.get('s_item_name', ''), per.get('s_item_use', ''),
                per.get('estimate_use', ''), per.get('customize_item', ''), per.get('uu_one', ''),
                per.get('order_key', ''),   per.get('customer', ''), per.get('generate_vendor', ''),
                per.get('status', ''), per.get('oem_fee', ''), per.get('other_expense', ''),
                per.get('advance_expenses', ''), per.get('total_expense', ''), per.get('estimate_generate', '') 
            ])
    file_name: str = f"用料明細_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name