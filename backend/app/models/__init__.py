from app import db
from datetime import datetime

# 教师表
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    title = db.Column(db.String(100))  # 职称
    introduction = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    courses = db.relationship('Course', backref='teacher', lazy=True)

# 课程表
class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credit = db.Column(db.Float)
    semester = db.Column(db.String(20))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    evaluations = db.relationship('Evaluation', backref='course', lazy=True)
    comments = db.relationship('Comment', backref='course', lazy=True)

# 评价表
class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.String(100))  # 可以是微信openid或其他用户标识
    score = db.Column(db.Float, nullable=False)  # 评分，1-5分
    workload_score = db.Column(db.Float)  # 工作量评分
    content_score = db.Column(db.Float)  # 内容评分
    teaching_score = db.Column(db.Float)  # 教学评分
    tags = db.Column(db.String(500))  # 标签，用逗号分隔
    comment = db.Column(db.Text)  # 评价内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 认同数
    likes = db.Column(db.Integer, default=0)

# 评论表（社区交流）
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.String(100))
    user_name = db.Column(db.String(100))  # 用户昵称
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # 父评论ID，用于回复
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    likes = db.Column(db.Integer, default=0)