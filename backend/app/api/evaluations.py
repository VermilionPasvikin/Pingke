from flask import request, jsonify
from flask_restful import Resource
from app import db
from app.models import Evaluation, Course
from app.schemas import EvaluationSchema
from sqlalchemy import desc

evaluation_schema = EvaluationSchema()
evaluations_schema = EvaluationSchema(many=True)

class EvaluationsResource(Resource):
    def get(self):
        # 获取评价列表，可以按课程筛选
        course_id = request.args.get('course_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        
        # 构建查询
        query = Evaluation.query
        
        if course_id:
            query = query.filter(Evaluation.course_id == course_id)
        
        # 排序
        if sort_by == 'created_at':
            query = query.order_by(desc(Evaluation.created_at))
        elif sort_by == 'score':
            query = query.order_by(desc(Evaluation.score))
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
        data = request.get_json()
        
        # 处理tags字段：如果是数组，转换为字符串
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = ','.join(data['tags'])
        
        # 移除前端提交但后端不需要的字段
        if 'anonymous' in data:
            del data['anonymous']
        
        # 验证数据
        errors = evaluation_schema.validate(data)
        if errors:
            return {'error': errors}, 400
        
        # 检查课程是否存在
        course = Course.query.get(data['course_id'])
        if not course:
            return {'error': 'Course not found'}, 404
        
        # 检查用户是否已经评价过这门课程（可选，取决于业务需求）
        user_id = data.get('user_id')
        if user_id:
            existing_evaluation = Evaluation.query.filter_by(
                course_id=data['course_id'],
                user_id=user_id
            ).first()
            if existing_evaluation:
                return {'error': 'You have already evaluated this course'}, 400
        
        # 创建评价
        new_evaluation = Evaluation(
            course_id=data['course_id'],
            user_id=user_id,
            score=data['score'],
            workload_score=data.get('workload_score'),
            content_score=data.get('content_score'),
            teaching_score=data.get('teaching_score'),
            tags=data.get('tags'),
            comment=data.get('comment')
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
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        data = request.get_json()
        
        # 验证用户权限
        if evaluation.user_id and data.get('user_id') != evaluation.user_id:
            return {'error': 'Unauthorized to update this evaluation'}, 403
        
        # 验证数据
        errors = evaluation_schema.validate(data, partial=True)
        if errors:
            return {'error': errors}, 400
        
        # 更新字段
        for key, value in data.items():
            if key != 'user_id':  # 不允许更改user_id
                setattr(evaluation, key, value)
        
        db.session.commit()
        
        result = evaluation_schema.dump(evaluation)
        return result, 200
    
    def delete(self, evaluation_id):
        # 删除评价（仅允许评价者自己删除）
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        data = request.get_json()
        
        # 验证用户权限
        if evaluation.user_id and data.get('user_id') != evaluation.user_id:
            return {'error': 'Unauthorized to delete this evaluation'}, 403
        
        db.session.delete(evaluation)
        db.session.commit()
        
        return {'message': 'Evaluation deleted successfully'}, 200

class EvaluationLikeResource(Resource):
    def post(self, evaluation_id):
        # 给评价点赞
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        evaluation.likes += 1
        db.session.commit()
        
        return {
            'likes': evaluation.likes,
            'likes_count': evaluation.likes,
            'is_liked': True
        }, 200

# 注册路由
# 延迟导入api对象以避免循环导入
from app.api import api
api.add_resource(EvaluationsResource, '/api/evaluations')
api.add_resource(EvaluationResource, '/api/evaluations/<int:evaluation_id>')
api.add_resource(EvaluationLikeResource, '/api/evaluations/<int:evaluation_id>/like')