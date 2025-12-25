from marshmallow import Schema, fields, validate
from datetime import datetime

# 教师Schema
class TeacherSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=100))
    department = fields.Str(validate=validate.Length(max=100))
    title = fields.Str(validate=validate.Length(max=100))
    introduction = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# 课程Schema
class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    course_code = fields.Str(required=True, validate=validate.Length(max=50))
    name = fields.Str(required=True, validate=validate.Length(max=200))
    description = fields.Str()
    credit = fields.Float()
    semester = fields.Str(validate=validate.Length(max=20))
    teacher_id = fields.Int()
    teacher = fields.Nested(TeacherSchema, only=['id', 'name', 'title', 'department'], dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # 额外的计算字段
    avg_score = fields.Float(dump_only=True)
    evaluation_count = fields.Int(dump_only=True)

# 评价Schema
class EvaluationSchema(Schema):
    id = fields.Int(dump_only=True)
    course_id = fields.Int(required=True)
    user_id = fields.Str()
    score = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    workload_score = fields.Float(validate=validate.Range(min=1, max=5))
    content_score = fields.Float(validate=validate.Range(min=1, max=5))
    teaching_score = fields.Float(validate=validate.Range(min=1, max=5))
    tags = fields.Str()
    comment = fields.Str()
    is_anonymous = fields.Bool()
    user_name = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    likes = fields.Method("get_likes_count")
    
    def get_likes_count(self, obj):
        # 计算点赞数量
        from app.models import Like
        return Like.query.filter_by(target_type='evaluation', target_id=obj.id).count()
    
    # 嵌套字段
    course = fields.Nested(CourseSchema, only=['id', 'name', 'course_code'], dump_only=True)

# 评论Schema
class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    course_id = fields.Int(required=True)
    user_id = fields.Str()
    user_name = fields.Str(required=True, validate=validate.Length(max=100))
    content = fields.Str(required=True)
    parent_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    likes = fields.Method("get_likes_count")
    
    def get_likes_count(self, obj):
        # 计算点赞数量
        from app.models import Like
        return Like.query.filter_by(target_type='comment', target_id=obj.id).count()
    
    # 嵌套字段
    replies = fields.Nested('self', many=True, exclude=['parent_id', 'course_id'], dump_only=True)
    course = fields.Nested(CourseSchema, only=['id', 'name'], dump_only=True)

# 排行榜Schema
class RankingSchema(Schema):
    course_id = fields.Int()
    course_name = fields.Str()
    course_code = fields.Str()
    teacher_name = fields.Str()
    avg_score = fields.Float()
    evaluation_count = fields.Int()
    rank = fields.Int()