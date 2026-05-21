from google.oauth2.service_account import Credentials
import gspread


def google_certificate(google_sheet_url: str):
    """
    google sheet認證
    :param google_sheet_url: str Google Sheet url
    """
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    cred_s = Credentials.from_service_account_file("file/google_sheet_certificate/api_key.json", scopes=scope)
    gs = gspread.authorize(cred_s)
    sheet = gs.open_by_url(google_sheet_url)
    return sheet


def google_certificate_test(google_sheet_url: str):
    """
    google sheet認證
    :param google_sheet_url: str Google Sheet url
    """
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    cred_s = Credentials.from_service_account_file("file/google_sheet_certificate/api_key.json", scopes=scope)
    gs = gspread.authorize(cred_s)
    sheet = gs.open_by_url(google_sheet_url)
    return sheet