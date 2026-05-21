def dict_to_eip_str(origin_dict: dict) -> str:
    """
    將資料轉換成EIP連動欄位格式(下拉選單、客戶選擇器)
    :param origin_dict: dict 轉換資料
    """
    if len(origin_dict) == 0:
        return ''
    final_str = ''
    for key in origin_dict.keys():
        option_str = '[{value}({key})]/n'.format(key=key, value=origin_dict.get(key))
        final_str += option_str
    return final_str


def eip_option_to_str(option: str):
    """
    將EIP欄位去除(、)、#unknown
    :param option: str BPM欄位資料
    """
    if len(option) == 0:
        return ''
    option = option.replace('#unknown)', '')
    option = option.replace(')', '')
    op_list = option.split('(')
    return op_list


def eip_option_to_str_name(option: str):
    """
    將EIP欄位去除(、)、#unknown 取得資料name值
    :param option: str BPM欄位資料
    """
    if len(option) == 0:
        return ''
    option = option.replace('#unknown)', '')
    option = option.replace(')', '')
    op_list = option.split('(')
    return op_list[0]


def eip_option_to_str_id(option: str):
    """
    將EIP欄位去除(、)、#unknown 取得資料ID值
    :param option: str BPM欄位資料
    """
    if len(option) == 0:
        return ''
    option = option.replace('#unknown)', '')
    option = option.replace(')', '')
    op_list = option.split('(')
    return op_list[1]


def eip_item_tree_to_str(option: str) -> str:
    """
    取出支出項目樹資料
    :param option: str 支出項目樹欄位
    """
    if len(option) == 0:
        return ''
    option = option.replace('#unknown)', '')
    option = option.replace(')', '')
    option = option.replace('[', '')
    op_list = option.split('(')
    return op_list[0]


def eip_item_tree_to_id(option: str) -> str:
    """
    取出支出項目樹(id值)
    :param option: str 支出項目樹欄位
    """
    if len(option) == 0:
        return ''
    option = option.replace('#unknown)', '')
    option = option.replace(')', '')
    option = option.replace('[', '')
    op_list = option.split('(')
    if len(op_list) == 3:
        op_list = op_list[-1].split(']/n')
    else:
        op_list = op_list[1].split(']/n')
    return op_list[0]


def eip_item_tree_name(option: str) -> str:
    """
    取出支出項目樹(name值)
    :param option: str 支出項目樹欄位
    """
    if len(option) == 0:
        return ''
    option = option.replace('#unknown)', '')
    option = option.replace(')', '')
    option = option.replace('[', '')
    op_list = option.split('(')
    if len(op_list) == 3:
        return f"{op_list[0]}({op_list[1].split('.')[0]}).{op_list[1].split('.')[1]}"
    else:
        return op_list[0]


def eip_payment_tern_to_neo(option: str) -> str:
    """
    付款方式對應成NEO相對應的值
    :param option
    """
    if len(option) == 0:
        return ''
    if option == '零用金':
        return 'PettyCash'
    elif option == '現金':
        return 'Cash'
    elif option == '應付款項':
        return 'AP'
    else:
        return ''


def eip_schedule_payment_pattern(option: str) -> str:
    """
    預定付款方式轉換成NEO相對應的值
    :param option: str 預定付款名稱
    """
    if len(option) == 0:
        return ''
    if option == '票據':
        return 'Notes'
    elif option == '匯款':
        return 'Remit'
    elif option == '現金':
        return 'Cash'
    else:
        return ''


def eip_option_to_str_by_parentheses(string: str) -> str:
    """
    處理EIP回傳有()的資料  EX: xxxx(ooo)(12345) return ooo
    :param string: str 目標資料
    """
    if len(string) == 0:
        return ''
    process_string = eip_option_to_str(string)
    if len(process_string) == 2:
        final_string = process_string[1]
    else:
        final_string = process_string[2]
    return final_string


def eip_replenish_type_to_neo(replenish_type: str) -> str:
    """
    零用金撥補類別對應至ERP的值
    :param replenish_type: str 撥補類別
    """
    if len(replenish_type) == 0:
        return ''
    if replenish_type == '撥入':
        return 'Increase'
    elif replenish_type == '撥出':
        return 'Reduce'
    else:
        return ''


def process_currency_data(detail: list):
    """
    抓取明細第一筆處理外幣現時匯率資料群
    :param detail: list 明細資料
    """
    if len(detail) == 0:
        return detail
    if eip_option_to_str(detail[0]['幣別'])[0] == 'NTD':
        return []
    currency_data = [{'SEQUENCENO': '0010', 'CURRENCYID': eip_option_to_str(detail[0]['幣別'])[0],
                      'EXCHANGERATE': float(detail[0].get('匯率'))}]
    return currency_data


