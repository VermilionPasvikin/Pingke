import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import db, User, Teacher, Course, Evaluation, Comment, Like
from app import create_app

# 创建应用实例
app = create_app()

# 在应用上下文中导入数据
with app.app_context():
    # 创建用户数据
    users = [
        User(openid='test_openid_001', nickname='小明', avatar_url='https://example.com/avatar1.jpg'),
        User(openid='test_openid_002', nickname='小红', avatar_url='https://example.com/avatar2.jpg'),
        User(openid='test_openid_003', nickname='小李', avatar_url='https://example.com/avatar3.jpg'),
        User(openid='test_openid_004', nickname='小王', avatar_url='https://example.com/avatar4.jpg'),
        User(openid='test_openid_005', nickname='小张', avatar_url='https://example.com/avatar5.jpg'),
        User(openid='test_openid_006', nickname='小刘', avatar_url='https://example.com/avatar6.jpg'),
        User(openid='test_openid_007', nickname='小陈', avatar_url='https://example.com/avatar7.jpg'),
        User(openid='test_openid_008', nickname='小赵', avatar_url='https://example.com/avatar8.jpg'),
    ]

    # 批量添加并提交用户数据
    db.session.add_all(users)
    db.session.commit()

    # 创建教师数据（使用指定的学院名称）
    teachers = [
        Teacher(name='张三', department='计算机与人工智能学院', title='教授',
                introduction='专注于数据结构与算法教学，有丰富的教学经验'),
        Teacher(name='李四', department='数学与统计学院', title='副教授',
                introduction='数学基础课程专家，教学方法灵活'),
        Teacher(name='王五', department='法学院', title='讲师',
                introduction='年轻有为的教师，善于互动教学'),
        Teacher(name='赵六', department='经济学院', title='教授',
                introduction='经济学理论研究专家'),
        Teacher(name='钱七', department='外国语学院', title='副教授',
                introduction='英语教学经验丰富'),
        Teacher(name='孙八', department='商学院', title='教授',
                introduction='工商管理领域资深教授'),
    ]

    # 批量添加并提交教师数据
    db.session.add_all(teachers)
    db.session.commit()

    # 创建课程数据（使用指定的学期格式）
    courses = [
        Course(course_code='CS101', name='数据结构与算法', description='介绍数据结构基本概念和常用算法，包括线性表、树、图等',
               credit=3, semester='2024春', teacher_id=1),
        Course(course_code='CS202', name='操作系统原理', description='学习操作系统的基本原理、进程管理、内存管理等核心内容',
               credit=4, semester='2023秋', teacher_id=1),
        Course(course_code='MTH303', name='线性代数', description='线性代数基础理论及其应用',
               credit=3, semester='2023春', teacher_id=2),
        Course(course_code='LAW404', name='法律基础', description='法律基础知识与法律思维培养',
               credit=2, semester='2023秋', teacher_id=3),
        Course(course_code='ECON505', name='微观经济学', description='微观经济学基本理论与分析方法',
               credit=4, semester='2022秋', teacher_id=4),
        Course(course_code='ENG606', name='高级英语', description='提升英语综合运用能力',
               credit=3, semester='2022春', teacher_id=5),
        Course(course_code='BUS707', name='市场营销', description='市场营销理论与实践',
               credit=3, semester='2024春', teacher_id=6),
    ]

    # 批量添加并提交课程数据
    db.session.add_all(courses)
    db.session.commit()

    # 创建评价数据（使用正确的字段，包括 is_anonymous 和 user_name）
    evaluations = [
        Evaluation(course_id=1, user_id=1, score=5, workload_score=4,
                  content_score=5, teaching_score=5, tags='干货,易懂,收获大',
                  comment='老师讲得非常好，内容充实，容易理解。课程设计合理，循序渐进。',
                  is_anonymous=False, user_name='小明'),
        Evaluation(course_id=1, user_id=2, score=4, workload_score=5,
                  content_score=4, teaching_score=4, tags='作业多,实用,有挑战',
                  comment='课程内容实用，但作业较多。不过做完作业后确实学到很多东西。',
                  is_anonymous=False, user_name='小红'),
        Evaluation(course_id=2, user_id=3, score=4.5, workload_score=3,
                  content_score=4, teaching_score=5, tags='深入,清晰,系统',
                  comment='讲解深入，思路清晰。老师对知识点的把握很到位。',
                  is_anonymous=False, user_name='小李'),
        Evaluation(course_id=3, user_id=4, score=5, workload_score=4,
                  content_score=5, teaching_score=5, tags='有趣,易上手,实用',
                  comment='非常有趣的课程，老师讲解生动，举例恰当。',
                  is_anonymous=False, user_name='小王'),
        Evaluation(course_id=4, user_id=5, score=3.5, workload_score=5,
                  content_score=3, teaching_score=4, tags='抽象,难,需要时间',
                  comment='内容较抽象，需要花时间理解。建议提前预习。',
                  is_anonymous=True, user_name='匿名用户'),
        Evaluation(course_id=5, user_id=6, score=4.5, workload_score=4,
                  content_score=5, teaching_score=4, tags='理论性强,有深度',
                  comment='经济学理论讲解透彻，案例分析很有启发性。',
                  is_anonymous=False, user_name='小刘'),
        Evaluation(course_id=6, user_id=7, score=4, workload_score=3,
                  content_score=4, teaching_score=5, tags='互动多,氛围好',
                  comment='课堂氛围很好，老师鼓励大家开口说英语。',
                  is_anonymous=False, user_name='小陈'),
        Evaluation(course_id=7, user_id=8, score=4.5, workload_score=4,
                  content_score=4, teaching_score=5, tags='实践性强,案例丰富',
                  comment='课程结合了很多实际案例，非常贴近实战。',
                  is_anonymous=False, user_name='小赵'),
    ]

    # 批量添加并提交评价数据
    db.session.add_all(evaluations)
    db.session.commit()

    # 创建评论数据（使用正确的 user_id 整数类型）
    comments = [
        Comment(course_id=1, user_id=1, user_name='小明',
               content='请问这门课期末考试难吗？'),
        Comment(course_id=1, user_id=2, user_name='小红',
               content='不难，只要平时认真听课就能过。老师会划重点的。', parent_id=1),
        Comment(course_id=2, user_id=3, user_name='小李',
               content='这门课有实验吗？实验难度怎么样？'),
        Comment(course_id=3, user_id=4, user_name='小王',
               content='老师推荐的教材很好用，建议大家都买一本。'),
        Comment(course_id=4, user_id=5, user_name='小张',
               content='求课程笔记分享，谢谢各位大佬！'),
        Comment(course_id=1, user_id=6, user_name='小刘',
               content='这门课作业量适中，每周都有练习题。'),
        Comment(course_id=5, user_id=7, user_name='小陈',
               content='经济学的数学要求高吗？'),
        Comment(course_id=6, user_id=8, user_name='小赵',
               content='英语课需要做presentation吗？'),
    ]

    # 批量添加并提交评论数据
    db.session.add_all(comments)
    db.session.commit()

    # 创建点赞数据
    likes = [
        Like(user_id=2, target_type='evaluation', target_id=1),
        Like(user_id=3, target_type='evaluation', target_id=1),
        Like(user_id=4, target_type='evaluation', target_id=1),
        Like(user_id=1, target_type='comment', target_id=2),
        Like(user_id=3, target_type='comment', target_id=4),
        Like(user_id=5, target_type='evaluation', target_id=3),
    ]

    # 批量添加并提交点赞数据
    db.session.add_all(likes)
    db.session.commit()

    print("测试数据导入成功！")
    print(f"导入用户数量: {len(users)}")
    print(f"导入教师数量: {len(teachers)}")
    print(f"导入课程数量: {len(courses)}")
    print(f"导入评价数量: {len(evaluations)}")
    print(f"导入评论数量: {len(comments)}")
    print(f"导入点赞数量: {len(likes)}")