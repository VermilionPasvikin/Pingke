"""
数据库迁移脚本：为evaluations表添加is_anonymous和user_name字段
"""
from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()

    with app.app_context():
        try:
            # 添加is_anonymous字段
            db.session.execute(text(
                "ALTER TABLE evaluations ADD COLUMN is_anonymous BOOLEAN DEFAULT 0"
            ))
            print("✓ 成功添加is_anonymous字段")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠ is_anonymous字段已存在，跳过")
            else:
                print(f"✗ 添加is_anonymous字段失败: {e}")
                raise

        try:
            # 添加user_name字段
            db.session.execute(text(
                "ALTER TABLE evaluations ADD COLUMN user_name VARCHAR(100)"
            ))
            print("✓ 成功添加user_name字段")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠ user_name字段已存在，跳过")
            else:
                print(f"✗ 添加user_name字段失败: {e}")
                raise

        # 提交事务
        db.session.commit()
        print("\n✓ 数据库迁移成功完成！")
        print("\n提示：请运行数据清理脚本修复已有评价的user_name字段")

if __name__ == '__main__':
    migrate()
