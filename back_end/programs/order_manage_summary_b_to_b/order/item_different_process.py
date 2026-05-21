from programs.core.db_process.xin_tea.order_manage_summary_b_to_b import main as xin_tea

def item_different_process(gs_url: str, modify_data: str) -> list:
    """
    處理料件差異數
    :param gs_url: 報價單Google Sheet連結
    :param modify_data: 修改的資料
    """
    upd_data: list = []
    for per_modify in modify_data:
        if per_modify.get('customize_type') == '手動增加':
            try:
                total_order_num: float = xin_tea.qry_order_manage_b_to_b_item_detail(gs_url, per_modify.get('s_item'))[0]['total_quantity']
            except IndexError:
                total_order_num: float = 0
            # 報價單無此料件則跳過
            if total_order_num == 0:
                continue
            # 查詢原有該筆BOM料件的使用量
            use_quantity: list = xin_tea.qry_bom_detail_use_quantity(per_modify.get('bom_detail_id'))
            if len(use_quantity) == 0:
                total_use: float = 0
            else:
                total_use = use_quantity[0]['total_use']
            new_quantity: float = float(per_modify.get('use_quantity'))*float(use_quantity[0]['quantity'])+float(per_modify.get('adjustment_quantity'))
            upd_data.append(
                (
                    new_quantity - total_use,
                    gs_url,
                    per_modify.get('s_item')
                )
            )
    return upd_data