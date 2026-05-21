from openpyxl import Workbook
from datetime import datetime


def crt_item_reference_xlsx(data: list) -> str:
    """
    產生料件參照表excel
    :param data: 料件參照表資料
    """
    workbook = Workbook()
    
    # Sheet1: 上傳檔案格式
    sheet1 = workbook.active
    sheet1.title = "上傳檔案格式"
    sheet1.append([
        '料件', '品名', '單位', '廠商', '是/否'
    ])
    
    # Sheet2: 料件參照表資料
    sheet2 = workbook.create_sheet("料件參照表")
    sheet2.append([
        '料件', '品名', '單位', '廠商', '是/否'
    ])
    
    if len(data) > 0:
        for per in data:
            yes_or_no: str = '是' if per.get('relationship', '') == '1' else '否'
            sheet2.append([
               per.get('item_id', ''), per.get('item_name', ''), per.get('unit', ''),
               per.get('vendor_name', ''), yes_or_no
            ])
    
    file_name: str = f"料件參照表_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.xlsx"
    workbook.save(file_name)
    return file_name