"""
初始化默认管理员账号
账号: admin
密码: admin123
"""

from database import get_db
from models import Admin, AdminRole
import hashlib
from datetime import datetime

def hash_password(password: str) -> str:
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_default_admin():
    """初始化默认管理员账号"""
    db = next(get_db())
    
    try:
        # 检查是否已存在admin账号
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        
        if existing_admin:
            print("⚠️  管理员账号 'admin' 已存在")
            print(f"   用户名: {existing_admin.username}")
            print(f"   角色: {existing_admin.role.value if existing_admin.role else 'admin'}")
            print(f"   状态: {'正常' if existing_admin.status == 1 else '禁用'}")
            print(f"   创建时间: {existing_admin.created_time}")
            
            # 询问是否重置密码
            reset = input("\n是否重置密码为 'admin123'? (y/n): ")
            if reset.lower() == 'y':
                existing_admin.password_hash = hash_password("admin123")
                existing_admin.status = 1  # 确保账号是激活状态
                db.commit()
                print("✅ 密码已重置为: admin123")
            return
        
        # 创建默认管理员账号
        admin = Admin(
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@example.com",
            role=AdminRole.SUPER_ADMIN,
            status=1,
            created_time=datetime.now()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("=" * 60)
        print("✅ 默认管理员账号创建成功！")
        print("=" * 60)
        print(f"   用户名: admin")
        print(f"   密码:   admin123")
        print(f"   角色:   超级管理员")
        print(f"   ID:     {admin.id}")
        print("=" * 60)
        print("\n🔐 请登录后尽快修改密码！")
        print("🌐 登录地址: http://your-domain/admin/login")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建管理员账号失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_default_admin()

