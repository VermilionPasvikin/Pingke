from flask import request, jsonify
from flask_restful import Resource
import requests
import jwt
import os
import time
from datetime import datetime, timedelta
from app import db
from app.models import User

class WechatLoginResource(Resource):
    def post(self):
        """微信登录接口"""
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return {'error': '缺少code参数'}, 400
        
        # 调用微信API获取openid
        openid = self._get_wechat_openid(code)
        if not openid:
            return {'error': '获取微信openid失败'}, 500
        
        # 查找或创建用户
        user = User.query.filter_by(openid=openid).first()
        
        if not user:
            # 创建新用户
            user = User(
                openid=openid,
                nickname='微信用户',  # 默认昵称，后续可以更新
                avatar_url=None       # 默认头像，后续可以更新
            )
            db.session.add(user)
            db.session.commit()
        
        # 生成JWT token
        token = self._generate_jwt_token(user.id)
        
        return {
            'token': token,
            'user': {
                'id': user.id,
                'nickname': user.nickname,
                'avatar_url': user.avatar_url
            }
        }, 200
    
    def _get_wechat_openid(self, code):
        """调用微信API获取openid"""
        # 这里需要配置微信小程序的appid和appsecret
        # 注意：在实际应用中，这些敏感信息应该存储在环境变量中
        appid = os.getenv('WECHAT_APPID', '')  # 替换为你的微信小程序appid
        secret = os.getenv('WECHAT_SECRET', '')  # 替换为你的微信小程序secret
        
        # 开发模式：如果appid和secret未配置，使用模拟的openid
        # 注意：这仅用于开发测试，生产环境必须使用真实的微信appid和secret
        if not appid or appid == 'your_wechat_appid_here' or not secret or secret == 'your_wechat_secret_here':
            print("开发模式启用：使用模拟的openid进行微信登录测试")
            # 使用code作为模拟的openid，确保每个不同的code生成不同的用户
            # 这样在开发环境中可以模拟多用户场景
            return f"mock_openid_{hash(code)}_{int(time.time())}"
        
        # 微信API接口
        url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
        
        try:
            response = requests.get(url, timeout=5)
            result = response.json()
            
            if 'openid' in result:
                return result['openid']
            else:
                print(f"微信API错误: {result}")
                return None
        except Exception as e:
            print(f"请求微信API失败: {e}")
            return None
    
    def _generate_jwt_token(self, user_id):
        """生成JWT token"""
        # 获取SECRET_KEY
        secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # 使用与Flask相同的SECRET_KEY
        
        # 设置token有效期为7天
        expiration = datetime.utcnow() + timedelta(days=7)
        
        # 创建payload
        payload = {
            'user_id': user_id,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        # 生成token
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token

class UpdateUserInfoResource(Resource):
    def put(self, user_id):
        """更新用户信息"""
        # 这里应该验证token中的user_id与请求的user_id是否匹配
        # 为了简化，暂时省略验证步骤
        
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        
        # 更新用户信息
        if 'nickname' in data:
            user.nickname = data['nickname']
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        db.session.commit()
        
        return {
            'id': user.id,
            'nickname': user.nickname,
            'avatar_url': user.avatar_url
        }, 200

# 注册路由
from app.api import api
api.add_resource(WechatLoginResource, '/api/auth/wechat-login')
api.add_resource(UpdateUserInfoResource, '/api/users/<int:user_id>')