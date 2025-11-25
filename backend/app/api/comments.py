from flask import request, jsonify
from flask_restful import Resource
import jwt
import os
from app import db
from app.models import Comment, Course, Like, User
from app.schemas import CommentSchema
from sqlalchemy import desc

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

def get_current_user():
    """从请求头中获取当前用户信息"""
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

class CommentsResource(Resource):
    def get(self):
        # 获取评论列表，可以按课程筛选
        course_id = request.args.get('course_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 获取当前登录用户
        user = get_current_user()
        
        # 构建查询，只获取顶级评论（非回复）
        query = Comment.query.filter(Comment.parent_id.is_(None))
        
        if course_id:
            query = query.filter(Comment.course_id == course_id)
        
        # 按创建时间降序排序
        query = query.order_by(desc(Comment.created_at))
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        comments = pagination.items
        
        # 序列化评论，包括回复
        result = []
        for comment in comments:
            comment_data = comment_schema.dump(comment)
            # 计算回复数量
            comment_data['reply_count'] = len(comment.replies)
            
            # 获取评论点赞数
            likes_count = Like.query.filter_by(
                target_type='comment',
                target_id=comment.id
            ).count()
            comment_data['likes_count'] = likes_count
            
            # 检查当前用户是否点赞
            is_liked = False
            if user:
                is_liked = Like.query.filter_by(
                    user_id=user.id,
                    target_type='comment',
                    target_id=comment.id
                ).first() is not None
            comment_data['is_liked'] = is_liked
            
            result.append(comment_data)
        
        return {
            'comments': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }, 200
    
    def post(self):
        # 添加新评论或回复
        data = request.get_json()
        
        # 验证数据
        errors = comment_schema.validate(data)
        if errors:
            return jsonify({'error': errors}), 400
        
        # 检查课程是否存在
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # 如果是回复，检查父评论是否存在
        if data.get('parent_id'):
            parent_comment = Comment.query.get(data['parent_id'])
            if not parent_comment:
                return jsonify({'error': 'Parent comment not found'}), 404
            # 确保父评论属于同一课程
            if parent_comment.course_id != data['course_id']:
                return jsonify({'error': 'Parent comment belongs to a different course'}), 400
        
        # 获取当前登录用户
        user = get_current_user()
        
        # 创建评论
        new_comment = Comment(
            course_id=data['course_id'],
            user_id=user.id if user else None,
            user_name=user.nickname if user else data.get('user_name', '匿名用户'),
            content=data['content'],
            parent_id=data.get('parent_id')
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        result = comment_schema.dump(new_comment)
        result['is_liked'] = False  # 新创建的评论默认未点赞
        return jsonify(result), 201

class CommentResource(Resource):
    def get(self, comment_id):
        # 获取单个评论详情，包括所有回复
        comment = Comment.query.get_or_404(comment_id)
        result = comment_schema.dump(comment)
        return result, 200
    
    def put(self, comment_id):
        # 更新评论内容（仅允许评论者自己更新）
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()
        
        # 验证用户权限
        if comment.user_id and data.get('user_id') != comment.user_id:
            return {'error': 'Unauthorized to update this comment'}, 403
        
        # 验证数据
        if 'content' in data:
            if not data['content'] or not data['content'].strip():
                return {'error': 'Comment content cannot be empty'}, 400
        
        # 更新字段
        if 'content' in data:
            comment.content = data['content']
        
        db.session.commit()
        
        result = comment_schema.dump(comment)
        return jsonify(result), 200
    
    def delete(self, comment_id):
        # 删除评论（仅允许评论者自己删除）
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()
        
        # 验证用户权限
        if comment.user_id and data.get('user_id') != comment.user_id:
            return jsonify({'error': 'Unauthorized to delete this comment'}), 403
        
        # 删除评论及其所有回复
        def delete_comment_tree(comment):
            # 递归删除所有回复
            for reply in comment.replies:
                delete_comment_tree(reply)
            db.session.delete(comment)
        
        delete_comment_tree(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200

class CommentRepliesResource(Resource):
    def get(self, comment_id):
        # 获取评论的所有回复
        comment = Comment.query.get_or_404(comment_id)
        replies = comment.replies
        result = comments_schema.dump(replies)
        return jsonify(result), 200

class CommentLikeResource(Resource):
    def post(self, comment_id):
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401
        
        # 获取评论
        comment = Comment.query.get_or_404(comment_id)
        
        # 检查用户是否已经点赞
        existing_like = Like.query.filter_by(
            user_id=user.id,
            target_type='comment',
            target_id=comment_id
        ).first()
        
        if existing_like:
            # 如果已经点赞，则取消点赞
            db.session.delete(existing_like)
            db.session.commit()
            is_liked = False
        else:
            # 如果未点赞，则添加点赞
            new_like = Like(
                user_id=user.id,
                target_type='comment',
                target_id=comment_id
            )
            db.session.add(new_like)
            db.session.commit()
            is_liked = True
        
        # 获取点赞数量
        likes_count = Like.query.filter_by(
            target_type='comment',
            target_id=comment_id
        ).count()
        
        return { 
            'message': '操作成功',
            'likes_count': likes_count,
            'is_liked': is_liked
        }, 200

# 注册路由
# 延迟导入api对象以避免循环导入
from app.api import api
api.add_resource(CommentsResource, '/api/comments')
api.add_resource(CommentResource, '/api/comments/<int:comment_id>')
api.add_resource(CommentRepliesResource, '/api/comments/<int:comment_id>/replies')
api.add_resource(CommentLikeResource, '/api/comments/<int:comment_id>/like')