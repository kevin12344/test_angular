from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea
from programs.core.cloud_eip.web_service import EIPService

class DeleteGiftBox:
    def __init__(self, sq_form_id: list, user_data: dict):
        self.sq_form_id = sq_form_id
        self.user_data: dict = user_data
        self.error_msg: str = ''
        self.error_gift_box: list = []


    def execute(self) -> dict:
        """
        執行刪除禮盒生產單
        :return: dict
        """
        result: dict = self.__delete_gift_box()
        return result
    

    def __check_rule(self) -> str:
        """
        檢查是否符合刪除禮盒生產單規則
        """
        for per_sq in self.sq_form_id:
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_gift_box(per_sq)
            for per_detail in sq_form_detail:
                gift_box_id: str = per_detail.get('bpm_generate_id', '')
                if gift_box_id in self.error_gift_box:
                    continue
                # 簽核完畢表單不能刪除(駁回or完成)
                if per_detail.get('bpm_generate_status', '0') != '0':
                    self.error_gift_box.append(gift_box_id)
                    self.error_msg += f"【{gift_box_id}】禮盒生產單已簽核完畢，無法刪除\n"


    def __delete_gift_box(self) -> str:
        """
        刪除禮盒生產單
        """
        form_id: list = []
        delete_gift_box_status: list = []
        clear_gift_box_form: list = []
        for per_sq in self.sq_form_id:
            sq_form_detail: list = xin_tea.qry_order_manage_summary_b_to_b_gift_box(per_sq)
            for per_detail in sq_form_detail:
                bpm_form_id: str = per_detail.get('bpm_generate_id', '')
                # 有BPM單才可以刪除
                if bpm_form_id != '':
                    # 整單駁回(BPM)
                    EIPService().sign(self.user_data['bpm_account'], bpm_form_id, '', '-1')
                    # 刪除禮盒生產單狀態資料
                    delete_gift_box_status.append(
                        (
                            bpm_form_id,
                        )
                    )
                    # 清除訂單明細禮盒生產單號
                    clear_gift_box_form.append(
                        (
                            per_detail.get('order_key'),
                        )
                    )
                    # 紀錄處理單號
                    form_id.append(bpm_form_id)
        result: bool = xin_tea.delete_gift_box_form(delete_gift_box_status, clear_gift_box_form)
        if result:
            return {'process_form': form_id, 'status': 'success', 'message': '禮盒生產單刪除成功'}
        return {'process_form': form_id, 'status': 'fail', 'message': '禮盒生產單刪除失敗'}