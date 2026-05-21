import jwt
import datetime
from flask import request, jsonify, Blueprint
from programs.core.db_process.jw_common.main import qry_employee

SECRET_KEY = "1234567890"

bp_main = Blueprint('login_api', __name__)


@bp_main.route('/test', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    employee = qry_employee(username)

    if not employee:
        return jsonify({"success": False, "message": "帳號不存在"}), 401

    if (employee['id'] or '')[-4:] != password:
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
