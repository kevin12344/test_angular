def change_data(item_detail_in_out: list) -> list:
    """
    轉換出入明細資料格式
    :param item_detail_in_out: 出入明細資料
    """
    """
    # 先複製所有原始數據
    result = item_detail_in_out.copy()
    
    # 用集合記錄已處理的項目鍵值，提高查詢效率
    processed_keys = set()
    
    # 找出唯一的母件項目
    unique_items = []
    for item in item_detail_in_out:
        key = f"{item['m_item']}{item['complete_time']}"
        if key not in processed_keys and item.get('m_item'):  # 確保有母件項目
            processed_keys.add(key)
            unique_items.append(item)
    
    # 為每個唯一母件項目添加兩筆新記錄
    print('item', unique_items)
    for item in unique_items:
        # 添加兩筆新記錄，表示入庫和出庫
        common_data = {
            's_item': item.get('m_item'),
            's_item_name': item.get('m_item_name'),
            'shipping_out_warehouse': item.get('shipping_out_warehouse'),
            'unit': '',
            'complete_time': item.get('complete_time'),
            # 保留其他可能需要的欄位
            'm_item': item.get('m_item'),
            'm_item_name': item.get('m_item_name'),
            'generate_status': item.get('generate_status')
        }
        if item.get('item_category') in ['A', 'B'] and len(item.get('bom_bpm_form_id')) > 0: 
            # 入庫記錄
            in_record = common_data.copy()
            in_record['total_estimate_use'] = item.get('total_estimate_generate')
            result.append(in_record)
        
        # 出庫記錄
        out_record = common_data.copy()
        out_record['total_estimate_use'] = -item.get('total_estimate_generate')
        result.append(out_record)
    """
    # 增加識別碼
    for i, item in enumerate(item_detail_in_out):
        item['complete_time'] = f"{str(item.get('complete_time'))}-{i+1}"
    
    return item_detail_in_out