"""
统一的JWT认证工具模块
"""
import jwt
import os
from functools import wraps
from flask import request, jsonify
from app.models import User

def get_current_user():
    """
    从请求头中获取当前用户信息

    Returns:
        User: 当前登录的用户对象，如果未登录或token无效则返回None
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    try:
        secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        return user
    except Exception:
        return None

def login_required(f):
    """
    装饰器：要求用户必须登录才能访问

    使用方法:
        @login_required
        def some_resource_method(self):
            user = get_current_user()
            # user 保证不为None
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401
        return f(*args, **kwargs)
    return decorated_function
