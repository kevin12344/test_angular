from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea
from datetime import datetime

class ModifyOrderManageSummary:
    """修改訂單管理總表"""
    def __init__(self, modify_order: list):
        self.modify_order: list = modify_order
        
    
    def process(self) -> str:
        """
        處理修改訂單管理總表
        """
        # 1. 檢查資料是否符合修改訂單管理總表條件
        result: str = self.__check_data()
        if result != 'OK':
            return result
        # 2. 處理修改訂單管理總表
        result: str = self.__modify_order_manage_summary()
        return result
    
    def __check_data(self) -> str:
        """
        檢查修改訂單管理總表資料
        """
        for per_detail in self.modify_order:
            e_commerce_platform: str = per_detail.get('e_commerce_platform')
            # 修改成狀態2(必須滿足 新訂單_訂單狀態:已確認/備註欄位:已確認或空白/預計抛單日有值:拋單生產日不得小於現在日期)
            if per_detail.get('status') == '2':
                if (per_detail.get('is_check_remark_message') not in ['', '已確認']) or (per_detail.get('to_order_generate_date') == ''):
                    return f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件"
                # 新訂單_訂單狀態 依電商平台決定是否可改成狀態2
                new_order_status: str = per_detail.get('new_order_order_status')
                if e_commerce_platform == 'line 禮物':
                    if new_order_status not in ['已付款']:
                        return f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件"
                elif e_commerce_platform == 'shopline':
                    if new_order_status not in ['已確認']:
                        return f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件"
                elif e_commerce_platform == 'pinkoi':
                    if new_order_status not in ['待出貨', '尚未付款']:
                        return f"心茶訂單【{per_detail.get('order_key')}】不符合修改成狀態2條件"
                # 拋單生產日不得小於現在日期
                if per_detail.get('to_order_generate_date') < datetime.now().strftime('%Y/%m/%d'):
                    return f"心茶訂單【{per_detail.get('order_key')}】拋單生產日不得小於現在日期"
        return 'OK' 
    
    def __modify_order_manage_summary(self) -> bool:
        """
        修改訂單管理總表
        """
        update_param: list = []
        update_special: list = []
        now_date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for per_upd in self.modify_order:
            update_param.append(
                (
                    per_upd.get('white_list_process'), per_upd.get('is_check_remark_message'),
                    per_upd.get('to_order_generate_date'), per_upd.get('earliest_arrival_date'),
                    per_upd.get('generate_vendor'), per_upd.get('shipping_out_warehouse'),
                    per_upd.get('status'), per_upd.get('xin_tea_remark'), now_date,
                    per_upd.get('quantity'), per_upd.get('latest_arrival_date'), per_upd.get('delivery_vendor'),
                    per_upd.get('order_key')
                )
            )
            
        result: bool = xin_tea.modify_order_manage_summary_b_to_c(update_param)
        if result:
            return '修改成功'
        return '修改失敗'