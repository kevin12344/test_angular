from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea

class BatchRepeatSpread:
    def __init__(self, b_to_c: list):
        self.b_to_c: list = b_to_c
        self.error_order: list = []
        
    def process(self) -> bool:
        """批次重新展算-僅限於未結訂單(2.1 5 5.1)"""
        error_message: str = self.__check_rule()
        result: bool = self.__batch_repeat_spread()
        if result:
            if error_message:
                return f'{error_message}，其餘訂單批次重新展算成功'
            return '批次重新展算成功'
        return '批次重新展算失敗'
    
    def __check_rule(self) -> str | list:
        """檢查規則"""
        error_message: str = ''
        for per_detail in self.b_to_c:
            # 1. 檢查狀態是否可重新展算
            if per_detail.get('status') not in ['2.1', '5', '5.1']:
                error_message += f"訂單【{per_detail.get('order_key')}】狀態不符合重新展算狀態\n"
                self.error_order.append(per_detail.get('order_key'))
        return error_message
    

    def __batch_repeat_spread(self) -> bool:
        """批次重新展算"""

        # BOM展算規則
        can_spread_rule: list = xin_tea.qry_bom_spread_rule_can_spread()
        no_spread_rule: list = xin_tea.qry_bom_spread_rule_no_spread()
        
        can_spread: list = [per_can.get('item_category') for per_can in can_spread_rule]
        no_spread: list = [per_no.get('item_category') for per_no in no_spread_rule]
        
        crt_use_item_param: list = []
        upd_use_item_delete_param: list = []
        upd_order_manage_check_message_clear: list = []

        for per_detail in self.b_to_c:
            # 檢查訂單是否在錯誤列表中
            if per_detail.get('order_key') in self.error_order:
                continue
            # 查詢該筆品項之BOM表
            bom: str = ''
            item_data: list = xin_tea.qry_item_data(per_detail.get('item'))
            if item_data:
                bom = item_data[0].get('bom')
            # 有BOM表且品項類別為A,B，則查詢該品項之BOM表
            if len(bom) > 0 and per_detail.get('item_category') in can_spread:
                bom_data: list = xin_tea.qry_bom_by_item(per_detail.get('item'), bom)
                order_m_item: str = per_detail.get('item')
                quantity: float = per_detail.get('quantity')

                for per_bom in bom_data:
                    m_item: str = per_bom.get('m_item')
                    # 只算一階料
                    if order_m_item == m_item:
                        s_item: str = per_bom.get('s_item')
                        # 計算用量(該子件用量*訂單數量)
                        s_item_use_quantity: float = float(per_bom.get('use_quantity')) * float(quantity)
                        unit: str = ''
                        item_data: list = xin_tea.qry_item_data(per_detail.get('item'))
                        try:
                            unit = item_data[0]['unit']
                        except:
                            pass
                        crt_use_item_param.append(
                            (
                                per_detail.get('e_commerce_platform_order_no'), per_detail.get('split_berfore_order_no'), per_detail.get('order_key'), per_detail.get('to_order_generate_date'),
                                per_detail.get('earliest_arrival_date'), per_detail.get('latest_arrival_date'),
                                '', per_detail.get('item'), per_detail.get('product_name'), quantity, '標準', '', per_detail.get('order_remark_or_shipping_remark'),
                                order_m_item, per_detail.get('product_name'), s_item, per_bom.get('s_item_name'), per_bom.get('use_quantity'), s_item_use_quantity,
                                '', '', '官網B2C訂單', per_detail.get('item_category'), per_detail.get('generate_vendor'), '0', '', '', '', '', per_detail.get('shipping_out_warehouse'),
                                per_detail.get('bom_bpm_form_id'), '0', unit
                            )
                        )
            # 無BOM or 料件類別為X,Y,3,DX，直接新增
            if len(bom) == 0 or per_detail.get('item_category') in no_spread:
                unit: str = ''
                item_data: list = xin_tea.qry_item_data(per_detail.get('item'))
                try:
                    unit = item_data[0]['unit']
                except:
                    pass
                crt_use_item_param.append(
                    (
                        per_detail.get('e_commerce_platform_order_no'), per_detail.get('split_berfore_order_no'), per_detail.get('order_key'), per_detail.get('to_order_generate_date'),
                        per_detail.get('earliest_arrival_date'), per_detail.get('latest_arrival_date'),
                        '', per_detail.get('item'), per_detail.get('product_name'), per_detail.get('quantity'), '標準', '', per_detail.get('order_remark_or_shipping_remark'),
                        per_detail.get('item'), per_detail.get('product_name'), per_detail.get('item'), per_detail.get('product_name'), '1', per_detail.get('quantity'),
                        '', '', '官網B2C訂單', per_detail.get('item_category'), per_detail.get('generate_vendor'),
                        '0', '', '', '', '', per_detail.get('shipping_out_warehouse'),
                        per_detail.get('bom_bpm_form_id'), '0', unit
                    )
                )
            # 刪除原有展算資料
            upd_use_item_delete_param.append(
                (
                    per_detail.get('order_key'),
                )
            )
            # 將檢查結果清除
            upd_order_manage_check_message_clear.append(
                ('', per_detail.get('order_key'))
            )
        result: bool = xin_tea.batch_repeat_spread(crt_use_item_param, upd_use_item_delete_param, upd_order_manage_check_message_clear)
        return result