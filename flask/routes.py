from flask import Blueprint, request, jsonify
from models import db, User
import subprocess

bp = Blueprint('auth', __name__)


@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'code': 400, 'message': 'Missing fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': 'User already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'code': 200, 'message': 'User registered successfully'}), 200


@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password', 'code': 400}), 400

    return jsonify({'message': 'Login successful', 'code': 200}), 200


@bp.route('/api/run_script', methods=['POST'])
def run_script():
    data = request.get_json()
    num = data.get('grabNum')
    id = data.get('grabId')

    if not num or not id:
        return jsonify({'code': 400, 'message': 'Missing script num or Id'}), 400

    # 构建脚本路径
    script_path = r'C:\Users\17662\Desktop\数据库\text-and-data\大众点评爬虫\main.py'

    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',  # 设置编码为 UTF-8
            check=True
        )
        return jsonify({'status': 'success', 'message': 'main.py script executed successfully!', 'output': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'code': 500, 'message': 'Script execution failed', 'error': e.stderr}), 500