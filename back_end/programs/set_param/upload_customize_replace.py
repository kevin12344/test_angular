import pandas as pd
from io import BytesIO
from programs.core.db_process.xin_tea.set_param import main as xin_tea_set_param

class UploadCustomizeReplace:
    def __init__(self, new_item_replace: BytesIO):
        self.new_item_replace: list = pd.read_excel(new_item_replace, sheet_name=0).fillna('').to_dict(orient='records')
    
    def upload_customize_replace(self) -> str:
        """
        執行客製料件替換
        """    
        # 1. 檢查料件是否存在於料件主檔
        try:
            check_item: str = self.__check_item_id_in_item()
            if check_item != 'OK':
                return check_item
        except:
            return '檢查料件異常'
        # 3. 開始執行客製料件替換更新
        result: str = self.__upd_customize_replace()
        return result
        
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
    
    def __upd_customize_replace(self) -> str:
        """
        更新客製料件替換(舊有刪除，直接全部新增)
        """
        crt: list = []
        upd: list = []
        for per_item in self.new_item_replace:
            item_id: str = str(per_item.get('客製化料號'))
            replace_id: str = str(per_item.get('需扣掉料號'))
            #exist: list = xin_tea_set_param.qry_item_in_customize_replace(item_id, replace_id)
            """
            if exist:
                # 更新
                upd.append(
                    (
                        replace_id, item_id
                    )
                )
            else:
            """
            # 新增
            crt.append(
                (
                    item_id, replace_id
                )
            )
        result: bool = xin_tea_set_param.crt_upd_customize_replace(crt, upd)
        if result:
            return '更新客製化料件替換成功'
        else:
            return '更新客製化料件替換失敗'