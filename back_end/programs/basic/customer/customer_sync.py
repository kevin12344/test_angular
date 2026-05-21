import pandas as pd
import time
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.db_process.xin_tea.basic.customer import main as xin_tea_basic_customer

def exe_customer_sync() -> bool:
    """
    同步客戶資料
    """
    sheet = google_certificate(
            'https://docs.google.com/spreadsheets/d/1BCAWGAmFbAIqAbiwuzEACIEK8Pp48GvV2S5cZJVxzqc/edit?gid=1997023834#gid=1997023834')
    worksheet = sheet.get_worksheet(0)
    customer_df = pd.DataFrame(worksheet.get_all_records())
    customer: list = customer_df.to_dict(orient='records')
    customer_add: list = []
    customer_upd: list = []
    for per_customer in customer:
        customer_phone = str(per_customer.get('客戶電話', '')).strip()
        if customer_phone.isdigit() and len(customer_phone) < 10:
            customer_phone = customer_phone.zfill(10)
        uniform_invoice_no: str = str(per_customer.get('客戶統編', '')).strip()
        if uniform_invoice_no.isdigit() and len(uniform_invoice_no) < 8:
            uniform_invoice_no = uniform_invoice_no.zfill(8)
        if len(per_customer.get('客戶簡稱')) > 0:
            # 判斷客戶是否存在
            customer: list = xin_tea_basic_customer.qry_customer_exist(str(per_customer.get('客戶代號')).strip())
            if len(customer) == 0:
                # 新增客戶
                customer_add.append((
                    per_customer.get('系統用代號', ''), str(per_customer.get('客戶代號', '')).strip(), str(per_customer.get('客戶簡稱', '')).strip(),
                    str(per_customer.get('公司抬頭', '')).strip(), uniform_invoice_no, str(per_customer.get('客戶地址含郵遞區號', '')).strip(),
                    per_customer.get('客戶窗口', ''), customer_phone, str(per_customer.get('客戶信箱', '')).strip(),
                    per_customer.get('付款條件', ''), per_customer.get('付款方式', ''), per_customer.get('往來銀行', ''), per_customer.get('往來分行', ''),
                    per_customer.get('往來銀行帳號', ''), per_customer.get('幣別', ''), per_customer.get('運送方式', ''), per_customer.get('運費', ''), per_customer.get('單號', '') 
                ))
            else:
                # 更新客戶
                customer_upd.append((
                    str(per_customer.get('客戶簡稱', '')).strip(),
                    str(per_customer.get('公司抬頭', '')).strip(), uniform_invoice_no, str(per_customer.get('客戶地址含郵遞區號', '')).strip(),
                    per_customer.get('客戶窗口', ''), customer_phone, str(per_customer.get('客戶信箱', '')).strip(),
                    per_customer.get('付款條件', ''), per_customer.get('付款方式', ''), per_customer.get('往來銀行', ''), per_customer.get('往來分行', ''),
                    per_customer.get('往來銀行帳號', ''), per_customer.get('幣別', ''), per_customer.get('運送方式', ''), per_customer.get('運費', ''), per_customer.get('單號', ''),
                    str(per_customer.get('客戶代號', '')).strip()
                ))
    result: bool = xin_tea_basic_customer.customer_sync(customer_add, customer_upd)
    return result
    