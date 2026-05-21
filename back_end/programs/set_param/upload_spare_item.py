import pandas as pd
from io import BytesIO
from programs.core.db_process.xin_tea.set_param import main as xin_tea_set_param

class UploadSpareItem:
    def __init__(self, new_item_reference: BytesIO):
        self.spare_item: list = pd.read_excel(new_item_reference, sheet_name=0).fillna('').to_dict(orient='records')
    
    def upload_spare_item(self) -> str:
        """
        執行備用料件上傳
        """    
        # 檢查料件是否存在於料件主檔
        check_item: str = self.__check_item_id_in_item()
        if check_item != 'OK':
            return check_item
        # 開始執行備用料件更新
        result: str = self.__update_spare_item()
        return result
        
    def __check_item_id_in_item(self) -> str:
        """
        檢查料件是否存在於料件主檔
        """
        error_message: str = ''
        item: list = list(set([str(item['禮盒料號']) for item in self.spare_item]))
        spare_item: list = list(set([str(item['備用料號']) for item in self.spare_item]))
        check_data: list = xin_tea_set_param.qry_item_id_in_item(item)
        check_data: list = [item['item'] for item in check_data]
        check_spare_data: list = xin_tea_set_param.qry_item_id_in_item(spare_item)
        check_spare_data: list = [item['item'] for item in check_spare_data]

        if len(check_data) != len(item):
            # 找出不存在的料件
            not_exist_item: list = list(set(item) - set(check_data))
            not_exist_item: str = ','.join(not_exist_item)
            error_message += f'不存在的料件: {not_exist_item}<br>' 
        if len(check_spare_data) != len(spare_item):
            # 找出不存在的料件
            not_exist_spare_item: list = list(set(spare_item) - set(check_spare_data))
            not_exist_spare_item: str = ','.join(not_exist_spare_item)
            if error_message != '':
                error_message += '; '
            error_message += f'不存在的備用料件: {not_exist_spare_item}'
        return 'OK'
    
    def __update_spare_item(self) -> str:
        """
        執行備用料件更新(舊有刪除，直接全部新增)
        """
        crt: list = []
        upd: list = []
        for per_spare in self.spare_item:
            item: str = str(per_spare.get('禮盒料號'))
            customize_or_standard: str = str(per_spare.get('客製化'))
            #check_data: list = xin_tea_set_param.qry_spare_item_exist(item, customize_or_standard)
            """
            if check_data:
                # 更新
                upd.append(
                    (
                        str(per_spare.get('備用料號')), per_spare.get('滿多少加X'),
                        str(per_spare.get('禮盒料號')), per_spare.get('客製化')
                    )
                )
            else:
            """
            # 新增
            crt.append(
                (
                    str(per_spare.get('禮盒料號')), per_spare.get('客製化'),
                    str(per_spare.get('備用料號')), per_spare.get('滿多少加X')
                )
            )
        result: bool = xin_tea_set_param.crt_or_upd_spare_item(crt, upd)
        if result:
            return '備用料件更新成功'
        else:
            return '備用料件更新失敗'