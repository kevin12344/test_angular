from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea
from programs.core.cloud_eip.web_service import EIPService

class DeleteBToBOrder:
    def __init__(self, sq_form_id: list, user_data: dict):
        self.sq_form_id = sq_form_id
        self.user_data: dict = user_data
        self.error_order: list = []
        self.error_msg: str = ''

    def execute(self) -> dict:
        """
        執行刪除B2B銷售訂單
        :return: dict
        """
        result: dict = self.__delete_b_to_b_order()
        return result
    
    def __check_rule(self) -> str:
        """
        檢查是否符合刪除B2B銷售訂單規則
        """
        for per_sq in self.sq_form_id:
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_by_sq_id(per_sq)
            bpm_form_id: str = sq_form_detail[0]['bpm_form_id']
            if bpm_form_id in self.error_order:
                continue
            # 簽核完畢表單不能刪除(駁回or完成)
            if sq_form_detail[0]['bpm_form_status'] != '0':
                self.error_order.append(bpm_form_id)
                self.error_msg += f"訂單【{bpm_form_id}】B2B銷售訂單已簽核完畢，無法刪除\n"
            
    def __delete_b_to_b_order(self) -> str:
        """
        刪除B2B銷售訂單
        """
        process_form: list = []
        delete_b_to_b_order_status: list = []
        clear_b_to_b_order_form: list = []
        for per_sq in self.sq_form_id:
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_by_sq_id(per_sq)
            # 有BPM單才可以刪除
            bpm_form_id: str = sq_form_detail[0]['bpm_form_id']
            if bpm_form_id != '':
                # 整單駁回(BPM)
                EIPService().sign(self.user_data['bpm_account'], bpm_form_id, '', '-1')
                # 刪除B2B訂單狀態資料
                delete_b_to_b_order_status.append(
                    (
                        bpm_form_id,
                    )
                )
                # 清除訂單明細B2B單號
                clear_b_to_b_order_form.append(
                    (
                        per_sq,
                    )
                )
                process_form.append(bpm_form_id)
        result: bool = xin_tea.delete_b_to_b_order_status(delete_b_to_b_order_status, clear_b_to_b_order_form)
        if result:
            return {'process_form': process_form, 'status': 'success', 'message': 'B2B銷售訂單產生成功'}
        return {'process_form': process_form, 'status': 'fail', 'message': 'B2B銷售訂單產生失敗'}