from flask import request
from flask_restful import Resource
from app import db
from app.models import Comment, Course
from app.schemas import CommentSchema
from sqlalchemy import desc

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

class DiscussionsResource(Resource):
    def get(self):
        # 获取讨论列表（等同于评论列表的顶级评论）
        course_id = request.args.get('course_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
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
            # 获取前3条回复
            comment_data['replies'] = []
            for reply in comment.replies[:3]:
                reply_data = comment_schema.dump(reply)
                # 为回复设置author字段，与主评论处理方式一致
                reply_data['author'] = reply_data['user_name']
                reply_data['likes_count'] = reply_data['likes']
                reply_data['is_liked'] = False
                comment_data['replies'].append(reply_data)
            # 回复总数
            comment_data['replies_count'] = len(comment.replies)
            # 重命名字段以匹配前端
            comment_data['id'] = comment_data['id']
            comment_data['author'] = comment_data['user_name']
            comment_data['content'] = comment_data['content']
            comment_data['created_at'] = comment_data['created_at']
            comment_data['likes_count'] = comment_data['likes']
            comment_data['is_liked'] = False  # 可以根据实际登录状态判断
            
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
        
        # 创建新讨论
        new_comment = Comment(
            course_id=data['course_id'],
            user_name='匿名用户',  # 可以根据实际登录状态获取用户名
            content=data['content'],
            parent_id=None
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # 返回创建的讨论
        result = comment_schema.dump(new_comment)
        result['author'] = result['user_name']
        result['likes_count'] = result['likes']
        result['is_liked'] = False
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

class DiscussionRepliesResource(Resource):
    def post(self, discussion_id):
        # 添加回复
        data = request.get_json()
        
        if not data or not data.get('content'):
            return {'message': '缺少内容'}, 400
        
        # 验证讨论是否存在
        parent_comment = Comment.query.get_or_404(discussion_id)
        
        # 创建回复
        new_reply = Comment(
            course_id=parent_comment.course_id,
            user_name='匿名用户',  # 可以根据实际登录状态获取用户名
            content=data['content'],
            parent_id=discussion_id
        )
        
        db.session.add(new_reply)
        db.session.commit()
        
        # 返回创建的回复
        result = comment_schema.dump(new_reply)
        result['author'] = result['user_name']
        result['likes_count'] = result['likes']
        result['is_liked'] = False
        
        return result, 201

class DiscussionLikeResource(Resource):
    def post(self, discussion_id):
        # 点赞/取消点赞讨论
        comment = Comment.query.get_or_404(discussion_id)
        
        # 获取用户标识（在实际应用中，这应该从认证信息中获取）
        # 这里为了演示，我们假设每个点赞请求都会切换点赞状态
        # 在生产环境中，应该有一个用户点赞记录的表来跟踪谁点赞了什么
        
        # 切换点赞状态（模拟实现，实际应该检查用户是否已点赞）
        # 由于我们没有用户点赞记录，这里简单地增加点赞数
        # 在实际应用中，应该根据用户是否已点赞来决定增加或减少
        comment.likes += 1
        db.session.commit()
        
        # 返回更新后的点赞数和点赞状态
        # 由于没有实际的用户点赞记录，这里总是返回is_liked=true
        return { 
            'message': '操作成功', 
            'likes': comment.likes,
            'likes_count': comment.likes,
            'is_liked': True
        }, 200

class ReplyLikeResource(Resource):
    def post(self, reply_id):
        # 点赞/取消点赞回复
        reply = Comment.query.get_or_404(reply_id)
        
        # 模拟点赞操作
        reply.likes += 1
        db.session.commit()
        
        return {
            'message': '操作成功', 
            'likes': reply.likes,
            'likes_count': reply.likes,
            'is_liked': True
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