from flask import request
from flask_restful import Resource
from app import db
from app.models import Teacher, Course
from app.schemas import TeacherSchema, CourseSchema
from sqlalchemy import desc

teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)
course_schema = CourseSchema()

class TeachersResource(Resource):
    def get(self):
        # 获取教师列表
        teachers = Teacher.query.all()
        result = teachers_schema.dump(teachers)
        return result, 200
    
    def post(self):
        # 添加新教师
        data = request.get_json()
        
        # 验证数据
        errors = teacher_schema.validate(data)
        if errors:
            return {'error': errors}, 400
        
        # 创建教师
        new_teacher = Teacher(
            name=data['name'],
            department=data.get('department'),
            title=data.get('title'),
            introduction=data.get('introduction')
        )
        
        db.session.add(new_teacher)
        db.session.commit()
        
        result = teacher_schema.dump(new_teacher)
        return result, 201

class TeacherResource(Resource):
    def get(self, teacher_id):
        # 获取单个教师信息
        teacher = Teacher.query.get_or_404(teacher_id)
        result = teacher_schema.dump(teacher)
        return result, 200
    
    def put(self, teacher_id):
        # 更新教师信息
        teacher = Teacher.query.get_or_404(teacher_id)
        data = request.get_json()
        
        # 验证数据
        errors = teacher_schema.validate(data, partial=True)
        if errors:
            return {'error': errors}, 400
        
        # 更新字段
        for key, value in data.items():
            setattr(teacher, key, value)
        
        db.session.commit()
        
        result = teacher_schema.dump(teacher)
        return result, 200
    
    def delete(self, teacher_id):
        # 删除教师
        teacher = Teacher.query.get_or_404(teacher_id)
        
        # 检查是否有关联的课程
        if teacher.courses:
            return {'error': 'Cannot delete teacher with associated courses'}, 400
        
        db.session.delete(teacher)
        db.session.commit()
        
        return {'message': 'Teacher deleted successfully'}, 200

class TeacherCoursesResource(Resource):
    def get(self, teacher_id):
        # 获取教师的所有课程
        teacher = Teacher.query.get_or_404(teacher_id)
        courses = Course.query.filter_by(teacher_id=teacher_id).all()
        
        # 计算每个课程的平均评分
        result = []
        for course in courses:
            course_data = course_schema.dump(course)
            # 计算平均评分
            if course.evaluations:
                avg_score = sum(e.score for e in course.evaluations) / len(course.evaluations)
                course_data['avg_score'] = round(avg_score, 1)
                course_data['evaluation_count'] = len(course.evaluations)
            else:
                course_data['avg_score'] = 0
                course_data['evaluation_count'] = 0
            result.append(course_data)
        
        return result, 200

# 注册路由
# 延迟导入api对象以避免循环导入
from app.api import api
api.add_resource(TeachersResource, '/api/teachers')
api.add_resource(TeacherResource, '/api/teachers/<int:teacher_id>')
api.add_resource(TeacherCoursesResource, '/api/teachers/<int:teacher_id>/courses')