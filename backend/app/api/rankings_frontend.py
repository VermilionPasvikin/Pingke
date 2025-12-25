from flask import request
from flask_restful import Resource
from app import db
from app.models import Course, Teacher, Evaluation
from app.schemas import RankingSchema
from datetime import datetime, timedelta

ranking_schema = RankingSchema()
rankings_schema = RankingSchema(many=True)

class RankingsResource(Resource):
    def get(self):
        # 获取排行榜数据，根据type参数决定返回哪种排行榜
        ranking_type = request.args.get('type', 'courses')  # courses, teachers, tags, departments
        semester = request.args.get('semester')
        department = request.args.get('department')
        limit = int(request.args.get('limit', 10))
        
        if ranking_type == 'courses':
            # 课程排行榜
            course_query = Course.query
            if semester:
                course_query = course_query.filter(Course.semester == semester)
            if department:
                course_query = course_query.filter(Course.department == department)
            
            all_courses = course_query.all()
            course_scores = []
            
            for course in all_courses:
                if course.evaluations:
                    avg_score = sum(e.score for e in course.evaluations) / len(course.evaluations)
                    course_scores.append({
                        'id': course.id,
                        'name': course.name,
                        'code': course.course_code,
                        'teacher': course.teacher.name if course.teacher else '未知',
                        'score': round(avg_score, 1),
                        'count': len(course.evaluations)
                    })
            
            # 按评分排序
            course_scores.sort(key=lambda x: x['score'], reverse=True)
            return {'list': course_scores[:limit]}, 200
            
        elif ranking_type == 'teachers':
            # 教师排行榜
            teacher_query = Teacher.query
            if department:
                teacher_query = teacher_query.filter(Teacher.department == department)
            
            all_teachers = teacher_query.all()
            teacher_scores = []
            
            for teacher in all_teachers:
                # 收集所有课程的评价
                all_evaluations = []
                for course in teacher.courses:
                    all_evaluations.extend(course.evaluations)
                
                if all_evaluations:
                    avg_score = sum(e.score for e in all_evaluations) / len(all_evaluations)
                    teacher_scores.append({
                        'id': teacher.id,
                        'name': teacher.name,
                        'department': teacher.department or '未知',
                        'score': round(avg_score, 1),
                        'count': len(all_evaluations)
                    })
            
            teacher_scores.sort(key=lambda x: x['score'], reverse=True)
            return {'list': teacher_scores[:limit]}, 200
            
        elif ranking_type == 'tags':
            # 标签排行榜（简化版）
            # 这里应该从评价中提取标签并统计，但为简化先返回示例数据
            tags = [
                {'name': '给分好', 'count': 156},
                {'name': '教学认真', 'count': 145},
                {'name': '考试简单', 'count': 132},
                {'name': '内容丰富', 'count': 128},
                {'name': '不点名', 'count': 110},
                {'name': '作业少', 'count': 98},
                {'name': '有趣', 'count': 95},
                {'name': '实用', 'count': 87}
            ]
            return {'list': tags[:limit]}, 200
            
        elif ranking_type == 'departments':
            # 学院排行榜
            # 从所有课程中按学院分组
            department_scores = {}
            
            all_courses = Course.query.all()
            
            for course in all_courses:
                dept = course.department or '未知'
                if dept not in department_scores:
                    department_scores[dept] = {'total_score': 0, 'count': 0}
                
                if course.evaluations:
                    avg_score = sum(e.score for e in course.evaluations) / len(course.evaluations)
                    department_scores[dept]['total_score'] += avg_score
                    department_scores[dept]['count'] += 1
            
            # 计算每个学院的平均评分
            result = []
            for dept, data in department_scores.items():
                if data['count'] > 0:
                    result.append({
                        'name': dept,
                        'score': round(data['total_score'] / data['count'], 1),
                        'count': data['count']
                    })
            
            result.sort(key=lambda x: x['score'], reverse=True)
            return {'list': result[:limit]}, 200
            
        else:
            return {'message': '无效的排行榜类型'}, 400

# 注册路由，使用前端期望的路径
# 延迟导入api对象以避免循环导入
from app.api import api
api.add_resource(RankingsResource, '/api/rankings')