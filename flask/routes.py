from flask import Blueprint, request, send_file,jsonify
from models import db, User
import subprocess
import os
import logging
bp = Blueprint('auth', __name__)

# 初始化日志记录
logging.basicConfig(level=logging.DEBUG)

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


# 定义图片保存路径
IMAGE_DIR = r'C:\Users\17662\Desktop\数据库\text-and-data\文本分析挖掘'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)


@bp.route('/api/get_image/<image_name>', methods=['GET'])
def get_image(image_name):
    IMAGE_DIR = r'C:\Users\17662\Desktop\数据库\text-and-data\文本分析挖掘'
    try:
        image_path = os.path.join(IMAGE_DIR, image_name)
        logging.debug(f"Request for image: {image_name}")
        logging.debug(f"Full image path: {image_path}")

        if os.path.exists(image_path):
            logging.debug(f"Image {image_name} found")
            return send_file(image_path, mimetype='image/png')
        else:
            logging.debug(f"Image {image_name} not found")
            return jsonify({'code': 404, 'message': 'Image not found'}), 404
    except Exception as e:
        logging.error(f"Error getting image {image_name}: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# 确保其他部分代码（例如 run_analysis 路由）也正确实现并记录日志
@bp.route('/api/run_analysis', methods=['POST'])
def run_analysis():
    IMAGE_DIR = r'C:\Users\17662\Desktop\数据库\text-and-data\文本分析挖掘'
    script_path = r'C:\Users\17662\Desktop\数据库\text-and-data\文本分析挖掘\数据分布分析.py'

    try:
        # 设置环境变量以便脚本知道图片保存路径
        env = os.environ.copy()
        env['IMAGE_DIR'] = IMAGE_DIR

        # 打开日志文件
        with open('script_output.log', 'w') as log_file:
            # 执行脚本，并将标准输出和标准错误重定向到日志文件中
            result = subprocess.run(['python', script_path], check=True, env=env, stdout=log_file, stderr=log_file)

        # 假设生成的图片保存在特定目录中，并且文件名是固定的
        image_filenames = ['ph1.png', 'ph2.png', 'ph3.png', 'ph4.png', 'ph5.png']
        return jsonify({'code': 200, 'images': image_filenames}), 200
    except subprocess.CalledProcessError as e:
        logging.error(f"CalledProcessError: {e}")
        with open('script_output.log', 'r') as log_file:
            logging.error(log_file.read())
        return jsonify({'code': 500, 'message': str(e)}), 500
    except Exception as e:
        logging.error(f"Error running analysis: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500
