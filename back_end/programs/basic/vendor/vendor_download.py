import datetime
from openpyxl import Workbook

def download_vendor_excel(vendor: list) -> str:
    """
    產生廠商資料Excel
    :param customer: list 廠商資料
    """
    try:
        wb = Workbook()
        ws = wb.active
        ws.append([
            "系統用代號", "合併收尋欄", "廠商代號", "廠商簡稱", "廠商抬頭", "耗料倉別", "入庫倉別", "廠商窗口", "廠商電話", "廠商地址含郵遞區號", 
            "廠商信箱", "發票寄送方式", "付款方式", "運費規則", "委託人", "委託人電話", "委託人地址", "發單者公司_是否透露公司名字", 
            "發票收件人", "發票收件電話", "發票收件資訊", "幣別", "稅別", "外加稅金率", "商品價格_交期表_MOQ", "廠商統編", "交期", 
            "付款日期", "往來銀行", "往來銀行帳號", "單號", "下單方式", "代工暨採購說明文件連結", "注意事項", "廠商存摺影本連結", 
            "更新至主檔日", "審核主管", "申請者"
        ])
        for per_vendor in vendor:
            ws.append([
                per_vendor.get('sys_id'), per_vendor.get('vendor_id'), per_vendor.get('vendor_name'),
                per_vendor.get('vendor_title'), per_vendor.get('consume_warehouse'), per_vendor.get('inventory_in_warehouse'),
                per_vendor.get('vendor_window'), per_vendor.get('vendor_phone'), per_vendor.get('vendor_address'),
                per_vendor.get('vendor_email'), per_vendor.get('invoice_send'), per_vendor.get('payment_type'),
                per_vendor.get('payment_time'), per_vendor.get('freight_rule'), per_vendor.get('client'),
                per_vendor.get('client_phone'), per_vendor.get('client_address'), per_vendor.get('crt_form'),
                per_vendor.get('invoice_recipient'), per_vendor.get('invoice_receipt_phone'), per_vendor.get('invoice_receipt_information'),
                per_vendor.get('currency_type'), per_vendor.get('tax_type'), per_vendor.get('additional_tax'),
                per_vendor.get('moq'), per_vendor.get('vendor_uniform_invoice_no'), per_vendor.get('delivery_date'),
                per_vendor.get('payment_date'), per_vendor.get('bank'), per_vendor.get('bank_account'),
                per_vendor.get('bpm_form_id'), per_vendor.get('create_form_type'), per_vendor.get('oem_file_url'),
                per_vendor.get('note'), per_vendor.get('vendor_passbook'), per_vendor.get('upd_date'),
                per_vendor.get('audit_supervisior'), per_vendor.get('application')
            ])
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_name: str = f"廠商_{timestamp}.xlsx"
        wb.save(file_name)
        return file_name
    except:
        return ''