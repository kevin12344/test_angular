import pandas as pd
import time
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.db_process.xin_tea.basic.vendor import main as xin_tea_basic_vendor

def exe_vendor_sync() -> bool:
    """
    同步廠商資料
    """
    sheet = google_certificate(
            'https://docs.google.com/spreadsheets/d/1BCAWGAmFbAIqAbiwuzEACIEK8Pp48GvV2S5cZJVxzqc/edit?gid=1997023834#gid=1997023834')
    worksheet = sheet.get_worksheet(1)
    vendor_df = pd.DataFrame(worksheet.get_all_records())
    vendor: list = vendor_df.to_dict(orient='records')
    vendor_add: list = []
    vendor_upd: list = []
    for per_vendor in vendor:
        # 判斷客戶是否存在
        if len(per_vendor.get('廠商代號')) == 0:
            continue
        vendor: list = xin_tea_basic_vendor.qry_vendor_exist(str(per_vendor.get('廠商代號')).strip())
        if len(vendor) == 0:
            # 新增廠商
            vendor_add.append((
                str(per_vendor.get('系統用代號', '')).strip(), str(per_vendor.get('廠商代號', '')).strip(),
                str(per_vendor.get('廠商簡稱', '')).strip(), str(per_vendor.get('廠商抬頭', '')).strip(),
                str(per_vendor.get('耗料倉別', '')).strip(), str(per_vendor.get('入庫倉別', '')).strip(), str(per_vendor.get('廠商窗口', '')).strip(),
                str(per_vendor.get('廠商電話', '')).strip(), str(per_vendor.get('廠商地址含郵遞區號', '')).strip(),
                str(per_vendor.get('廠商信箱', '')).strip(), str(per_vendor.get('發票寄送方式', '')).strip(),
                str(per_vendor.get('付款方式', '')).strip(), str(per_vendor.get('付款時間', '')).strip(),
                str(per_vendor.get('運費規則', '')).strip(), str(per_vendor.get('委託人', '')).strip(), str(per_vendor.get('委託人電話', '')).strip(),
                str(per_vendor.get('委託人地址', '')).strip(), str(per_vendor.get('發單者公司_是否透露公司名字', '')).strip(),
                str(per_vendor.get('發票收件人', '')).strip(), str(per_vendor.get('發票收件電話', '')).strip(),
                str(per_vendor.get('發票收件資訊', '')).strip(), str(per_vendor.get('幣別', '')).strip(),
                str(per_vendor.get('稅別', '')).strip(), float(per_vendor.get('外加稅金率') or 0 ), str(per_vendor.get('商品價格_交期表_MOQ', '')).strip(),
                str(per_vendor.get('廠商統編', '')).strip(), str(per_vendor.get('交期', '')).strip(), str(per_vendor.get('付款日期', '')).strip(),
                str(per_vendor.get('往來銀行', '')).strip(), str(per_vendor.get('往來銀行帳號', '')),
                str(per_vendor.get('單號', '')).strip(), str(per_vendor.get('下單方式', '')).strip(), str(per_vendor.get('代工暨採購說明文件連結')).strip(),
                str(per_vendor.get('注意事項', '')).strip(), str(per_vendor.get('廠商存摺影本連結', '')).strip(), per_vendor.get('更新至主檔日'),
                str(per_vendor.get('審核主管', '')), str(per_vendor.get('申請者', '')).strip()
            ))
        else:
            # 更新廠商
            vendor_upd.append((
                str(per_vendor.get('廠商簡稱', '')).strip(), str(per_vendor.get('廠商抬頭', '')).strip(),
                str(per_vendor.get('耗料倉別', '')).strip(), str(per_vendor.get('入庫倉別', '')).strip(), str(per_vendor.get('廠商窗口', '')).strip(),
                str(per_vendor.get('廠商電話', '')).strip(), str(per_vendor.get('廠商地址含郵遞區號', '')).strip(),
                str(per_vendor.get('廠商信箱', '')).strip(), str(per_vendor.get('發票寄送方式', '')).strip(),
                str(per_vendor.get('付款方式', '')).strip(), str(per_vendor.get('付款時間', '')).strip(),
                str(per_vendor.get('運費規則', '')).strip(), str(per_vendor.get('委託人', '')).strip(), str(per_vendor.get('委託人電話', '')).strip(),
                str(per_vendor.get('委託人地址', '')).strip(), str(per_vendor.get('發單者公司_是否透露公司名字', '')).strip(),
                str(per_vendor.get('發票收件人', '')).strip(), str(per_vendor.get('發票收件電話', '')).strip(),
                str(per_vendor.get('發票收件資訊', '')).strip(), str(per_vendor.get('幣別', '')).strip(),
                str(per_vendor.get('稅別', '')).strip(), float(per_vendor.get('外加稅金率') or 0 ), str(per_vendor.get('商品價格_交期表_MOQ', '')).strip(),
                str(per_vendor.get('廠商統編', '')).strip(), str(per_vendor.get('交期', '')).strip(), str(per_vendor.get('付款日期', '')).strip(),
                str(per_vendor.get('往來銀行', '')).strip(), str(per_vendor.get('往來銀行帳號', '')),
                str(per_vendor.get('單號', '')).strip(), str(per_vendor.get('下單方式', '')).strip(), str(per_vendor.get('代工暨採購說明文件連結')).strip(),
                str(per_vendor.get('注意事項', '')).strip(), str(per_vendor.get('廠商存摺影本連結', '')).strip(), per_vendor.get('更新至主檔日'),
                str(per_vendor.get('審核主管', '')), str(per_vendor.get('申請者', '')).strip(), str(per_vendor.get('廠商代號', '')).strip()
            ))
    result: bool = xin_tea_basic_vendor.vendor_sync(vendor_add, vendor_upd)
    return result
    