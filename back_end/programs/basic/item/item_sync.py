import pandas as pd
import time
from programs.core.google_sheet_certificate.google_sheet_certificate import google_certificate
from programs.core.db_process.xin_tea.basic.item import main as xin_tea_basic_item


class ItemSync:
    def __init__(self):
        pass

    def execute_sync(self) -> bool:
        """
        執行料件資料同步
        """
        # 1. 料件同步(抓Google Sheet)
        result: bool = self.__exe_item_sync()
        if result:
            # 2. 更新訂單管理總表上的訂單BOM
            exe_result: bool = self.__upd_order_manage_summary_bom()
            return exe_result
        return result

    @staticmethod
    def __exe_item_sync() -> bool:
        """
        同步料件資料
        """
        sheet = google_certificate(
                'https://docs.google.com/spreadsheets/d/1rpsLbbCMvt6WX3fRSwqLaDlAv4786_MvJvDNlE3gDRQ/edit?gid=0#gid=0')
        worksheet = sheet.get_worksheet(0)
        item_df = pd.DataFrame(worksheet.get_all_records())
        item: list = item_df.to_dict(orient='records')
        item_add: list = []
        item_upd: list = []
        for per_item in item:
            if len(str(per_item.get('item')).strip()) > 0:
                # 判斷料件是否存在
                item: list = xin_tea_basic_item.qry_item_exist(str(per_item.get('item')).strip())
                if len(item) == 0:
                    # 新增料件
                    item_add.append(
                        (
                            per_item.get('key'), str(per_item.get('item')), per_item.get('category'),
                            per_item.get('itemName'), per_item.get('unit'), per_item.get('unitPrice'),
                            per_item.get('googlesheet申請單連結'), per_item.get('purchasePrice'), per_item.get('備註', ''), per_item.get('supplier', ''),
                            per_item.get('用料清單單號', ''), per_item.get('料件檔案連結', ''), per_item.get('前置料件總交期', ''),
                            per_item.get('交期', ''), per_item.get('MOQ', ''), per_item.get('滿裝箱數', ''),
                            per_item.get('下單連結', ''), per_item.get('安全庫存量'), per_item.get('產品分類', ''),
                            per_item.get('產品包裝形式', '')
                        )
                    )
                else:
                    # 更新料件
                    item_upd.append(
                        (
                            per_item.get('key'), per_item.get('category'),
                            per_item.get('itemName'), per_item.get('unit'), per_item.get('unitPrice'),
                            per_item.get('googlesheet申請單連結'), per_item.get('purchasePrice'), per_item.get('備註', ''), per_item.get('supplier', ''),
                            per_item.get('用料清單單號', ''), per_item.get('料件檔案連結', ''), per_item.get('前置料件總交期', ''),
                            per_item.get('交期', ''), per_item.get('MOQ', ''), per_item.get('滿裝箱數', ''),
                            per_item.get('下單連結', ''), per_item.get('安全庫存量'), per_item.get('產品分類', ''),
                            per_item.get('產品包裝形式', ''), str(per_item.get('item'))
                        )
                    )
        result: bool = xin_tea_basic_item.item_sync(item_add, item_upd)
        return result
    
    @staticmethod
    def __upd_order_manage_summary_bom() -> bool:
        """
        更新訂單管理總表BOM
        """
        # 比對與更新訂單管理摘要表中的 BOM 資料 (B to C)
        order_manage_summary_b_to_c: list = xin_tea_basic_item.qry_upd_item_for_order_manage_summary_b_to_c()
        upd_order_manage_summary_b_to_c: list = []
        for per_order in order_manage_summary_b_to_c:
            if per_order.get('bom_bpm_form_id') != per_order.get('new_bom'):
                upd_order_manage_summary_b_to_c.append(
                    (
                        f"BOM單號更新為{per_order.get('new_bom')}", per_order.get('new_bom'), per_order.get('order_key')
                    )
                )
        xin_tea_basic_item.upd_order_manage_summary_b_to_c_bom(upd_order_manage_summary_b_to_c)
