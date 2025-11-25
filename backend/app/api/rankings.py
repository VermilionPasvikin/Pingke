from flask import request
from flask_restful import Resource
from app import db
from app.models import Course, Teacher, Evaluation
from app.schemas import RankingSchema
from datetime import datetime, timedelta

ranking_schema = RankingSchema()
rankings_schema = RankingSchema(many=True)

class CourseRankingResource(Resource):
    def get(self):
        # 获取课程排行榜
        semester = request.args.get('semester')
        limit = int(request.args.get('limit', 10))
        time_range = request.args.get('time_range')  # 'week', 'month', 'year', 'all'
        
        # 构建课程查询
        course_query = Course.query
        if semester:
            course_query = course_query.filter(Course.semester == semester)
        
        all_courses = course_query.all()
        
        # 计算评分并排序
        course_scores = []
        for course in all_courses:
            # 根据时间范围筛选评价
            evaluations = course.evaluations
            if time_range:
                now = datetime.utcnow()
                if time_range == 'week':
                    start_time = now - timedelta(days=7)
                elif time_range == 'month':
                    start_time = now - timedelta(days=30)
                elif time_range == 'year':
                    start_time = now - timedelta(days=365)
                else:
                    start_time = datetime.min
                evaluations = [e for e in evaluations if e.created_at >= start_time]
            
            # 计算平均评分
            if evaluations:
                avg_score = sum(e.score for e in evaluations) / len(evaluations)
                course_scores.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'course_code': course.course_code,
                    'teacher_name': course.teacher.name if course.teacher else '未知',
                    'avg_score': round(avg_score, 1),
                    'evaluation_count': len(evaluations)
                })
        
        # 按评分降序排序
        course_scores.sort(key=lambda x: x['avg_score'], reverse=True)
        
        # 添加排名
        for i, course in enumerate(course_scores[:limit]):
            course['rank'] = i + 1
        
        return {'rankings': course_scores[:limit]}, 200

class TeacherRankingResource(Resource):
    def get(self):
        # 获取教师排行榜
        department = request.args.get('department')
        limit = int(request.args.get('limit', 10))
        time_range = request.args.get('time_range')
        
        # 构建教师查询
        teacher_query = Teacher.query
        if department:
            teacher_query = teacher_query.filter(Teacher.department == department)
        
        all_teachers = teacher_query.all()
        
        # 计算教师平均评分
        teacher_scores = []
        for teacher in all_teachers:
            all_evaluations = []
            
            # 收集教师所有课程的评价
            for course in teacher.courses:
                evaluations = course.evaluations
                if time_range:
                    now = datetime.utcnow()
                    if time_range == 'week':
                        start_time = now - timedelta(days=7)
                    elif time_range == 'month':
                        start_time = now - timedelta(days=30)
                    elif time_range == 'year':
                        start_time = now - timedelta(days=365)
                    else:
                        start_time = datetime.min
                    evaluations = [e for e in evaluations if e.created_at >= start_time]
                all_evaluations.extend(evaluations)
            
            if all_evaluations:
                avg_score = sum(e.score for e in all_evaluations) / len(all_evaluations)
                teacher_scores.append({
                    'teacher_id': teacher.id,
                    'teacher_name': teacher.name,
                    'department': teacher.department,
                    'title': teacher.title,
                    'avg_score': round(avg_score, 1),
                    'evaluation_count': len(all_evaluations),
                    'course_count': len([c for c in teacher.courses if c.evaluations])
                })
        
        # 按评分降序排序
        teacher_scores.sort(key=lambda x: x['avg_score'], reverse=True)
        
        # 添加排名
        for i, teacher in enumerate(teacher_scores[:limit]):
            teacher['rank'] = i + 1
        
        return {'rankings': teacher_scores[:limit]}, 200

class TagRankingResource(Resource):
    def get(self):
        # 获取热门标签排行榜
        limit = int(request.args.get('limit', 20))
        
        # 收集所有评价的标签
        all_tags = []
        evaluations = Evaluation.query.all()
        
        for eval in evaluations:
            if eval.tags:
                tags = [tag.strip() for tag in eval.tags.split(',')]
                all_tags.extend(tags)
        
        # 统计标签频率
        tag_counts = {}
        for tag in all_tags:
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 排序并返回
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        result = []
        for i, (tag, count) in enumerate(sorted_tags):
            result.append({
                'tag': tag,
                'count': count,
                'rank': i + 1
            })
        
        return {'rankings': result}, 200

class DepartmentRankingResource(Resource):
    def get(self):
        # 获取各学院/系的课程平均评分排行榜
        limit = int(request.args.get('limit', 10))
        
        # 按学院分组计算平均评分
        departments = db.session.query(
            Teacher.department,
            db.func.count(Course.id).label('course_count'),
            db.func.count(Evaluation.id).label('evaluation_count')
        ).join(
            Course, Teacher.id == Course.teacher_id
        ).outerjoin(
            Evaluation, Course.id == Evaluation.course_id
        ).group_by(
            Teacher.department
        ).all()
        
        # 计算每个学院的平均评分
        dept_scores = []
        for dept in departments:
            if dept.evaluation_count > 0:
                # 获取该学院所有课程的评价并计算平均分
                avg_score_query = db.session.query(
                    db.func.avg(Evaluation.score)
                ).join(
                    Course, Evaluation.course_id == Course.id
                ).join(
                    Teacher, Course.teacher_id == Teacher.id
                ).filter(
                    Teacher.department == dept.department
                ).scalar()
                
                dept_scores.append({
                    'department': dept.department,
                    'avg_score': round(avg_score_query, 1),
                    'course_count': dept.course_count,
                    'evaluation_count': dept.evaluation_count
                })
        
        # 按平均分排序
        dept_scores.sort(key=lambda x: x['avg_score'], reverse=True)
        
        # 添加排名
        for i, dept in enumerate(dept_scores[:limit]):
            dept['rank'] = i + 1
        
        return {'rankings': dept_scores[:limit]}, 200

# 注册路由
# 延迟导入api对象以避免循环导入
from app.api import api
api.add_resource(CourseRankingResource, '/api/rankings/courses')
api.add_resource(TeacherRankingResource, '/api/rankings/teachers')
api.add_resource(TagRankingResource, '/api/rankings/tags')
api.add_resource(DepartmentRankingResource, '/api/rankings/departments')