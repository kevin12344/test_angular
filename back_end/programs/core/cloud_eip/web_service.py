import json, os, requests
from dotenv import load_dotenv

# EIP
class EIPService:
    def __init__(self):
        self.url: str = os.getenv('EIP_URL')
        #self.url: str = os.getenv('EIP_TEST_URL')
        self.api_key: str = os.getenv('EIP_API_KEY')
        self.json_param: dict = {'apikey': self.api_key}

    def qry(self, form_id: str):
        """
        查詢表單資料
        :param form_id: str 表單單號
        """
        self.json_param |= {'function': 'getSubjectData', 'id': form_id}
        resp = requests.post(url=self.url, data=self.json_param)
        try:
            resp.json()
        except json.JSONDecoder:
            return {}
        return resp.json()

    def crt(self, sender: str, form_id: str, data: dict, call_back_url: str = '', specialFlow: str = '', to_be_modified_subject_id: str = ''):
        """
        外部起單/修改表單
        :param sender: str 起單人
        :param form_id: str 表單識別碼
        :param data: dict 表單json資料
        :param call_back_url: str 回呼網址
        :param specialFlow: str 簽核流程xml
        :param to_be_modified_subject_id: str 修改表單ID
        """
        
        self.json_param |= {'function': 'createSmartForm', 'formId': form_id, 'sender': sender,
                            'json': json.dumps(data), 'callBackUrl': call_back_url, 'specialFlow': specialFlow}
        if len(to_be_modified_subject_id) > 0:
            self.json_param |= {'toBeModifiedSubjectId': to_be_modified_subject_id}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def sign(self, sender: str, form_id: str, comment: str, decision: int, reject_step=''):
        """
        外部簽核
        :param sender: str 簽核者
        :param form_id: str 表單單號
        :param comment: str 簽核意見
        :param decision: int 簽核結果
        :param reject_step: str 駁回設定
        """
        self.json_param |= {'function': 'appendResponse', 'sender': sender, 'subjectId': form_id, 'decision': decision, 'comment': comment, 'rejectStep': reject_step}
        resp = requests.post(self.url, data=self.json_param)
        return str(resp.text)

    def get_signed_list(self, form_id: str):
        """
        取得該表單之所有簽核者
        :param form_id: str 表單單號
        """
        self.json_param |= {'function': 'getSignedList', 'subjectId': form_id}
        resp = requests.post(self.url, data=self.json_param)
        return str(resp.text)

    def upd_content_form(self, subject_id: str, **data):
        """
        修改表單(內容欄位)
        :param subject_id: str 表單單號
        :param data: dict 修改欄位名稱&內容字典
        """
        self.json_param |= {'function': 'updateContentForm', 'subjectId': subject_id}
        for key, content in data.items():
            self.json_param |= {key: content}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text).replace('\r', '\n')


    def upd_data_form(self, subject_id: str, **data):
        """
        修改表單(統計表格欄位)
        :param subject_id: str 表單單號
        :param data: dict 修改欄位名稱&內容字典
        """
        self.json_param |= {'function': 'updateDataForm', 'subjectId': subject_id}
        for key, content in data.items():
            self.json_param |= {key: content}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text).replace('\r', '\n')

    def file_download(self, file_id: str):
        """
        檔案下載
        :param file_id: str 檔案的google ID值
        """
        self.json_param |= {'function': 'getFileDownloadUrl', 'id': file_id}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def get_sign_data(self, form_id):
        """
        讀取表單完整簽核內容
        :param form_id: str 表單單號
        """
        self.json_param |= {'function': 'getSignData', 'id': form_id}
        resp = requests.post(url=self.url, data=self.json_param)
        return resp.json()

    def get_subject_state(self, form_id: str, with_step='false'):
        """
        讀取表單的簽核狀態
        :param form_id: str 表單單號
        """
        self.json_param |= {'function': 'getSubjectState', 'id': form_id, 'withStep': with_step}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def get_account_info(self, account_id: str):
        """
        查詢帳號內容
        :param account_id: str 帳號ID
        """
        self.json_param |= {'function': 'getAccountInfos', 'id': account_id}
        resp = requests.post(url=self.url, data=self.json_param)
        try:
            resp.json()
        except json.JSONDecoder:
            return {}
        return resp.json()

    def check_parameter(self):
        # 檢視參數是否正確
        self.json_param |= {'function': 'showParameters'}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def read_xml_content(self, jdo_name: str):
        """
        讀取xml內容
        :param jdo_name: str 檔案類型
        """
        self.json_param |= {'function': 'getXml', 'type': jdo_name}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def append_customer(self, customer_id: str, customer_name: str):
        """
        EIP系統新增客戶
        :param customer_id: str 客戶代號
        :param customer_name: str 客戶名稱
        """
        self.json_param |= {'function': 'appendCustomer', 'customerId': customer_id, 'customerTitle': customer_name}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def get_signed_subjects(self, non_read: str = 'false'):
        """
        讀取已簽核完畢的表單列表
        :param non_read: str 設定回傳單號為已讀取過or未讀取過
        """
        self.json_param |= {'function': 'getSignedSubjects', 'all': non_read}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)

    def update_role(self, role_id: str, caption: str, description: str, with_structure: int, player: str) -> str:
        """
        更新角色
        :param role_id: str 角色識別碼
        :param caption: str 角色名稱
        :param description: str 說明
        :param with_structure: int 組織結構考量方式(0: 不考慮, 1: 簽核時僅挑出 填單人上層主管, 2:  簽核時僅挑出 簽核人上層主管)
        :param player: str 擔當者列表
        """
        self.json_param |= {'function': 'updateRole', 'id': role_id, 'caption': caption, 'description': description, 'withStructure': with_structure, 'player': player}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text)
    
    def upd_data_form_V2(self, subject_id: str, row_index: str, **data):
        """
        修改表單(統計表格欄位)
        :param subject_id: str 表單單號
        :param row_index: str 修改列數
        :param return_form: 回傳值
        :param data: dict 修改欄位名稱&內容字典
        """
        self.json_param |= {'function': 'updateDataForm', 'subjectId': subject_id, 'rowIndex': row_index, 'returnForm': 'false'}
        for key, content in data.items():
            self.json_param |= {key: content}
        resp = requests.post(url=self.url, data=self.json_param)
        return str(resp.text).replace('\r', '\n')