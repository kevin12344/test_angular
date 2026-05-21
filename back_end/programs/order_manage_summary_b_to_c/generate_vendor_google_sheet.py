import gspread
from programs.core.google_sheet_certificate import google_sheet_certificate
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea
from datetime import datetime

def crt_vendor_google_sheet(generate_vendor: str, vendor_google_sheet_data: list) -> bool:
    """
    產生google sheet
    :param generate_vendor: 產生的廠商
    :param vendor_google_sheet_data: 廠商資料
    """
    try:
        # 擴展認證範圍，加入必要的權限
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        # 使用 service_account.Credentials 建立認證
        creds = service_account.Credentials.from_service_account_file(
            "file/google_sheet_certificate/api_key.json",
            scopes=scope,
        )
        gc = gspread.authorize(creds)
        
        # 建立 Drive service
        drive_service = build('drive', 'v3', credentials=creds)
        
        # 建立新的 spreadsheet，名稱為廠商名稱加上日期
        vendor: str = ''
        if generate_vendor == 'F0017均茂有限公司':
            vendor = '均茂'
        elif generate_vendor == 'F0013俬儲空間':
            vendor = '俬儲'
        sheet_name = f"【心茶】{vendor}每日拋單表_{datetime.now().strftime('%Y%m%d')}"
        spreadsheet = gc.create(sheet_name)
        worksheet = spreadsheet.get_worksheet(0)
        
        # 設定擁有者權限
        owner_email = "JWBPI.TW@gmail.com"
        # 首先給予寫入權限
        spreadsheet.share(
            owner_email,
            perm_type='user',
            role='writer'
        )
        """
        # 使用 Drive API 設定擁有者
        permission = {
            'type': 'user',
            'role': 'owner',
            'emailAddress': owner_email
        }
        
        drive_service.permissions().create(
            fileId=spreadsheet.id,
            body=permission,
            transferOwnership=True
        ).execute()
        """
        # 定義表頭
        headers: list = xin_tea.qry_vendor_google_sheet_column(generate_vendor)
        header_list = get_headers(headers)
        
        # 更新表頭
        worksheet.update('A1', [header_list])
        
        # 準備資料列
        rows = []
        values: list = xin_tea.qry_vendor_google_sheet_value(generate_vendor)
        
        for item in vendor_google_sheet_data:
            row = []
            for per_value in values:
                if per_value.get('value') == '':
                    row.append('')
                else:
                    row.append(item.get(per_value.get('value')))
            rows.append(row)  # 別忘了把每一列加入 rows
        # 取得最後一個欄位的字母
        last_column = number_to_excel_column(len(values))
        # 更新資料列
        if rows:
            worksheet.update(f'A2:{last_column}{len(rows)+1}', rows)
        
        # 設定共用權限
        spreadsheet.share('', perm_type='anyone', role='writer')
        
        # 更新資料的google sheet url
        upd_google_sheet_data: list = []
        for per_vendor in vendor_google_sheet_data:
            # 將 URL 和 order_key 作為一個字典或元組加入列表
            upd_google_sheet_data.append(
                (
                    spreadsheet.url, sheet_name, per_vendor.get('order_key')  # 假設每個 vendor 資料都有 order_key
                )
            )
        # 更新資料庫
        xin_tea.upd_google_sheet_url(upd_google_sheet_data)
        return spreadsheet.url
        
    except Exception as e:
        print(f"建立 Google Sheet 時發生錯誤: {e}")
        return ''
    
def get_headers(headers: list) -> list:
    """
    處理資料庫回傳的 headers 資料
    :param headers: 資料庫回傳的 headers 列表
    :return: 處理後的表頭列表
    """
    try:
        # 先依照 column_pri_seq 排序，再取出 column_name
        sorted_headers = sorted(headers, key=lambda x: x['column_pri_seq'])
        return [header['column_name'].strip() for header in sorted_headers]
    except Exception as e:
        print(f"處理表頭時發生錯誤: {str(e)}")
        return []
    
    
def number_to_excel_column(n):
    """
    將數字轉換為 Excel 欄位名稱
    例如：1 -> A, 2 -> B, 26 -> Z, 27 -> AA
    """
    result = ""
    while n > 0:
        n -= 1
        result = chr(n % 26 + 65) + result
        n //= 26
    return result