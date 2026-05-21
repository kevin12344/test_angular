import pandas as pd
from io import BytesIO
from programs.core.db_process.xin_tea.permission import main as xin_tea_permission

class UploadAccountInfo:
    def __init__(self, account_info: BytesIO):
        self.account_info: list = pd.read_excel(account_info).fillna('').to_dict(orient='records')
    
    def update_account_and_dept(self) -> str:
        """更新帳號資料"""
        upd_data: list = []
        crt_data: list = []
        dept_crt: list = []
        check_dept: list = []
        for per_detail in self.account_info:
            account: str = per_detail.get('帳號')
            dept: str = per_detail.get('任職部門')
            account_data: list = xin_tea_permission.qry_account_permission(account)
            dept_data: list = xin_tea_permission.qry_dept_permission(dept)
            if account_data:
                upd_data.append(
                    (
                        account, dept
                    )
                )
            else:
                crt_data.append(
                    (
                        account, dept, per_detail.get('姓名')
                    )
                )
            if not dept_data:
                if dept not in check_dept:
                    check_dept.append(dept)
                    dept_crt.append(
                        (
                            dept,
                        )
                    )
        """更新部門"""
        if len(dept_crt) == 0 and len(crt_data) == 0 and len(upd_data) == 0:
            return '無新資料需更新'
        result: bool = xin_tea_permission.crt_or_upd_account_info_dept(crt_data, upd_data, dept_crt)
        if result: 
            return '人員帳號資料更新成功!'
        return '人員帳號資料更新失敗!'