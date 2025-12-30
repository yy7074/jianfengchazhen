#!/usr/bin/env python3
"""
见缝插针游戏后端启动脚本
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pymysql
        print("✅ 核心依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)

def check_database():
    """检查数据库连接"""
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"⚠️ 数据库连接失败: {e}")
        print("请检查数据库配置和服务状态")
        return False

def check_redis():
    """检查Redis连接"""
    try:
        from database import redis_client
        redis_client.ping()
        print("✅ Redis连接正常")
        return True
    except Exception as e:
        print(f"⚠️ Redis连接失败: {e}")
        print("Redis服务可选，但建议启动以获得更好的性能")
        return False

def create_directories():
    """创建必要的目录"""
    dirs = ["uploads", "uploads/videos", "uploads/avatars", "logs"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✅ 目录结构创建完成")

def init_database():
    """初始化数据库"""
    try:
        from database import Base, engine
        from services.config_service import ConfigService
        from database import get_db
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建完成")
        
        # 初始化配置
        db = next(get_db())
        try:
            ConfigService.init_default_configs(db)
            print("✅ 默认配置初始化完成")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False
    
    return True

def start_server():
    """启动服务器"""
    from config import settings

    host = settings.SERVER_HOST
    port = settings.SERVER_PORT

    print(f"\n启动服务器...")
    print(f"地址: http://{host}:{port}")
    if settings.DOCS_URL:
        print(f"API文档: http://{host}:{port}{settings.DOCS_URL}")
    print(f"管理后台: http://{host}:{port}{settings.ADMIN_PREFIX}/")
    print("\n按 Ctrl+C 停止服务器\n")

    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=settings.DEBUG,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")

def main():
    """主函数"""
    print("🎯 见缝插针游戏后端启动检查\n")
    
    # 检查环境
    check_python_version()
    check_dependencies()
    
    # 创建目录
    create_directories()
    
    # 检查服务
    db_ok = check_database()
    redis_ok = check_redis()
    
    if not db_ok:
        print("\n❌ 数据库连接失败，无法启动服务")
        sys.exit(1)
    
    # 初始化数据库
    if not init_database():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ 环境检查完成，准备启动服务器")
    print("="*50)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 