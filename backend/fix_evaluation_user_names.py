"""
数据清理脚本：修复已有评价的user_name字段

选项1：删除user_id为NULL的无效评价
选项2：修复已有user_id但缺少user_name的评价
选项3：两者都执行
"""
from app import create_app, db
from app.models import Evaluation, User

def fix_evaluations():
    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("开始修复评价数据")
        print("=" * 50)

        # 选项1：删除user_id为NULL的评价
        null_evaluations = Evaluation.query.filter_by(user_id=None).all()
        if null_evaluations:
            print(f"\n找到 {len(null_evaluations)} 条user_id为NULL的评价")
            confirm = input("是否删除这些无效评价? (y/n): ")
            if confirm.lower() == 'y':
                for eval in null_evaluations:
                    db.session.delete(eval)
                db.session.commit()
                print(f"✓ 已删除 {len(null_evaluations)} 条无效评价")
            else:
                print("⚠ 跳过删除NULL评价")
        else:
            print("\n✓ 没有user_id为NULL的评价")

        # 选项2：修复缺少user_name的评价
        print("\n正在查找缺少user_name的评价...")
        evaluations_to_fix = Evaluation.query.filter(
            (Evaluation.user_name.is_(None)) | (Evaluation.user_name == '')
        ).all()

        if evaluations_to_fix:
            print(f"找到 {len(evaluations_to_fix)} 条需要修复的评价")
            fixed_count = 0
            anonymous_count = 0

            for eval in evaluations_to_fix:
                if eval.user_id:
                    user = User.query.get(eval.user_id)
                    if user:
                        eval.user_name = user.nickname
                        eval.is_anonymous = False
                        fixed_count += 1
                    else:
                        # 用户已删除，标记为匿名
                        eval.user_name = '匿名用户'
                        eval.is_anonymous = True
                        anonymous_count += 1
                else:
                    # user_id为NULL，标记为匿名
                    eval.user_name = '匿名用户'
                    eval.is_anonymous = True
                    anonymous_count += 1

            db.session.commit()
            print(f"✓ 修复完成:")
            print(f"  - {fixed_count} 条设置为实名")
            print(f"  - {anonymous_count} 条设置为匿名")
        else:
            print("✓ 所有评价的user_name字段都已正确设置")

        # 统计信息
        print("\n" + "=" * 50)
        print("修复后的统计信息:")
        total = Evaluation.query.count()
        anonymous = Evaluation.query.filter_by(is_anonymous=True).count()
        named = total - anonymous
        print(f"  总评价数: {total}")
        print(f"  实名评价: {named}")
        print(f"  匿名评价: {anonymous}")
        print("=" * 50)
        print("✓ 数据修复完成！")

if __name__ == '__main__':
    fix_evaluations()
