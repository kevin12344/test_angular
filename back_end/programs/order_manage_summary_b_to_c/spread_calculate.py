from datetime import datetime
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea

class SpreadCalculate:
    def __init__(self, b_to_c: list):
        self.b_to_c: list = b_to_c
        
    def process(self) -> bool:
        # 用料明細展算
        result: bool = self.__spread_calculate()
        if result:
            return '批次展算成功'
        return '批次展算失敗'
        
    def __spread_calculate(self) -> bool:
        crt_use_item_param: list = []
        upd_spread_calculate_param: list = []
        # BOM展算規則
        can_spread_rule: list = xin_tea.qry_bom_spread_rule_can_spread()
        no_spread_rule: list = xin_tea.qry_bom_spread_rule_no_spread()
        
        can_spread: list = [per_can.get('item_category') for per_can in can_spread_rule]
        no_spread: list = [per_no.get('item_category') for per_no in no_spread_rule]
        
        for per_vendor in self.b_to_c:
            bom: str = ''
            try:
                print(len(per_vendor.get('bom_bpm_form_id')))
                bom = per_vendor.get('bom_bpm_form_id')
            except:
                pass
            # BOM 改抓現行料件主檔(避免預購期間BOM表有異動)
            item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
            if item_data:
                bom = item_data[0].get('bom')
            # 有BOM表且品項類別為A,B，則查詢該品項之BOM表
            if len(bom) > 0 and per_vendor.get('item_category') in can_spread:
                bom_data: list = xin_tea.qry_bom_by_item(per_vendor.get('item'), bom)
                order_m_item: str = per_vendor.get('item')
                quantity: float = per_vendor.get('quantity')
                for per_bom in bom_data:
                    m_item: str = per_bom.get('m_item')
                    # 只算一階料
                    if order_m_item == m_item:
                        s_item: str = per_bom.get('s_item')

                        # 計算用量(該子件用量*訂單數量)
                        s_item_use_quantity: float = float(per_bom.get('use_quantity')) * float(quantity)
                        unit: str = ''
                        item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
                        try:
                            unit = item_data[0]['unit']
                        except:
                            pass
                        crt_use_item_param.append(
                            (
                                per_vendor.get('e_commerce_platform_order_no'), per_vendor.get('split_berfore_order_no'), per_vendor.get('order_key'), per_vendor.get('earliest_arrival_date'), per_vendor.get('latest_arrival_date'),
                                per_vendor.get('to_order_generate_date'),
                                '', per_vendor.get('item'), per_vendor.get('product_name'), quantity, '標準', '', per_vendor.get('order_remark_or_shipping_remark'),
                                order_m_item, per_vendor.get('product_name'), s_item, per_bom.get('s_item_name'), per_bom.get('use_quantity'), s_item_use_quantity,
                                '', '', '官網B2C訂單', per_vendor.get('item_category'), per_vendor.get('generate_vendor'), '0', '' , '', '', '', per_vendor.get('shipping_out_warehouse'),
                                per_vendor.get('bom_bpm_form_id'), '0', unit
                            )
                        )
            # 無BOM or 料件類別為X,Y,3,DX，直接新增
            if len(bom) == 0 or per_vendor.get('item_category') in no_spread:
                print('456')
                unit: str = ''
                item_data: list = xin_tea.qry_item_data(per_vendor.get('item'))
                try:
                    unit = item_data[0]['unit']
                except:
                    pass
                crt_use_item_param.append(
                    (
                        per_vendor.get('e_commerce_platform_order_no'), per_vendor.get('split_berfore_order_no'), per_vendor.get('order_key'), per_vendor.get('earliest_arrival_date'), per_vendor.get('latest_arrival_date'),
                        per_vendor.get('to_order_generate_date'),
                        '', per_vendor.get('item'), per_vendor.get('product_name'), per_vendor.get('quantity'), '標準', '', per_vendor.get('order_remark_or_shipping_remark'),
                        per_vendor.get('item'), per_vendor.get('product_name'), per_vendor.get('item'), per_vendor.get('product_name'), '1', per_vendor.get('quantity'),
                        '', '', '官網B2C訂單', per_vendor.get('item_category'), per_vendor.get('generate_vendor'), 
                        '0', '' , '', '', '', per_vendor.get('shipping_out_warehouse'),
                        per_vendor.get('bom_bpm_form_id'), '0', unit
                    )
                )
            # 更新展算時間
            upd_spread_calculate_param.append(
                (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), per_vendor.get('order_key')
                )
            )
        result: bool = xin_tea.crt_spread_calculate(crt_use_item_param, upd_spread_calculate_param)
        return result