from programs.core.cloud_eip.web_service import EIPService

# EIP 底層架構
class EipBaseFrame:
    def __init__(self, apikey: str, subject_id: str, sender: str, result: str, env_id: str):
        self.eip_service = EIPService()
        self.eip_param: dict = {'subject_id': subject_id, 'sender': sender, 'result': result}
        self.origin_data: dict = self.eip_service.qry(self.eip_param['subject_id'])
        self.form_name: str = self.origin_data.get('formName')
        self.apikey: str = apikey
        self.env_id: str = env_id