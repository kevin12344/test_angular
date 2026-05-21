from openpyxl import Workbook
from datetime import datetime


def crt_inventory_form_diff_xlsx(data: list) -> str:
    """
    產生庫存表單差異excel
    :param data: 庫存表單差異資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append(['單號', '差異原因'])
    if len(data) > 0:
        for per in data:
            sheet1.append([
                per.get('bpm_form_id', ''), per.get('status', '')
            ])
    file_name: str = f"庫存差異表單_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name