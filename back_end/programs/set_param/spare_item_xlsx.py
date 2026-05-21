from openpyxl import Workbook
from datetime import datetime


def crt_spare_item_xlsx(data: list) -> str:
    """
    產生備用料件excel
    :param data: 料件參照表資料
    """
    workbook = Workbook()
    sheet1 = workbook.active
    sheet1.append([
        '禮盒料號', '客製化', '備用料號', '滿多少加X'
    ])
    for per in data:
        sheet1.append([
           per.get('item', ''), per.get('customize_or_standard', ''), per.get('spare_item', ''), per.get('full_num_additional_add', '')
        ])

    file_name: str = f"現有備用料件_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name