def eip_option_to_str_by_parentheses_for_google_sheet(string: str) -> str:
    """
    處理EIP回傳有()的資料 - 從google sheet回傳資料  EX: xxxx(ooo)(12345) return xxxx(ooo)
    :param string: str 目標資料
    """
    if len(string) == 0:
        return ''
    if len(string) == 2:
        process_string = string[0]
    else:
        process_string = string[0] + '(' + string[1] + ')'
    return process_string


def eip_option_to_str_by_external_program_check(data: str) -> list:
    """
    處理EIP統計表格外部程式檢查資料格式 EX: [xxx]/n[XXX]/n
    :param data: str 外部程式檢查資料格式
    """
    if len(data) == 0:
        return []
    process_data = data.replace('[', '')
    string_list = process_data.split(']/n')
    string_list.pop()
    return string_list


def eip_many_choose_control_item(data: str) -> list:
    """
    處理EIP多項選擇框資料格式 EX: [xxx(XXX)]/n[XXX(XXXX)]/n
    :param data: str 外部程式檢查資料格式
    """
    if len(data) == 0:
        return []
    process_data = data.replace('[', '')
    string_list = process_data.split(']/n')
    process_string: list = []
    for per_string in string_list:
        process_string.append(per_string.split('(')[0])
    process_string.pop()
    return process_string


def eip_option_to_str_by_file(data: str) -> list:
    """
    取得EIP檔案之ID
    :param data: str 檔案格式內容
    """
    if len(data) == 0:
        return []
    process_data = data.replace(')]/n', '')
    process_data_two = process_data.replace('[', '')
    string_list = process_data_two.split('(')
    return string_list


def eip_email_for_account(data: str) -> str:
    """
    抓取部門樹格式的email
    :param data: str 部門樹格式內容
    """
    if len(data) == 0:
        return ''
    process_data = data.replace(')]/n', '')
    process_data_two = process_data.replace('[', '')
    process_list = process_data_two.split('/')
    list_one = process_list[2]
    email_txt = list_one.split('#')[0]
    return email_txt


def eip_form_url_process(data: str) -> str:
    """
    抓表單連結格式的表單單號 [[服務完成單] 2021-11-29 語慈新增 「小鑫娛樂發大財 」服務完成單(Service-20211129-1#smartForm)]/n"
    :param data: str 表單連結格式內容
    """
    if len(data) == 0:
        return ''
    process_data = data.replace(')]/n', '')
    process_data_two = process_data.split('(')
    process_data_three = process_data_two[-1]
    return process_data_three.split('#')[0]


def eip_file_upload_process(file_list: list) -> str:
    """
    檔案處理
    :param file_list: list 檔案資料群
    """
    if len(file_list) == 0:
        return ''
    file_string: str = ''
    for per_file in file_list:
        file_string = file_string + '[' + per_file.split('=')[0] + ']/n'
    return file_string


def eip_sign_list_process(data: str) -> list:
    """
    處理EIP多項選擇框資料格式 EX: [xxx(XXX)]/n[XXX(XXXX)]/n
    :param data: str 外部程式檢查資料格式
    """
    if len(data) == 0:
        return []
    process_data = data.replace('[', '').replace(']/n', '').replace('#account)', ' ').replace('/', ' ')
    string_list = process_data.split(' ')
    string_list.pop()
    return string_list


def all_eip_sign_list(data: str) -> list:
    """
    處理EIP讀取簽核者清單API回傳值
    :param data: str 讀取簽核者清單API回傳值
    """
    if len(data) == 0:
        return []
    process_data = data.replace('[', '').split(']/n')
    process_data.pop()
    return process_data


def eip_subject_state(state: str) -> str:
    if len(state) == 0:
        return ''
    if state == '0':
        return '進行中'
    elif state == '1':
        return '通過'
    else:
        return '駁回'
    
def department_tree_process(data: str) -> list:
    """
    處理部門樹格式資料
    :param data: list 部門樹格式資料
    """
    if len(data) == 0:
        return []
    department_tree: list = []
    for per_department in all_eip_sign_list(data):
        department_tree.append(eip_option_to_str_name(per_department))
    return department_tree


if __name__ == '__main__':
    txt = '[拜訪慧景-停車費(去程).jpg(0676765E-0029-4AD9-8953-2274828744A2)]/n'
    # print(txt)
    if eip_item_tree_name(txt).endswith('.jpg'):
        print('123')
    else:
        print('456')