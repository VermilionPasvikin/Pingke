from app import db
from datetime import datetime
from sqlalchemy import and_

# 用户表（支持微信登录）
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(100), unique=True, nullable=False, index=True)  # 微信openid
    nickname = db.Column(db.String(100))  # 用户昵称
    avatar_url = db.Column(db.String(500))  # 用户头像URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    comments = db.relationship('Comment', backref='user', lazy=True)
    evaluations = db.relationship('Evaluation', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 评分，1-5分
    workload_score = db.Column(db.Float)  # 工作量评分
    content_score = db.Column(db.Float)  # 内容评分
    teaching_score = db.Column(db.Float)  # 教学评分
    tags = db.Column(db.String(500))  # 标签，用逗号分隔
    comment = db.Column(db.Text)  # 评价内容
    is_anonymous = db.Column(db.Boolean, default=False)  # 是否匿名评价
    user_name = db.Column(db.String(100))  # 用户昵称或"匿名用户"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 点赞关系
    likes = db.relationship('Like', secondary='likes',
                           primaryjoin='Evaluation.id == Like.target_id',
                           secondaryjoin="and_(Like.target_id == Evaluation.id, Like.target_type == 'evaluation')",
                           viewonly=True)

# 点赞表（通用，支持评论和评价的点赞）
class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # 'comment' 或 'evaluation'
    target_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束：每个用户对每个目标只能点赞一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='_user_target_uc'),
    )

# 评论表（社区交流）
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(100))  # 保留用户昵称，用于兼容旧数据
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # 父评论ID，用于回复
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    # 点赞关系
    likes = db.relationship('Like', secondary='likes',
                           primaryjoin='Comment.id == Like.target_id',
                           secondaryjoin="and_(Like.target_id == Comment.id, Like.target_type == 'comment')",
                           viewonly=True)