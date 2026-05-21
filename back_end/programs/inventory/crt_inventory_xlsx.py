from openpyxl import Workbook
from datetime import datetime


def crt_inventory_detail_xlsx(data: list) -> str:
    """
    產生庫存明細excel
    :param data: 庫存明細資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        'item', 'itemName', 'unit', '庫存數量', '系統單號', 'key1', 'key', '倉別',
        '開立日期'
    ])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('s_item', ''), per.get('s_item_name', ''), per.get('unit', ''),
                per.get('estimate_cost_quantity', ''), per.get('bpm_form_id', ''),
                per.get('key1', ''), per.get('key_word', ''), per.get('cost_warehouse', ''),
                per.get('issue_date', '')
            ])
    file_name: str = f"庫存明細_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name