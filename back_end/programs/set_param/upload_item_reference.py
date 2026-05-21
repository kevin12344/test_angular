import pandas as pd
from io import BytesIO
from programs.core.db_process.xin_tea.set_param import main as xin_tea_basic_item_reference

class UploadItemReference:
    def __init__(self, new_item_reference: BytesIO):
        self.item_reference: list = pd.read_excel(new_item_reference, sheet_name=0).fillna('').to_dict(orient='records')
    
    def upload_item_reference(self) -> str:
        """
        執行料件參照表
        """    
        # 1. 檢查料件是否存在於料件主檔
        try:
            check_item: str = self.__check_item_id_in_item()
            if check_item != 'OK':
                return check_item
        except:
            return '檢查料件異常'
        # 2. 檢查廠商是否存在於廠商主檔
        try:
            check_vendor: str = self.__check_vendor_id_in_vendor()
            if check_vendor != 'OK':
                return check_vendor
        except:
            return '檢查廠商異常'
        # 3. 開始執行料件參照資料更新
        result: str = self.__upd_item_reference()
        return result
        
    def __check_item_id_in_item(self) -> str:
        """
        檢查料件是否存在於料件主檔
        """
        item_reference: list = list(set([str(item['料件']) for item in self.item_reference]))
        check_data: list = xin_tea_basic_item_reference.qry_item_id_in_item(item_reference)
        check_data: list = [str(item['item']) for item in check_data]
        if len(check_data) != len(item_reference):
            # 找出不存在的料件
            not_exist_item: list = list(set(item_reference) - set(check_data))
            not_exist_item: str = ','.join(not_exist_item)
            return f'不存在的料件: {not_exist_item}'
        return 'OK'

    def __check_vendor_id_in_vendor(self) -> str:
        """
        檢查廠商是否存在於廠商主檔
        """
        vendor_reference: list = list(set([item['廠商'] for item in self.item_reference]))
        check_data: list = xin_tea_basic_item_reference.qry_vendor_in_vendor_list(vendor_reference)
        check_data: list = [str(item['vendor']) for item in check_data]
        if len(check_data) != len(vendor_reference):
            # 找出不存在的廠商
            not_exist_vendor: list = list(set(vendor_reference) - set(check_data))
            not_exist_vendor: str = ','.join(not_exist_vendor)
            return f'不存在的廠商: {not_exist_vendor}'
        return 'OK'
    
    
    def __upd_item_reference(self) -> str:
        """
        更新料件參照表
        """
        crt: list = []
        upd: list = []
        add_new_vendor: list = []
        check_vendor: list = []
        for per_item in self.item_reference:
            vendor_name: str = per_item.get('廠商', '')
            yes_or_no: str = '1' if per_item.get('是/否', '') == '是' else '0'
            # 先判斷廠商+料件是否存在，存在更新，不存在新增
            exist: list = xin_tea_basic_item_reference.qry_item_reference_exist(str(per_item.get('料件')), vendor_name)
            if exist:
                # 更新
                upd.append(
                    (
                        yes_or_no, str(per_item.get('料件')), vendor_name
                    )
                )
            else:
                # 新增
                crt.append(
                    (
                        str(per_item.get('料件')), vendor_name, per_item.get('品名', ''), per_item.get('單位', ''), yes_or_no, 
                    )
                )
            # 判斷廠商是否存在於生產廠商主檔
            if vendor_name not in check_vendor:
                check_vendor.append(vendor_name)
                exist: list = xin_tea_basic_item_reference.qry_vendor_in_vendor(vendor_name)
                # 新的生產廠商要新增
                if not exist:
                    vendor_data: list = xin_tea_basic_item_reference.qry_vendor_data(vendor_name)
                    if vendor_data:
                        add_new_vendor.append(
                            (
                                vendor_data[0]['vendor_id'], vendor_data[0]['vendor_name'], vendor_data[0]['consume_warehouse'], '1'
                            )
                        )
        # 執行新增/更新
        result: bool = xin_tea_basic_item_reference.crt_and_upd_item_reference(crt, upd, add_new_vendor)
        if result:
            return '上傳成功'
        return '上傳失敗'