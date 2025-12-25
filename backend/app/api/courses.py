from flask import request, jsonify
from flask_restful import Resource
from app import db
from app.models import Course, Teacher, Evaluation
from app.schemas import CourseSchema
from sqlalchemy import desc, func

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

class CoursesResource(Resource):
    def get(self):
        # 获取课程列表，支持筛选和排序
        semester = request.args.get('semester')
        department = request.args.get('department')
        # 新增支持多个学院筛选的departments参数
        departments = request.args.get('departments')
        keyword = request.args.get('keyword')
        # 支持default排序（等同于created_at）
        sort_by = request.args.get('sort_by', 'default')
        if sort_by == 'default':
            sort_by = 'created_at'
        page = int(request.args.get('page', 1))
        # 兼容page_size参数，适配前端请求
        per_page = int(request.args.get('page_size', request.args.get('per_page', 20)))
        
        # 构建查询
        query = Course.query
        
        # 筛选条件
        if semester:
            query = query.filter(Course.semester == semester)
        
        # 支持单个学院筛选
        if department:
            query = query.join(Teacher).filter(Teacher.department == department)
        
        # 支持多个学院筛选
        elif departments:
            # 将逗号分隔的学院列表转换为数组
            department_list = [dept.strip() for dept in departments.split(',')]
            # 筛选属于任一指定学院的课程
            query = query.join(Teacher).filter(Teacher.department.in_(department_list))
        
        if keyword:
            query = query.filter(
                (Course.name.contains(keyword)) | 
                (Course.course_code.contains(keyword)) |
                (Course.description.contains(keyword)) |
                (Course.teacher.has(Teacher.name.contains(keyword)))
            )
        
        # 排序
        if sort_by in ['score', 'score_desc', 'score_asc']:
            # 按评分排序，需要进行复杂查询
            courses = []
            all_courses = query.all()
            # 计算每个课程的平均评分并排序
            course_scores = []
            for course in all_courses:
                if course.evaluations:
                    avg_score = sum(e.score for e in course.evaluations) / len(course.evaluations)
                    course_scores.append((course, avg_score))
                else:
                    course_scores.append((course, 0))
            
            # 根据排序类型决定升序或降序
            reverse = sort_by != 'score_asc'
            course_scores.sort(key=lambda x: x[1], reverse=reverse)
            courses = [c[0] for c in course_scores]
            
            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            paginated_courses = courses[start:end]
            total = len(courses)
        elif sort_by == 'comments_desc':
            # 按评论数量降序排序
            courses = []
            all_courses = query.all()
            # 计算每个课程的评论数量并排序
            course_comments = []
            for course in all_courses:
                comment_count = len(course.evaluations)
                course_comments.append((course, comment_count))
            
            # 按评论数量降序排序
            course_comments.sort(key=lambda x: x[1], reverse=True)
            courses = [c[0] for c in course_comments]
            
            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            paginated_courses = courses[start:end]
            total = len(courses)
        else:
            # 简单排序
            if sort_by == 'created_at':
                query = query.order_by(desc(Course.created_at))
            elif sort_by == 'name':
                query = query.order_by(Course.name)
            
            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            paginated_courses = pagination.items
            total = pagination.total
        
        # 序列化并添加平均评分
        result = []
        for course in paginated_courses:
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
        
        return {
            'courses': result,
            'total': total,
            'page': page,
            'per_page': per_page
        }, 200
    
    def post(self):
        # 添加新课程
        data = request.get_json()
        
        # 验证数据
        errors = course_schema.validate(data)
        if errors:
            return {'error': errors}, 400
        
        # 检查教师是否存在
        if data.get('teacher_id'):
            teacher = Teacher.query.get(data['teacher_id'])
            if not teacher:
                return {'error': 'Teacher not found'}, 404
        
        # 创建课程
        new_course = Course(
            course_code=data['course_code'],
            name=data['name'],
            description=data.get('description'),
            credit=data.get('credit'),
            semester=data.get('semester'),
            teacher_id=data.get('teacher_id')
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        result = course_schema.dump(new_course)
        return result, 201

class CourseResource(Resource):
    def get(self, course_id):
        # 获取单个课程详情
        course = Course.query.get_or_404(course_id)
        course_data = course_schema.dump(course)
        
        # 计算平均评分和评价数量
        if course.evaluations:
            avg_score = sum(e.score for e in course.evaluations) / len(course.evaluations)
            course_data['avg_score'] = round(avg_score, 1)
            course_data['evaluation_count'] = len(course.evaluations)
            
            # 计算各维度平均评分
            workload_scores = [e.workload_score for e in course.evaluations if e.workload_score]
            content_scores = [e.content_score for e in course.evaluations if e.content_score]
            teaching_scores = [e.teaching_score for e in course.evaluations if e.teaching_score]
            
            if workload_scores:
                course_data['avg_workload_score'] = round(sum(workload_scores) / len(workload_scores), 1)
            if content_scores:
                course_data['avg_content_score'] = round(sum(content_scores) / len(content_scores), 1)
            if teaching_scores:
                course_data['avg_teaching_score'] = round(sum(teaching_scores) / len(teaching_scores), 1)
                
            # 统计标签
            all_tags = []
            for eval in course.evaluations:
                if eval.tags:
                    tags = [tag.strip() for tag in eval.tags.split(',')]
                    all_tags.extend(tags)
            
            # 计算标签频率
            tag_counts = {}
            for tag in all_tags:
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            course_data['popular_tags'] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        else:
            course_data['avg_score'] = 0
            course_data['evaluation_count'] = 0
        
        return course_data, 200


class CoursePopularTagsResource(Resource):
    def get(self, course_id):
        # 获取课程热门标签
        course = Course.query.get_or_404(course_id)
        
        # 统计标签
        all_tags = []
        for eval in course.evaluations:
            if eval.tags:
                tags = [tag.strip() for tag in eval.tags.split(',')]
                all_tags.extend(tags)
        
        # 计算标签频率
        tag_counts = {}
        for tag in all_tags:
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 转换为前端期望的格式
        popular_tags = []
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            popular_tags.append({
                'name': tag,
                'count': count
            })
        
        return {'tags': popular_tags}, 200


class CourseRatingDistributionResource(Resource):
    def get(self, course_id):
        # 获取课程评分分布
        course = Course.query.get_or_404(course_id)
        
        # 初始化评分分布
        distribution = {
            '5': 0,
            '4': 0,
            '3': 0,
            '2': 0,
            '1': 0
        }
        
        # 统计各评分数量
        for eval in course.evaluations:
            score_key = str(int(eval.score))
            if score_key in distribution:
                distribution[score_key] += 1
        
        return {'distribution': distribution}, 200
    
    def put(self, course_id):
        # 更新课程信息
        course = Course.query.get_or_404(course_id)
        data = request.get_json()
        
        # 验证数据
        errors = course_schema.validate(data, partial=True)
        if errors:
            return {'error': errors}, 400
        
        # 检查教师是否存在
        if 'teacher_id' in data and data['teacher_id']:
            teacher = Teacher.query.get(data['teacher_id'])
            if not teacher:
                return {'error': 'Teacher not found'}, 404
        
        # 更新字段
        for key, value in data.items():
            setattr(course, key, value)
        
        db.session.commit()
        
        result = course_schema.dump(course)
        return result, 200
    
    def delete(self, course_id):
        # 删除课程
        course = Course.query.get_or_404(course_id)
        
        # 检查是否有关联的评价或评论
        if course.evaluations or course.comments:
            return {'error': 'Cannot delete course with associated evaluations or comments'}, 400
        
        db.session.delete(course)
        db.session.commit()
        
        return {'message': 'Course deleted successfully'}, 200

# 注册路由
# 延迟导入api对象以避免循环导入
from app.api import api
# 直接注册路由，确保路径正确
api.add_resource(CoursesResource, '/api/courses')
api.add_resource(CourseResource, '/api/courses/<int:course_id>')
api.add_resource(CoursePopularTagsResource, '/api/courses/<int:course_id>/popular_tags')
api.add_resource(CourseRatingDistributionResource, '/api/courses/<int:course_id>/rating_distribution')