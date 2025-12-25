from flask import request, jsonify
from flask_restful import Resource
from app import db
from app.models import Comment, Course, Like, User
from app.schemas import CommentSchema
from app.utils.auth import get_current_user
from sqlalchemy import desc
from datetime import datetime

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

class DiscussionsResource(Resource):
    def get(self):
        # 获取讨论列表（等同于评论列表的顶级评论）
        course_id = request.args.get('course_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # 获取当前登录用户
        user = get_current_user()
        
        # 构建查询，只获取顶级评论（非回复）
        query = Comment.query.filter(Comment.parent_id.is_(None))
        
        if course_id:
            query = query.filter(Comment.course_id == course_id)
        
        # 按创建时间降序排序
        query = query.order_by(desc(Comment.created_at))
        
        # 分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        comments = pagination.items
        
        # 序列化评论，包括回复
        result = []
        for comment in comments:
            comment_data = comment_schema.dump(comment)
            
            # 获取评论点赞数
            likes_count = Like.query.filter_by(
                target_type='comment',
                target_id=comment.id
            ).count()
            
            # 检查当前用户是否点赞
            is_liked = False
            if user:
                is_liked = Like.query.filter_by(
                    user_id=user.id,
                    target_type='comment',
                    target_id=comment.id
                ).first() is not None
            
            # 获取前3条回复
            comment_data['replies'] = []
            for reply in comment.replies[:3]:
                reply_data = comment_schema.dump(reply)
                
                # 获取回复点赞数
                reply_likes_count = Like.query.filter_by(
                    target_type='comment',
                    target_id=reply.id
                ).count()
                
                # 检查当前用户是否点赞回复
                reply_is_liked = False
                if user:
                    reply_is_liked = Like.query.filter_by(
                        user_id=user.id,
                        target_type='comment',
                        target_id=reply.id
                    ).first() is not None
                
                # 为回复设置author字段，与主评论处理方式一致
                reply_data['author'] = reply_data['user_name']
                reply_data['likes_count'] = reply_likes_count
                reply_data['is_liked'] = reply_is_liked
                comment_data['replies'].append(reply_data)
            
            # 回复总数
            comment_data['replies_count'] = len(comment.replies)
            # 重命名字段以匹配前端
            comment_data['id'] = comment_data['id']
            comment_data['author'] = comment_data['user_name']
            comment_data['content'] = comment_data['content']
            comment_data['created_at'] = comment_data['created_at']
            comment_data['likes_count'] = likes_count
            comment_data['is_liked'] = is_liked
            
            result.append(comment_data)
        
        return {
            'discussions': result,
            'total': pagination.total
        }, 200
    
    def post(self):
        # 添加新讨论（顶级评论）
        data = request.get_json()
        
        # 验证数据
        if not data or not data.get('course_id') or not data.get('content'):
            return {'message': '缺少必要参数'}, 400
        
        # 获取当前登录用户
        user = get_current_user()
        
        # 创建新讨论
        new_comment = Comment(
            course_id=data['course_id'],
            user_id=user.id if user else None,
            user_name=user.nickname if user else '匿名用户',
            content=data['content'],
            parent_id=None
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # 返回创建的讨论
        result = comment_schema.dump(new_comment)
        result['author'] = result['user_name']
        result['likes_count'] = 0  # 新创建的讨论默认点赞数为0
        result['is_liked'] = False  # 新创建的讨论默认未点赞
        result['replies'] = []
        result['replies_count'] = 0
        
        return result, 201

class DiscussionResource(Resource):
    def get(self, discussion_id):
        # 获取单个讨论详情
        comment = Comment.query.get_or_404(discussion_id)

        result = comment_schema.dump(comment)
        # 转换格式
        result['author'] = result['user_name']
        result['likes_count'] = result['likes']
        result['is_liked'] = False

        # 获取所有回复
        replies = []
        for reply in comment.replies:
            reply_data = comment_schema.dump(reply)
            reply_data['author'] = reply_data['user_name']
            reply_data['likes_count'] = reply_data['likes']
            reply_data['is_liked'] = False
            replies.append(reply_data)

        result['replies'] = replies
        result['replies_count'] = len(replies)

        return result, 200

    def put(self, discussion_id):
        # 更新讨论内容（仅允许发帖者自己更新）
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        comment = Comment.query.get_or_404(discussion_id)

        # 确保是顶级评论（讨论）
        if comment.parent_id is not None:
            return {'error': 'Not a discussion'}, 400

        # 验证用户权限
        if comment.user_id != user.id:
            return {'error': 'Unauthorized to update this discussion'}, 403

        data = request.get_json()

        # 验证数据
        if 'content' in data:
            if not data['content'] or not data['content'].strip():
                return {'error': 'Discussion content cannot be empty'}, 400
            comment.content = data['content']
            comment.updated_at = datetime.utcnow()

        db.session.commit()

        # 返回格式化的数据
        result = comment_schema.dump(comment)
        result['author'] = result['user_name']

        return result, 200

    def delete(self, discussion_id):
        # 删除讨论（仅允许发帖者自己删除）
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        comment = Comment.query.get_or_404(discussion_id)

        # 确保是顶级评论（讨论）
        if comment.parent_id is not None:
            return {'error': 'Not a discussion'}, 400

        # 验证用户权限
        if comment.user_id != user.id:
            return {'error': 'Unauthorized to delete this discussion'}, 403

        # 删除讨论及其所有回复（级联删除）
        def delete_comment_tree(comment):
            # 删除该评论的所有点赞
            Like.query.filter_by(target_type='comment', target_id=comment.id).delete()
            # 递归删除所有回复
            for reply in comment.replies:
                delete_comment_tree(reply)
            db.session.delete(comment)

        delete_comment_tree(comment)
        db.session.commit()

        return {'message': 'Discussion deleted successfully'}, 200

class DiscussionRepliesResource(Resource):
    def post(self, discussion_id):
        # 添加回复
        data = request.get_json()
        
        if not data or not data.get('content'):
            return {'message': '缺少内容'}, 400
        
        # 验证讨论是否存在
        parent_comment = Comment.query.get_or_404(discussion_id)
        
        # 获取当前登录用户
        user = get_current_user()
        
        # 创建回复
        new_reply = Comment(
            course_id=parent_comment.course_id,
            user_id=user.id if user else None,
            user_name=user.nickname if user else '匿名用户',
            content=data['content'],
            parent_id=discussion_id
        )
        
        db.session.add(new_reply)
        db.session.commit()
        
        # 返回创建的回复
        result = comment_schema.dump(new_reply)
        result['author'] = result['user_name']
        result['likes_count'] = 0  # 新创建的回复默认点赞数为0
        result['is_liked'] = False  # 新创建的回复默认未点赞
        
        return result, 201

class DiscussionLikeResource(Resource):
    def post(self, discussion_id):
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401
        
        # 获取讨论
        comment = Comment.query.get_or_404(discussion_id)
        
        # 检查用户是否已经点赞
        existing_like = Like.query.filter_by(
            user_id=user.id,
            target_type='comment',
            target_id=discussion_id
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
                target_id=discussion_id
            )
            db.session.add(new_like)
            db.session.commit()
            is_liked = True
        
        # 获取点赞数量
        likes_count = Like.query.filter_by(
            target_type='comment',
            target_id=discussion_id
        ).count()
        
        return { 
            'message': '操作成功', 
            'likes_count': likes_count,
            'is_liked': is_liked
        }, 200

class ReplyLikeResource(Resource):
    def post(self, reply_id):
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401
        
        # 获取回复
        reply = Comment.query.get_or_404(reply_id)
        
        # 检查用户是否已经点赞
        existing_like = Like.query.filter_by(
            user_id=user.id,
            target_type='comment',
            target_id=reply_id
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
                target_id=reply_id
            )
            db.session.add(new_like)
            db.session.commit()
            is_liked = True
        
        # 获取点赞数量
        likes_count = Like.query.filter_by(
            target_type='comment',
            target_id=reply_id
        ).count()
        
        return {
            'message': '操作成功', 
            'likes_count': likes_count,
            'is_liked': is_liked
        }, 200

# 注册路由
# 延迟导入api，避免循环导入问题
# 从app.api模块导入api对象
from app.api import api
api.add_resource(DiscussionsResource, '/api/discussions')
api.add_resource(DiscussionResource, '/api/discussions/<int:discussion_id>')
api.add_resource(DiscussionRepliesResource, '/api/discussions/<int:discussion_id>/replies')
api.add_resource(DiscussionLikeResource, '/api/discussions/<int:discussion_id>/like')
api.add_resource(ReplyLikeResource, '/api/replies/<int:reply_id>/like')