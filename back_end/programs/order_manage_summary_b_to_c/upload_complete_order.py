import pandas as pd
import threading
from programs.core.db_process.xin_tea.order_manage_summary_b_to_c import main as xin_tea
from programs.core.work_day.work_day import next_working_day
from datetime import datetime
from programs.order_manage_summary_b_to_c.sync_google_sheet import sync_item_detail_in_out


class UploadCompleteOrderChange:
    def __init__(self, new_order, e_commerce_platform: str, direct_data: bool = False):
        if not direct_data:
            self.new_order: list = pd.read_excel(new_order).fillna('').to_dict(orient='records')
        else:
            self.new_order: list = new_order
        self.e_commerce_platform = e_commerce_platform

    def change_data(self):
        """依電商平台決定轉換資料邏輯"""
        return self.__upload_complete_order()
    
    def __upload_complete_order(self) -> str:
        """完成訂單處理"""
        result = self.__check_excel_column_correct()
        if result is True:
            # 檢查訂單是否可以匯入
            message: str
            error_order: list
            error_num: int
            vendor_no_check_num: int
            order_no_exist_num: int
            success_num: int
            error_status_num: int
            order_no_not_to_vendor_num: int
            error_order_status_num: int
            message, error_order, error_num, vendor_no_check_num, order_no_exist_num, success_num, error_status_num, order_no_not_to_vendor_num, error_order_status_num = self.__check_import_complete()
            print('message', message)
            print('error_order', error_order)
            # 完成訂單處理
            exe_result: bool
            error_message: str
            exe_result, error_message = self.__upd_complete_order_status(error_order)
            final_message: str = message + error_message
            if final_message:
                # 將錯誤訊息寫入table
                error_message: list = [
                    (
                        self.e_commerce_platform, '完成訂單上傳', message
                    )
                ]
                xin_tea.crt_upload_record(error_message)
            if exe_result:
                # 在背景執行緒中執行 Google Sheet 同步(出入明細)
                threading.Thread(target=sync_item_detail_in_out, daemon=True).start()
                return f"{self.e_commerce_platform}完成訂單上傳成功筆數: {success_num}，失敗筆數: {error_num}<br>廠商未確認筆數: {vendor_no_check_num}，訂單號碼不存在筆數: {order_no_exist_num}， \
                訂單狀態不符合完成訂單匯入條件筆數: {error_status_num}，訂單號碼尚未拋轉給廠商筆數: {order_no_not_to_vendor_num}, 訂單號碼狀態不符合完成訂單匯入條件筆數: {error_order_status_num}"
            return f"{self.e_commerce_platform}完成訂單上傳失敗!"
        return result
    
    
    def __check_import_complete(self) -> tuple[str, list]:
        """檢查完成訂單是否可匯入"""
        error_msg: str = ''
        check_order: list = []
        error_order: list = []
        error_num: int = 0
        success_num: int = 0
        vendor_no_check_num: int = 0
        order_no_exist_num: int = 0
        error_status_num: int = 0
        order_no_not_to_vendor_num: int = 0
        error_order_status_num: int = 0
        
        for per_detail in self.new_order:
            # 根據不同電商平台獲取訂單號
            if self.e_commerce_platform in ['line 禮物', 'pinkoi']:
                order_no = str(per_detail.get('訂單編號'))
            elif self.e_commerce_platform == 'shopline':
                order_no = str(per_detail.get('訂單號碼'))
            else:
                continue  # 不支援的平台跳過處理
                
            # 已處理過的訂單不再檢查
            if order_no in check_order:
                continue
                
            # 記錄已處理的訂單
            check_order.append(order_no)

            # 狀態不符合完成訂單匯入條件
            if self.e_commerce_platform == 'line 禮物':
                order_status = per_detail.get('訂單狀態')
                if order_status not in ['配送中', '配送完成', '已取消']:
                    error_num += 1
                    error_status_num += 1
                    error_msg += f"訂單號碼 {order_no} 狀態為 {order_status}，不符合完成訂單匯入條件!<br>"
                    error_order.append(order_no)
                    continue
                
            elif self.e_commerce_platform == 'shopline':
                order_status = per_detail.get('訂單狀態')
                if order_status not in ['已完成', '已取消']:
                    error_num += 1
                    error_status_num += 1
                    error_msg += f"訂單號碼 {order_no} 狀態為 {order_status}，不符合完成訂單匯入條件!<br>"
                    error_order.append(order_no)
                    continue
            elif self.e_commerce_platform == 'pinkoi':
                order_status = per_detail.get('訂單類型')
                if order_status not in ['已完成', '已出貨', '已取消']:
                    error_num += 1
                    error_status_num += 1
                    error_msg += f"訂單號碼 {order_no} 狀態為 {order_status}，不符合完成訂單匯入條件!<br>"
                    error_order.append(order_no)
                    continue
                
            # 檢查訂單是否存在
            order_data = xin_tea.qry_order_no(order_no)
            if not order_data:
                error_num += 1
                order_no_exist_num += 1
                error_msg += f"訂單號碼 {order_no} 不存在!<br>"
                error_order.append(order_no)
                continue
            else:
                # 該訂單號碼是否允許變7.1(結案狀態)
                if order_data[0]['status'] not in ['2.1', '5.1']:
                    error_num += 1
                    error_msg += f"訂單號碼 {order_no} 之訂單狀態為 {order_data[0]['status']}，不符合完成訂單匯入條件!<br>"
                    error_order.append(order_no)
                    error_order_status_num += 1
                    continue
                
            # 訂單號碼已存在檢查是否有廠商未確認的訂單
            is_vendor_check: bool = True
            to_vendor_order_data = xin_tea.qry_order_no_to_vendor(order_no)
            if len(to_vendor_order_data) > 0:
                for per_order in to_vendor_order_data:
                    if per_order.get('vendor_check') == '0':
                        error_num += 1
                        vendor_no_check_num += 1
                        error_msg += f"訂單號碼{order_no}廠商未確認!<br>"
                        error_order.append(order_no)
                        is_vendor_check = False
                        break  # 找到一個未確認就可以跳出循環
            else:
                # 根本尚未拋轉給廠商
                error_num += 1
                order_no_not_to_vendor_num += 1
                is_vendor_check = False
                error_msg += f"訂單號碼 {order_no} 尚未拋轉給廠商!<br>"
            if is_vendor_check:
                success_num += 1
        return error_msg, error_order, error_num, vendor_no_check_num, order_no_exist_num, success_num, error_status_num, order_no_not_to_vendor_num, error_order_status_num
    
    
    def __upd_complete_order_status(self, error_order: list) -> bool | str:
        """
        更新完成訂單狀態
        :param error_order: 錯誤訂單號碼
        """
        upd_order_param: list = []
        upd_vendor_close_param: list = []
        upd_vendor_cancel_param: list = []
        upd_use_detail: list = []
        check_order: list = []
        error_message: str = ''
        for per_order in self.new_order:
            # 訂單已經出貨-結案or取消略過
            # LINE 禮物
            if self.e_commerce_platform == 'line 禮物':
                order_no: str = str(per_order.get('訂單編號'))
                close_data: list = xin_tea.qry_order_no_already_close(order_no)
                # 已出貨-結案取消不處理
                if close_data:
                    continue
                # 錯誤訂單號碼不處理
                if order_no in error_order:
                    continue
                order_status: str = per_order.get('訂單狀態')
                if order_no in check_order:
                    continue
                # 不符合結案or取消條件不處理
                if order_status not in ['配送中', '配送完成', '已取消']:
                    continue
                # 查詢當前該訂單
                order_data: list = xin_tea.qry_order_no(order_no)
                status: str =  order_data[0]['status']
                # 查詢該狀態完成訂單匯入後的狀態
                status_data: list = xin_tea.qry_status(status)
                # 結案
                if order_status in ['配送中', '配送完成']:
                    change_status: str = status_data[0]['complete_close_status']
                    complete_error: str = status_data[0]['complete_close_error']
                    to_vendor_status: str = xin_tea.qry_status(change_status)[0]['vendor_look_status']
                    # 更新廠商狀態
                    upd_vendor_close_param.append(
                        (
                            to_vendor_status, order_no
                        )
                    )
                    # 更新用料明細
                    upd_use_detail.append(
                        ('1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_no)
                    )
                # 取消
                elif order_status in ['已取消']:
                    change_status: str = status_data[0]['complete_cancel_status']
                    complete_error: str = status_data[0]['complete_cancel_error']
                    to_vendor_status: str = xin_tea.qry_status(change_status)[0]['vendor_look_status']
                    print('to_vendor_status', to_vendor_status)
                    # 更新廠商狀態
                    upd_vendor_cancel_param.append(
                        (
                            to_vendor_status, '0', order_no
                        )
                    )
                    # 更新用料明細
                    upd_use_detail.append(
                        ('-1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_no)
                    )
                # 其他狀態不處理
                else:
                    error_message += f"訂單號碼 {order_no} 狀態為 {order_status}，不符合完成訂單匯入條件!\n"
                # 更新訂單管理總表
                upd_order_param.append(
                    (
                        change_status, complete_error, order_no
                    )
                )
            elif self.e_commerce_platform == 'shopline':
                order_no: str = str(per_order.get('訂單號碼'))
                close_data: list = xin_tea.qry_order_no_already_close(order_no)
                # 已出貨-結案取消不處理
                if close_data:
                    continue
                # 錯誤訂單號碼不處理
                if order_no in error_order:
                    continue
                order_status: str = per_order.get('訂單狀態')
                if order_no in check_order:
                    continue
                # 不符合結案or取消條件不處理
                if order_status not in ['已完成', '已取消']:
                    continue
                # 查詢當前該訂單
                order_data: list = xin_tea.qry_order_no(order_no)
                status: str =  order_data[0]['status']
                # 查詢該狀態完成訂單匯入後的狀態
                status_data: list = xin_tea.qry_status(status)
                # 結案
                if order_status in ['已完成']:
                    change_status: str = status_data[0]['complete_close_status']
                    complete_error: str = status_data[0]['complete_close_error']
                    
                    to_vendor_status: str = xin_tea.qry_status(change_status)[0]['vendor_look_status']
                    print('change_status', change_status)
                    print('to_vendor_status', to_vendor_status)
                    # 更新廠商狀態
                    upd_vendor_close_param.append(
                        (
                            to_vendor_status, order_no
                        )
                    )
                    # 更新用料明細
                    upd_use_detail.append(
                        ('1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_no)
                    )
                # 取消
                elif order_status in ['已取消']:
                    change_status: str = status_data[0]['complete_cancel_status']
                    complete_error: str = status_data[0]['complete_cancel_error']
                    to_vendor_status: str = xin_tea.qry_status(change_status)[0]['vendor_look_status']
                    # 更新廠商狀態
                    upd_vendor_cancel_param.append(
                        (
                            to_vendor_status, '0', order_no
                        )
                    )
                    # 更新用料明細
                    upd_use_detail.append(
                        ('-1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_no)
                    )
                # 其他狀態不處理
                else:
                    error_message += f"訂單號碼 {order_no} 狀態為 {order_status}，不符合完成訂單匯入條件!\n"
                # 更新訂單管理總表
                upd_order_param.append(
                    (
                        change_status, complete_error, order_no
                    )
                )
            elif self.e_commerce_platform == 'pinkoi':
                order_no: str = str(per_order.get('訂單編號'))
                close_data: list = xin_tea.qry_order_no_already_close(order_no)
                # 已出貨-結案取消不處理
                if close_data:
                    continue
                # 錯誤訂單號碼不處理
                if order_no in error_order:
                    continue
                order_status: str = per_order.get('訂單類型')
                if order_no in check_order:
                    continue
                # 不符合結案or取消條件不處理
                if order_status not in ['已完成', '已出貨', '已取消']:
                    continue
                # 查詢當前該訂單
                order_data: list = xin_tea.qry_order_no(order_no)
                status: str =  order_data[0]['status']
                # 查詢該狀態完成訂單匯入後的狀態
                status_data: list = xin_tea.qry_status(status)
                # 結案
                if order_status in ['已完成', '已出貨']:
                    change_status: str = status_data[0]['complete_close_status']
                    complete_error: str = status_data[0]['complete_close_error']
                    to_vendor_status: str = xin_tea.qry_status(change_status)[0]['vendor_look_status']
                    print('to_vendor_status', to_vendor_status)
                    # 更新廠商狀態
                    upd_vendor_close_param.append(
                        (
                            to_vendor_status, order_no
                        )
                    )
                    # 更新用料明細
                    upd_use_detail.append(
                        ('1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_no)
                    )
                # 取消
                elif order_status in ['已取消']:
                    change_status: str = status_data[0]['complete_cancel_status']
                    complete_error: str = status_data[0]['complete_cancel_error']
                    to_vendor_status: str = xin_tea.qry_status(change_status)[0]['vendor_look_status']
                    print('to_vendor_status', to_vendor_status)
                    # 更新廠商狀態
                    upd_vendor_cancel_param.append(
                        (
                            to_vendor_status, '0', order_no
                        )
                    )
                    # 更新用料明細
                    upd_use_detail.append(
                        ('-1', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), order_no)
                    )
                # 其他狀態不處理
                else:
                    error_message += f"訂單號碼 {order_no} 狀態為 {order_status}，不符合完成訂單匯入條件!\n"
                # 更新訂單管理總表
                upd_order_param.append(
                    (
                        change_status, complete_error, order_no
                    )
                )
        result: bool = xin_tea.upd_complete_order_data(upd_order_param, upd_vendor_close_param, upd_vendor_cancel_param, upd_use_detail)
        return result, error_message
    
    def __check_excel_column_correct(self) -> bool | str:
        """
        檢查Excel欄位是否正確
        :return: True 如果欄位正確，否則返回錯誤訊息
        """
        try:
            # 取得上傳檔案的欄位名稱
            column_key = self.new_order[0].keys()
            
            # 從資料庫取得該平台需要的欄位設定
            check_column: list = xin_tea.qry_e_commerce_platform_column(self.e_commerce_platform)
            # 檢查是否有取得欄位設定
            if not check_column:
                return f'無法取得 {self.e_commerce_platform} 的欄位設定'
                
            # 取得資料庫中定義的必要欄位名稱列表（依照 column_pri_seq 排序）
            required_columns = [col['column_name'].strip() for col in sorted(check_column, key=lambda x: x['column_pri_seq'])]
            
            # 檢查是否所有必要欄位都存在於上傳檔案中
            missing_columns = [col for col in required_columns if col not in column_key]
            
            if missing_columns:
                return '檔案格式錯誤!'
            return True
        except Exception as e:
            return f'檢查欄位時發生錯誤: {str(e)}'