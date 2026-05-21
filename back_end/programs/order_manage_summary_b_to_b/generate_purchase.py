from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea
from datetime import datetime
from programs.core.cloud_eip.web_service import EIPService

class GeneratePurchase():
    def __init__(self, sq_form_id: list, user_data: dict):
        self.sq_form_id = sq_form_id
        self.user_data: dict = user_data
        self.error_msg: str = ''
        self.error_order_key: list = []

    def execute(self) -> dict:
        """
        執行產生採購單
        :return: dict
        """
        # 檢查規則
        error_msg: str
        error_order_key: list
        error_msg, error_order_key = self.__check_rule()
        # 檢查項目
        result: dict = self.__generate_purchase(error_order_key)
        return result
    

    def __check_rule(self) -> str:
        """
        檢查是否符合產生採購單規則
        """
        for per_sq in self.sq_form_id:
            detail: list = []
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_gift_box(per_sq.get('generate'))
            for per_sq in sq_form_detail:
                # 是否有先產生B2B訂單
                if per_sq.get('bpm_form_id') == '':
                    self.error_order_key.append(per_sq.get('order_key'))
                    self.error_msg += f"訂單編號【{per_sq.get('order_key')}】未產生B2B訂單，請先產生B2B訂單\n"
        return self.error_msg, self.error_order_key

    def __generate_purchase(self, error_order_key: list) -> str:
        """
        產生採購單
        :param error_order_key: list 錯誤訂單編號
        """
        form_id: list = []
        crt_gift_box_status: list = []
        upd_b_to_b_new_form_id: list = []
        clear_update_remind: list = []
    
        for k, per_sq in enumerate(self.sq_form_id):
            # 跳過有錯誤的訂單
            if per_sq.get('key') in error_order_key:
                continue
            purchase_detail: list = xin_tea.qry_order_manage_summary_b_to_b_by_order_key(per_sq.get('key'))
        return '12345'