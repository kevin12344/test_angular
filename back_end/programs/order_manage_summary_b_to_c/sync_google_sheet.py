import time, math, gspread.exceptions
from googleapiclient.errors import HttpError
from programs.core.db_process.xin_tea.foundry import main as xin_tea
from programs.core.db_process.xin_tea.item_detail_in_out import main as xin_tea_item_detail_in_out
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea_order_manage_summary_b_to_c
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.data_work.google_sheet_format import count_day_for_google_sheet
from programs.core.data_work import date_format

def sync_foundry() -> bool:
    """
    同步代工廠大表至 Google Sheet
    """
    foundry: list = xin_tea.qry_foundry_by_gs()
    
    final_gs: list = []
    """
    [
        "生產單號", "最早到貨日", "最晚到貨日", "出貨日期", "生產料號", "生產品名", "預計生產數量", 
        "客製或標準", "客製規格描述", "訂單備註", "母件料號", "母件品名", "子件用料", "子件品名", 
        "子件用量", "預計耗用量", "客製化料件", "uu1", "訂單單號", "客戶簡稱", "生產廠商", 
        "生產狀態", "每單位代工費未稅", "其他費用未稅", "代墊運費含稅", "總費用未稅", "完工數量", "簽核進度"
    ]
    """
    final_gs.append(
        [
            '最早到貨日', '子件料號', '子件品名', '生產狀態', '廠商', '預計耗用量'
        ]
        
    )
    """
            [
                per_foundry.get('e_commerce_platform_order_no'), count_day_for_google_sheet(per_foundry.get('earliest_arrival_date')), count_day_for_google_sheet(per_foundry.get('latest_arrival_date')), '', 
                per_foundry.get('item'), per_foundry.get('item_name'), per_foundry.get('total_estimate_generate'),
                per_foundry.get('customize_or_normal'), per_foundry.get('customize_specific'),
                per_foundry.get('order_remark'), per_foundry.get('m_item'), per_foundry.get('m_item_name'),
                per_foundry.get('s_item'), per_foundry.get('s_item_name'), per_foundry.get('s_item_use'),
                per_foundry.get('total_estimate_use'), per_foundry.get('customize_item'), 
                per_foundry.get('uu_one'), per_foundry.get('e_commerce_platform_order_no'),
                per_foundry.get('customer'), per_foundry.get('generate_vendor'), int(per_foundry.get('generate_status')), 
                per_foundry.get('oem_fee'), per_foundry.get('other_expense'), per_foundry.get('advance_expenses'),
                per_foundry.get('total_expense'), per_foundry.get('estimate_generate'), ''
            ]
            """
    for per_foundry in foundry:
        final_gs.append(
            [
                count_day_for_google_sheet(per_foundry.get('earliest_arrival_date')),
                per_foundry.get('s_item', ''), per_foundry.get('s_item_name', ''),
                per_foundry.get('generate_status', ''), per_foundry.get('generate_vendor', ''), 
                per_foundry.get('total_estimate_use', 0)
            ]
        )
    # 寫入gs
    sleet_count: int = 1
    for _ in range(1, 10):
        try:
            sheet = google_certificate('https://docs.google.com/spreadsheets/d/1_ooamkhMxIqj2jvkr18RlkyFWjof3TRigSyeNzU7I4k/edit?gid=654078163#gid=654078163')
            for i in range(0, len(sheet.worksheets())):
                title = sheet.get_worksheet(i).title
                if title == 'web測試大表':
                    worksheet = sheet.get_worksheet(i)
                    
                    # 直接清除 A:F 範圍的值，保留格式
                    worksheet.batch_clear(["A:F"])
                    
                    # 寫入新的數據
                    num = len(final_gs)
                    insert_range = f"A1:F{num}"
                    result = worksheet.update(values=final_gs, range_name=insert_range)
                    print(result)
                    return True  # 成功後直接返回
                    
        except (gspread.exceptions.APIError, HttpError) as e:
            print("發生錯誤:", e)
            sleep(sleet_count)
            sleet_count += 1
    return False  



