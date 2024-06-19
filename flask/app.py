
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from config import Config
from models import db
from routes import bp as auth_bp
import subprocess

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

# 配置 CORS
CORS(app)

# 创建应用上下文并创建表格
with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)
