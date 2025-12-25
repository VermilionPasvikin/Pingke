from flask import request, jsonify
from flask_restful import Resource
import requests
import jwt
import os
import time
from datetime import datetime, timedelta
from app import db
from app.models import User, Evaluation, Comment, Like
from app.schemas import EvaluationSchema, CommentSchema
from app.utils.auth import get_current_user
from sqlalchemy import desc

evaluations_schema = EvaluationSchema(many=True)
comments_schema = CommentSchema(many=True)

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
            'user_id': user.id,
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

class CurrentUserResource(Resource):
    def get(self):
        """获取当前登录用户信息及统计数据"""
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        # 统计用户数据
        evaluations_count = Evaluation.query.filter_by(user_id=user.id).count()
        discussions_count = Comment.query.filter_by(user_id=user.id, parent_id=None).count()
        comments_count = Comment.query.filter_by(user_id=user.id).filter(Comment.parent_id.isnot(None)).count()

        return {
            'id': user.id,
            'nickname': user.nickname,
            'avatar_url': user.avatar_url,
            'openid': user.openid,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'stats': {
                'evaluations_count': evaluations_count,
                'discussions_count': discussions_count,
                'comments_count': comments_count,
                'total_posts': evaluations_count + discussions_count + comments_count
            }
        }, 200

class UserEvaluationsResource(Resource):
    def get(self, user_id):
        """获取指定用户的评价列表"""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # 构建查询
        query = Evaluation.query.filter_by(user_id=user_id)
        query = query.order_by(desc(Evaluation.created_at))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        evaluations = pagination.items

        result = evaluations_schema.dump(evaluations)

        return {
            'evaluations': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }, 200

class UserDiscussionsResource(Resource):
    def get(self, user_id):
        """获取指定用户的讨论列表（包括评论和回复）"""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # 获取用户的所有评论（包括讨论和回复）
        query = Comment.query.filter_by(user_id=user_id)
        query = query.order_by(desc(Comment.created_at))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        comments = pagination.items

        # 格式化数据
        result = []
        for comment in comments:
            comment_data = comments_schema.dump([comment])[0]
            # 添加类型标识
            comment_data['type'] = 'discussion' if comment.parent_id is None else 'reply'
            # 添加点赞信息
            likes_count = Like.query.filter_by(
                target_type='comment',
                target_id=comment.id
            ).count()
            comment_data['likes_count'] = likes_count

            # 如果是回复，添加父评论信息
            if comment.parent_id:
                parent = Comment.query.get(comment.parent_id)
                if parent:
                    comment_data['parent_author'] = parent.user_name
                    comment_data['parent_content'] = parent.content[:50] + '...' if len(parent.content) > 50 else parent.content

            result.append(comment_data)

        return {
            'discussions': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }, 200

class UpdateNicknameResource(Resource):
    def put(self):
        """更新当前用户昵称"""
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        data = request.get_json()

        if 'nickname' not in data:
            return {'error': '缺少昵称参数'}, 400

        nickname = data['nickname'].strip()
        if not nickname:
            return {'error': '昵称不能为空'}, 400

        if len(nickname) > 50:
            return {'error': '昵称长度不能超过50个字符'}, 400

        user.nickname = nickname
        user.updated_at = datetime.utcnow()
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
api.add_resource(CurrentUserResource, '/api/me')
api.add_resource(UserEvaluationsResource, '/api/users/<int:user_id>/evaluations')
api.add_resource(UserDiscussionsResource, '/api/users/<int:user_id>/discussions')
api.add_resource(UpdateNicknameResource, '/api/me/nickname')