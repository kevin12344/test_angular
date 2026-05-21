import datetime
from openpyxl import Workbook

def download_customer_excel(customer: list) -> str:
    """
    產生客戶資料Excel
    :param customer: list 客戶資料
    """
    try:
        wb = Workbook()
        ws = wb.active
        ws.append(["系統用代號", "合併收尋欄", "客戶代號", 
                "客戶簡稱", "公司抬頭", "客戶統編", "客戶地址含郵遞區號", 
                "客戶窗口", "客戶電話", "客戶信箱", "付款條件", 
                "付款方式", "往來銀行", "往來分行", "往來銀行帳號", 
                "幣別", "運送方式", "運費", "單號"])
        for per_customer in customer:
            ws.append([
                per_customer.get('sys_id'), per_customer.get('customer_id'),
                per_customer.get('customer_name'), per_customer.get('customer_title'),
                per_customer.get('customer_uniform_invoice_no'), per_customer.get('customer_address'),
                per_customer.get('customer_window'), per_customer.get('customer_phone'),
                per_customer.get('customer_email'), per_customer.get('payment_term'),
                per_customer.get('payment_type'), per_customer.get('bank'),
                per_customer.get('bank_branch'), per_customer.get('bank_account'),
                per_customer.get('currency_type'), per_customer.get('freight_type'),
                per_customer.get('freight'), per_customer.get('bpm_form_id')
            ])
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_name: str = f"客戶_{timestamp}.xlsx"
        wb.save(file_name)
        return file_name
    except:
        return ''