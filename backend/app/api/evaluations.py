from flask import request, jsonify
from flask_restful import Resource
from app import db
from app.models import Evaluation, Course, Like, User
from app.schemas import EvaluationSchema
from app.utils.auth import get_current_user
from sqlalchemy import desc
from datetime import datetime

evaluation_schema = EvaluationSchema()
evaluations_schema = EvaluationSchema(many=True)

class EvaluationsResource(Resource):
    def get(self):
        # 获取评价列表，可以按课程筛选
        course_id = request.args.get('course_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        score = request.args.get('score')
        
        # 构建查询
        query = Evaluation.query
        
        if course_id:
            query = query.filter(Evaluation.course_id == course_id)
        
        # 添加评分筛选
        if score:
            query = query.filter(Evaluation.score == int(score))
        
        # 排序
        if sort_by == 'created_at':
            query = query.order_by(desc(Evaluation.created_at))
        elif sort_by == 'score_desc':
            query = query.order_by(desc(Evaluation.score))
        elif sort_by == 'score_asc':
            query = query.order_by(Evaluation.score)
        elif sort_by == 'likes':
            query = query.order_by(desc(Evaluation.likes))
        
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
    
    def post(self):
        # 添加新评价
        # 获取当前登录用户（从JWT token）
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        data = request.get_json()

        # 处理tags字段：如果是数组，转换为字符串
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = ','.join(data['tags'])

        # 提取并移除anonymous字段（不需要验证）
        is_anonymous = data.pop('anonymous', False)

        # 验证数据
        errors = evaluation_schema.validate(data, partial=True)
        if errors:
            return {'error': errors}, 400

        # 检查课程是否存在
        course = Course.query.get(data['course_id'])
        if not course:
            return {'error': 'Course not found'}, 404

        # 检查用户是否已经评价过这门课程
        existing_evaluation = Evaluation.query.filter_by(
            course_id=data['course_id'],
            user_id=user.id
        ).first()
        if existing_evaluation:
            return {'error': 'You have already evaluated this course'}, 400

        # 根据匿名状态设置user_name
        user_name = '匿名用户' if is_anonymous else user.nickname

        # 创建评价
        new_evaluation = Evaluation(
            course_id=data['course_id'],
            user_id=user.id,  # 从JWT token获取
            score=data['score'],
            workload_score=data.get('workload_score'),
            content_score=data.get('content_score'),
            teaching_score=data.get('teaching_score'),
            tags=data.get('tags'),
            comment=data.get('comment'),
            is_anonymous=is_anonymous,
            user_name=user_name
        )

        db.session.add(new_evaluation)
        db.session.commit()

        result = evaluation_schema.dump(new_evaluation)
        return result, 201

class EvaluationResource(Resource):
    def get(self, evaluation_id):
        # 获取单个评价详情
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        result = evaluation_schema.dump(evaluation)
        return result, 200
    
    def put(self, evaluation_id):
        # 更新评价（仅允许评价者自己更新）
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        evaluation = Evaluation.query.get_or_404(evaluation_id)

        # 验证用户权限：使用JWT token中的user_id
        if evaluation.user_id != user.id:
            return {'error': 'Unauthorized to update this evaluation'}, 403

        data = request.get_json()

        # 验证数据
        errors = evaluation_schema.validate(data, partial=True)
        if errors:
            return {'error': errors}, 400

        # 更新字段（不允许更改user_id和course_id）
        allowed_fields = ['score', 'workload_score', 'content_score',
                          'teaching_score', 'tags', 'comment', 'anonymous']
        for key, value in data.items():
            if key in allowed_fields:
                if key == 'anonymous':
                    # 特殊处理anonymous字段
                    evaluation.is_anonymous = value
                    evaluation.user_name = '匿名用户' if value else user.nickname
                elif key == 'tags' and isinstance(value, list):
                    evaluation.tags = ','.join(value)
                else:
                    setattr(evaluation, key, value)

        evaluation.updated_at = datetime.utcnow()
        db.session.commit()

        result = evaluation_schema.dump(evaluation)
        return result, 200
    
    def delete(self, evaluation_id):
        # 删除评价（仅允许评价者自己删除）
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401

        evaluation = Evaluation.query.get_or_404(evaluation_id)

        # 验证用户权限：使用JWT token中的user_id
        if evaluation.user_id != user.id:
            return {'error': 'Unauthorized to delete this evaluation'}, 403

        # 删除相关的点赞记录
        Like.query.filter_by(target_type='evaluation', target_id=evaluation_id).delete()

        db.session.delete(evaluation)
        db.session.commit()

        return {'message': 'Evaluation deleted successfully'}, 200

class EvaluationLikeResource(Resource):
    def post(self, evaluation_id):
        # 获取当前登录用户
        user = get_current_user()
        if not user:
            return {'error': '请先登录'}, 401
        
        # 获取评价
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        
        # 检查用户是否已经点赞
        existing_like = Like.query.filter_by(
            user_id=user.id,
            target_type='evaluation',
            target_id=evaluation_id
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
                target_type='evaluation',
                target_id=evaluation_id
            )
            db.session.add(new_like)
            db.session.commit()
            is_liked = True
        
        # 获取点赞数量
        likes_count = Like.query.filter_by(
            target_type='evaluation',
            target_id=evaluation_id
        ).count()
        
        return { 
            'message': '操作成功',
            'likes_count': likes_count,
            'is_liked': is_liked
        }, 200

# 注册路由
# 延迟导入api对象以避免循环导入
from app.api import api
api.add_resource(EvaluationsResource, '/api/evaluations')
api.add_resource(EvaluationResource, '/api/evaluations/<int:evaluation_id>')
api.add_resource(EvaluationLikeResource, '/api/evaluations/<int:evaluation_id>/like')