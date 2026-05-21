from openpyxl import Workbook
from datetime import datetime


def crt_item_detail_in_out_xlsx(data: list) -> str:
    """
    產生出入明細excel
    :param data: 代工廠大表資料
    """
    workbook = Workbook()
    print('data', data)
    sheet1 = workbook.active
    sheet1.append([
        'key', 'item', 'itemName', 'unit', '庫存數量', '倉別'
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('complete_time', ''), per.get('s_item', ''),
                per.get('s_item_name', ''), per.get('unit', ''),
                per.get('total_estimate_use', ''), per.get('shipping_out_warehouse', '')
            ])
    file_name: str = f"出入明細_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name