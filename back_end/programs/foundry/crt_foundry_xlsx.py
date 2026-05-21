from openpyxl import Workbook
from datetime import datetime


def crt_foundry_xlsx(data: list) -> str:
    """
    產生代工廠大表excel
    :param data: 代工廠大表資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        "最早到貨日", "子件料號", "子件品名", 
        "生產狀態", "廠商", "預計耗用量"
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('earliest_arrival_date', ''),per.get('s_item', ''),
                per.get('s_item_name', ''), per.get('generate_status', ''),
                per.get('generate_vendor', ''), per.get('total_estimate_use', '')
            ])
    file_name: str = f"代工廠大表_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name