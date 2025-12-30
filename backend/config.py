from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/game_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "123456"
    DATABASE_NAME: str = "game_db"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件上传配置
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: str = "50MB"
    
    # 管理员默认账号
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # 应用配置
    APP_NAME: str = "见缝插针游戏"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 3000

    # 管理后台路径前缀（用于安全隐藏后台入口）
    ADMIN_PREFIX: str = "/vfjsadrhbadmin"

    # API文档路径（设为空字符串则禁用）
    DOCS_URL: str = "/vfjsadrhbdocs"       # Swagger文档
    REDOC_URL: str = "/vfjsadrhbredoc"     # ReDoc文档
    OPENAPI_URL: str = "/vfjsadrhbopenapi" # OpenAPI JSON
    
    class Config:
        env_file = ".env"

# 创建全局设置实例
settings = Settings() 