def sync_item_detail_in_out() -> bool:
    """
    同步出入明細至 Google Sheet
    """
    item_detail_in_out: list = xin_tea_item_detail_in_out.qry_item_detail_in_out_for_google_sheet()
    
    final_gs: list = []
    final_gs.append(
        [
            "key", "item", "itemName", "unit", "庫存數量", "倉別"
        ]
    )
    for per_item in item_detail_in_out:
        final_gs.append(
            [
                per_item.get('complete_time', ''), per_item.get('s_item', ''), per_item.get('s_item_name', ''),
                per_item.get('unit', ''), per_item.get('total_estimate_use', 0), per_item.get('shipping_out_warehouse', '')
            ]
        )
    # 寫入gs
    sleet_count: int = 1
    for _ in range(1, 10):
        try:
            sheet = google_certificate('https://docs.google.com/spreadsheets/d/14ldhhNrhZmaHRSrAft36FTcmkwoeKWTZf1BJ6XBCVic/edit?gid=1059305883#gid=1059305883')
            for i in range(0, len(sheet.worksheets())):
                title = sheet.get_worksheet(i).title
                if title == 'web測試大表':
                    worksheet = sheet.get_worksheet(i)
                    
                    # 直接清除 A:AB 範圍的值，保留格式
                    worksheet.batch_clear(["A:F"])
                    
                    # 寫入新的數據
                    num = len(final_gs)
                    insert_range = f"A1:F{num}"
                    result = worksheet.update(values=final_gs, range_name=insert_range)
                    print(result)
                    return True  # 成功後直接返回
                    
        except (gspread.exceptions.APIError, HttpError) as e:
            print("發生錯誤:", e)
            sleep(sleet_count)
            sleet_count += 1
    return False


def sync_no_close_order() -> bool:
    """
    同步未結訂單至 Google Sheet
    """
    no_close_order: list = xin_tea_order_manage_summary_b_to_c.qry_no_close_order()
    
    final_gs: list = []
    final_gs.append(
        [
            "key", "訂單號碼", "訂單開立日期", "最晚到貨日", "料號", "品名", "規格", "訂單數量", 
            "單件優惠價", "訂單金額", "訂單狀態", "訂單類別", "訂單備註", "年份", "月份", "周別", 
            "計算key", "客製標準", "客戶簡稱", "開立人員", "出庫倉別", "最早到貨日"
        ]
    )
    
    # 行事曆起始日(計算周別)
    start_date: str = xin_tea_order_manage_summary_b_to_c.qry_calendar_start_date()[0]['value']
    
    for per_no in no_close_order:
        # 處理周別
        period: int = date_format.weekly_change(per_no.get('latest_arrival_date'), start_date)
    
        final_gs.append(
            [
                per_no.get('order_key', ''), 
                per_no.get('e_commerce_platform_order_no', ''), 
                count_day_for_google_sheet(per_no.get('e_commerce_platform_order_date')), 
                count_day_for_google_sheet(per_no.get('latest_arrival_date_str')), 
                per_no.get('item', ''), 
                per_no.get('product_name', ''), 
                per_no.get('platform_specific', ''), 
                per_no.get('quantity', 0), 
                per_no.get('special_price', 0), 
                per_no.get('order_money', 0), 
                per_no.get('generate_status', ''), 
                per_no.get('order_type', ''), 
                per_no.get('order_remark_or_shipping_remark', ''),
                per_no.get('order_year', ''), 
                per_no.get('order_month', ''), 
                period,
                per_no.get('count_key', ''), 
                per_no.get('customize_normal', ''), 
                per_no.get('customer_name', ''), 
                per_no.get('importer', ''), 
                per_no.get('shipping_out_warehouse', ''), 
                count_day_for_google_sheet(per_no.get('earliest_arrival_date'))
            ]
        )
    # 寫入gs
    sleet_count: int = 1
    for _ in range(1, 10):
        try:
            sheet = google_certificate('https://docs.google.com/spreadsheets/d/1tiYA4JmhGW5DoZHOfljsh1JkBxvcXcZzEgv34W82Erk/edit?gid=1566084965#gid=1566084965')
            for i in range(0, len(sheet.worksheets())):
                title = sheet.get_worksheet(i).title
                if title == 'web測試大表':
                    worksheet = sheet.get_worksheet(i)
                    
                    # 直接清除 A:V 範圍的值，保留格式
                    worksheet.batch_clear(["A:V"])
                    
                    # 寫入新的數據
                    num = len(final_gs)
                    insert_range = f"A1:V{num}"
                    result = worksheet.update(values=final_gs, range_name=insert_range)
                    print(result)
                    return True  # 成功後直接返回
                    
        except (gspread.exceptions.APIError, HttpError) as e:
            print("發生錯誤:", e)
            sleep(sleet_count)
            sleet_count += 1
    return False


    
    
def sleep(sleep: int):
    # 指數退避法 暫停時間
    sleep = math.pow(2, sleep)
    print(f"時間暫停秒數: ", sleep)
    time.sleep(sleep)
    if sleep < 6:
        sleep += 1


if __name__ == '__main__':
    sync_foundry()