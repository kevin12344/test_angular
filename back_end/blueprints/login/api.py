import os
import hmac
import hashlib
import secrets
import jwt
import datetime
from flask import request, jsonify, Blueprint
from programs.core.db_process.jw_common.main import qry_employee

SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_urlsafe(64)

bp_main = Blueprint('login_api', __name__)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


@bp_main.route('/test', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = data.get('username', '').strip()
    password_hash = data.get('password', '').strip().lower()

    employee = qry_employee(username)

    if not employee:
        return jsonify({"success": False, "message": "帳號不存在"}), 401

    expected_plain = (employee['id'] or '')[-4:]
    expected_hash = _sha256_hex(expected_plain)
    if not (hmac.compare_digest(expected_hash, password_hash)
            or hmac.compare_digest(expected_plain, password_hash)):
        return jsonify({"success": False, "message": "密碼錯誤"}), 401

    now = datetime.datetime.now(datetime.timezone.utc)
    token = jwt.encode({
        'user': username,
        'iat': now,
        'exp': now + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"success": True, "token": token, "message": "Login successful"})


@bp_main.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "未授權"}), 401
    try:
        payload = jwt.decode(auth_header.split(' ')[1], SECRET_KEY, algorithms=["HS256"])
        employee = qry_employee(payload['user'])
        if not employee:
            return jsonify({"message": "查無員工資料"}), 404
        return jsonify({
            "employee_id": employee['employee_id'],
            "employee_name": employee['employee_name']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token 已過期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token 無效"}), 401
