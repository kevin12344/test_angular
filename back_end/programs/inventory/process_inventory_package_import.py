import os
import gspread.exceptions
import time
import math
import pandas as pd
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.db_process.xin_tea.inventory import main as xin_tea
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions

load_dotenv()


class ProcessInventoryPackageImport:
    def __init__(self, gs_url: str):
        self.gs_url = gs_url
        self.sleep_count = 0

    def sync_inventory_package_import(self) -> bool:
        """
        同步GS出入明細
        """
        for _ in range(0, 9):
            try:
                sheet = google_certificate(self.gs_url)
                
                # 遍歷所有工作表
                for i in range(len(sheet.worksheets())):
                    worksheet = sheet.get_worksheet(i)
                    title = worksheet.title
                    
                    if title == '打包前資料':
                        worksheet = sheet.get_worksheet(i)
                        inventory_df = pd.DataFrame(worksheet.get_all_records())
                        inventory_df: list = inventory_df.to_dict(orient='records')
                        add_inventory: list = []
                        for per_inventory in inventory_df:
                            # 清洗資料不要同步
                            if '資料清洗' in per_inventory.get('系統單號', ''):
                                continue
                            try:
                                inventory_num: float = float(per_inventory.get('庫存數量') or 0)
                            except ValueError:
                                inventory_num: float = 0
                            add_inventory.append(
                                (
                                    str(per_inventory.get('item', '')), per_inventory.get('itemName', ''),
                                    per_inventory.get('unit', ''),
                                    inventory_num, per_inventory.get('系統單號', ''),
                                    per_inventory.get('key1', ''), per_inventory.get('key', ''),
                                    per_inventory.get('倉別', ''), per_inventory.get('開立日期', ''),
                                    per_inventory.get('寫入時間', ''), self.gs_url
                                )
                            )
                        delete_param: list = [
                            (
                                self.gs_url,
                            )
                        ]
                        result: bool = xin_tea.add_close_inventory_gs(add_inventory, delete_param)
                return result
            except (gspread.exceptions.APIError, google_exceptions.TooManyRequests, google_exceptions.ResourceExhausted) as e:
                self.__sleep()

    def __sleep(self):
        """指數退避法 - 暫停時間"""
        sleep_time = math.pow(2, self.sleep_count)
        print(f"時間暫停秒數: {sleep_time}")
        time.sleep(sleep_time)
        if self.sleep_count < 6:
            self.sleep_count += 1