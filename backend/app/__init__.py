from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 初始化API对象但先不关联Flask应用
    from app.api import api
    
    # 导入模型（确保在创建表之前导入）
    from app.models import Course, Teacher, Evaluation, Comment
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 先导入API模块，让它们注册路由
    from app.api import courses, teachers, evaluations, comments, rankings, discussions, rankings_frontend
    
    # 然后再将API对象与Flask应用关联，确保所有路由都已注册
    api.init_app(app)
    
    return app