import pandas as pd
from io import BytesIO
from programs.core.db_process.xin_tea.set_param import main as xin_tea_set_param

class UploadCustomizeItem:
    def __init__(self, new_item_replace: BytesIO):
        self.new_item_replace: list = pd.read_excel(new_item_replace, sheet_name=0).fillna('').to_dict(orient='records')

    def upload_customize_item(self) -> str:
        """
        執行可客製料件
        """    
        # 1. 檢查料件是否存在於料件主檔
        try:
            check_item: str = self.__check_item_id_in_item()
            if check_item != 'OK':
                return check_item
        except:
            return '檢查料件異常'
        # 3. 開始執行可客製料件更新
        try:
            result: str = self.__upd_customize_item()
            return result
        except:
            return '更新可客製料件失敗'

    def __check_item_id_in_item(self) -> str:
        """
        檢查料件是否存在於料件主檔
        """
        for per_item in self.new_item_replace:
            item_id: str = str(per_item.get('客製化料號'))
            check_data: list = xin_tea_set_param.qry_item_id_in_item([item_id])
            if not check_data:
                return f'不存在的料件: {item_id}'
        return 'OK'
    
    def __upd_customize_item(self) -> str:
        """
        更新可客製料件(舊有刪除，直接全部新增)
        """
        crt: list = []
        for per_item in self.new_item_replace:
            item_id: str = str(per_item.get('客製化料號'))
            #exist: list = xin_tea_set_param.qry_item_in_customize_item(item_id)
            #if not exist:
            # 新增
            crt.append(
                (
                    item_id,
                )
            )
        result: bool = xin_tea_set_param.crt_customize_item(crt)
        if result:
            return '更新可客製料件成功'
        else:
            return '更新可客製料件失敗'