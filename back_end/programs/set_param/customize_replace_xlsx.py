from openpyxl import Workbook
from datetime import datetime


def crt_customize_replace_xlsx(data: list) -> str:
    """
    產生客製料件替換excel
    :param data: 料件參照表資料
    """
    workbook = Workbook()
    
    sheet1 = workbook.active
    sheet1.append([
        '客製化料號', '需扣掉料號'
    ])
    for per in data:
        sheet1.append([
           per.get('customize_item', ''), per.get('replace_item', '')
        ])

    file_name: str = f"現有客製料件替換_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name