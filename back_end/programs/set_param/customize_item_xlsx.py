from openpyxl import Workbook
from datetime import datetime


def crt_customize_item_xlsx(data: list) -> str:
    """
    產生可客製料件excel
    :param data: 料件參照表資料
    """
    workbook = Workbook()
    
    # Sheet1: 上傳檔案格式
    sheet1 = workbook.active
    sheet1.append([
        '客製化料號'
    ])
    for per in data:
        sheet1.append([
           per.get('item', '')
        ])

    file_name: str = f"現有可客製料件_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name