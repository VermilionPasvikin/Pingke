import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import db, Teacher, Course, Evaluation, Comment
from app import create_app

# 创建应用实例
app = create_app()

# 在应用上下文中导入数据
with app.app_context():
    # 创建教师数据
    teachers = [
        Teacher(name='张三', department='计算机学院', title='教授'),
        Teacher(name='李四', department='电子工程学院', title='副教授'),
        Teacher(name='王五', department='数学学院', title='讲师'),
        Teacher(name='赵六', department='物理学院', title='教授')
    ]
    
    # 批量添加并提交教师数据
    db.session.add_all(teachers)
    db.session.commit()
    
    # 创建课程数据
    courses = [
        Course(course_code='CS101', name='数据结构', description='介绍数据结构基本概念和算法', 
               credit=3, semester='2024春季', teacher_id=1),
        Course(course_code='CS202', name='操作系统', description='学习操作系统原理和实现', 
               credit=4, semester='2024秋季', teacher_id=1),
        Course(course_code='EE303', name='数字电路', description='数字电路设计与应用', 
               credit=3, semester='2023春季', teacher_id=2),
        Course(course_code='MTH404', name='高等数学', description='高等数学基础', 
               credit=5, semester='2023秋季', teacher_id=3),
        Course(course_code='PHY505', name='量子力学', description='量子力学入门', 
               credit=4, semester='2022春季', teacher_id=4)
    ]
    
    # 批量添加并提交课程数据
    db.session.add_all(courses)
    db.session.commit()
    
    # 创建评价数据
    evaluations = [
        Evaluation(course_id=1, user_id='user1', score=5, workload_score=4, 
                  content_score=5, teaching_score=5, tags='干货,易懂', 
                  comment='老师讲得非常好，内容充实，容易理解'),
        Evaluation(course_id=1, user_id='user2', score=4, workload_score=5, 
                  content_score=4, teaching_score=4, tags='作业多,实用', 
                  comment='课程内容实用，但作业较多'),
        Evaluation(course_id=2, user_id='user3', score=4, workload_score=3, 
                  content_score=4, teaching_score=5, tags='深入,清晰', 
                  comment='讲解深入，思路清晰'),
        Evaluation(course_id=3, user_id='user4', score=5, workload_score=4, 
                  content_score=5, teaching_score=5, tags='有趣,易上手', 
                  comment='非常有趣的课程，老师讲解生动'),
        Evaluation(course_id=4, user_id='user5', score=3, workload_score=5, 
                  content_score=3, teaching_score=4, tags='抽象,难', 
                  comment='内容较抽象，需要花时间理解')
    ]
    
    # 批量添加并提交评价数据
    db.session.add_all(evaluations)
    db.session.commit()
    
    # 创建评论数据
    comments = [
        Comment(course_id=1, user_id='user10', user_name='小明', 
               content='请问这门课期末考试难吗？'),
        Comment(course_id=1, user_id='user11', user_name='小红', 
               content='不难，只要平时认真听课就能过', parent_id=1),
        Comment(course_id=2, user_id='user12', user_name='小李', 
               content='这门课有实验吗？'),
        Comment(course_id=3, user_id='user13', user_name='小王', 
               content='老师推荐的教材很好用'),
        Comment(course_id=4, user_id='user14', user_name='小张', 
               content='求课程笔记分享')
    ]
    
    # 批量添加并提交评论数据
    db.session.add_all(comments)
    db.session.commit()
    
    print("测试数据导入成功！")
    print(f"导入教师数量: {len(teachers)}")
    print(f"导入课程数量: {len(courses)}")
    print(f"导入评价数量: {len(evaluations)}")
    print(f"导入评论数量: {len(comments)}")