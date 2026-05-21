from datetime import datetime
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea

class CheckData:
    def __init__(self, b_to_c: list):
        self.b_to_c: list = b_to_c

    def check_data(self) -> list:
        """檢查訂單管理總表資料"""
        check_param: list = []
        for per_b_to_c in self.b_to_c:
            message: str = ''
            # 該筆已拋給廠商則不檢查
            vendor_data: list = xin_tea.qry_vendor_order(per_b_to_c.get('order_key'))
            if vendor_data:
                continue
            # 檢查拋單生產日
            check_message: str = self.__check_to_generate_date(per_b_to_c.get('to_order_generate_date'))
            message += check_message
            check_param.append(
                (
                    message, per_b_to_c.get('order_key')
                )
            )
        return check_param
                
    @staticmethod
    def __check_to_generate_date(to_generate_date: str) -> str:
        """
        檢查拋單生產日是否大於今天
        :param to_generate_date: 拋單生產日
        """
        if not to_generate_date:
            return ''
        
        # 將輸入的日期字串轉換為 datetime 物件
        to_generate_date_obj = datetime.strptime(to_generate_date, '%Y/%m/%d')
        
        # 取得今天的 datetime 物件，並去除時間部分
        today_obj = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    
        if to_generate_date_obj > today_obj:
            return '未到拋單生產日，不得拋單給廠商' 
        if to_generate_date_obj < today_obj:
            return '逾期未拋轉'
        if to_generate_date_obj == today_obj:
            return ''
        return '未知錯誤'