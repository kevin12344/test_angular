from programs.core.cloud_eip.eip_frame import EipBaseFrame
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea
from programs.core.data_work import string_format


# 銷售訂單-官網B2C
class XinTeaOrderBtoC(EipBaseFrame):
    def __init__(self, apikey: str, subject_id: str, sender: str, result: str, env_id: str):
        super().__init__(apikey, subject_id, sender, result, env_id)
        self.head_data: dict = self.origin_data.get('contentFields')[0]
        self.detail_list: list = self.origin_data.get('dataFields')
        self.form_name: str = self.origin_data.get('formName')

    def run_process(self) -> str:
        if self.apikey != self.eip_service.api_key:
            return 'Api_Key錯誤'
        if not self.__crt_sales_order_b_to_c():
            print(f"{self.form_name}執行失敗")
            return f"{self.form_name}執行失敗"
        return f"{self.form_name}執行成功"
        
            
    def __crt_sales_order_b_to_c(self) -> bool:
        # 寫入sales_order_b_to_c table & 寫入sales_order_b_to_c_detail
        sales_order_head: list = [
            (
                self.eip_param['subject_id'], '', self.head_data.get('開立人員'), self.head_data.get('開立日期'),
                self.head_data.get('客戶簡稱'), self.head_data.get('訂單類別', ''), self.head_data.get('uu'),
                '0', '1'                                                                          
            )
        ]
        sales_order: list = []
        for i, per_detail in enumerate(self.detail_list):
            sales_order.append((self.eip_param['subject_id'], i+1, per_detail.get('item'),
                                per_detail.get('category'), per_detail.get('itemName'), per_detail.get('用料清單單號'),
                                per_detail.get('訂單數量'), per_detail.get('生產廠商'), per_detail.get('出庫倉別'),
                                per_detail.get('帶出耗料倉別'), per_detail.get('完工入庫倉別'),
                                per_detail.get('拋單生產日期'), per_detail.get('推估出廠日期'),
                                per_detail.get('最早到貨日'), per_detail.get('最晚到貨日'), per_detail.get('新訂單訂單狀態'),
                                per_detail.get('新訂單付款狀態'), per_detail.get('電商平台'), per_detail.get('電商平台訂單日期'),
                                per_detail.get('電商平台訂單單號'), per_detail.get('物流方式'), per_detail.get('訂單備註和出貨備註'),
                                per_detail.get('各平台品名'), per_detail.get('各平台規格'), per_detail.get('收件人'),
                                per_detail.get('收件人電話'), per_detail.get('收件人地址'), per_detail.get('收件人Email'),
                                per_detail.get('付款方式'), float(per_detail.get('訂單金額').replace(',', '') or 0), per_detail.get('發票抬頭'),
                                per_detail.get('統一編號'), per_detail.get('uu1'), per_detail.get('年份'), per_detail.get('月份'),
                                per_detail.get('心茶訂單key值')
                              ))
        result: bool = xin_tea.crt_sales_order_b_to_c(sales_order_head, sales_order)
        if result:
            return True
        return False


if __name__ == '__main__':
    XinTeaOrderBtoC('AIzaSyBZrlwVzFDkUNmGp1zPvJLoB9MgQQ66w3g', '銷售訂單-官網B2C-20240905-2', '123', '1', '83491875_A1').run_process()