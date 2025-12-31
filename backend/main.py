from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import uvicorn
import logging

from config import settings
from database import get_db, Base, engine
from services.config_service import ConfigService
from services.ad_service import AdService
from services.ip_service import IPService

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="见缝插针小游戏后端API",
    docs_url=settings.DOCS_URL or None,
    redoc_url=settings.REDOC_URL or None,
    openapi_url=settings.OPENAPI_URL or None
)

# 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# IP黑名单拦截中间件
class IPBlockMiddleware(BaseHTTPMiddleware):
    """拦截被封禁的IP地址"""

    # 不需要检查IP的路径（管理员相关接口除外，以便管理员可以解封IP）
    WHITELIST_PATHS = ["/health", "/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next):
        # 白名单路径直接放行
        path = request.url.path
        if any(path.startswith(p) for p in self.WHITELIST_PATHS):
            return await call_next(request)

        # 管理后台路径放行（允许管理员操作）
        if path.startswith(settings.ADMIN_PREFIX):
            return await call_next(request)

        # 获取客户端IP
        client_ip = request.client.host if request.client else None

        # 检查X-Forwarded-For头（代理情况）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # 检查IP是否被封禁
        if client_ip:
            try:
                db = next(get_db())
                try:
                    if IPService.is_ip_blocked(db, client_ip):
                        block_info = IPService.get_ip_block_info(db, client_ip)
                        logging.warning(f"🚫 已拦截被封禁的IP: {client_ip}")
                        return JSONResponse(
                            status_code=403,
                            content={
                                "code": 403,
                                "message": "您的IP已被封禁，如有疑问请联系管理员",
                                "data": {
                                    "ip": client_ip,
                                    "reason": block_info.get("reason") if block_info else "异常访问",
                                    "expire_time": block_info.get("expire_time") if block_info else None
                                }
                            }
                        )
                finally:
                    db.close()
            except Exception as e:
                logging.error(f"IP检查失败: {e}")
                # 检查失败时不阻止请求，避免影响正常服务

        return await call_next(request)


# 注册IP拦截中间件
app.add_middleware(IPBlockMiddleware)

# 全局异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logging.error(f"请求验证失败: {request.url} - {error_details}")
    
    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "message": "请求参数验证失败",
            "data": {
                "errors": error_details,
                "request_body": str(exc.body) if hasattr(exc, 'body') else None
            }
        }
    )

# 静态文件服务（用于广告视频等）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 导入路由
from routers import user_router, ad_router, game_router, admin_router, version_router

# 注册路由
app.include_router(user_router.router, prefix="/api/user", tags=["用户"])
app.include_router(ad_router.router, prefix="/api/ad", tags=["广告"])
app.include_router(game_router.router, prefix="/api/game", tags=["游戏"])
app.include_router(admin_router.router, prefix=settings.ADMIN_PREFIX, tags=["管理"])
app.include_router(version_router.router, tags=["版本管理"])

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 创建上传目录
    import os
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("uploads/videos", exist_ok=True)
    os.makedirs("uploads/avatars", exist_ok=True)
    os.makedirs("uploads/apk", exist_ok=True)
    
    # 初始化默认配置
    db = next(get_db())
    try:
        ConfigService.init_default_configs(db)
        print("✅ 默认配置初始化完成")
        
        # 初始化默认广告
        AdService.init_default_ads(db)
        print("✅ 默认广告初始化完成")
        
        # 初始化默认等级配置
        from services.level_service import LevelService
        LevelService.init_default_levels(db)
        print("✅ 默认等级配置初始化完成")
        
        # 初始化默认管理员账号
        from models import Admin, AdminRole
        import hashlib
        from datetime import datetime
        
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not existing_admin:
            admin = Admin(
                username="admin",
                password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
                email="admin@example.com",
                role=AdminRole.SUPER_ADMIN,
                status=1,
                created_time=datetime.now()
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员账号创建完成 (用户名: admin, 密码: admin123)")
        else:
            print("ℹ️  管理员账号已存在")
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径返回简单的欢迎页面"""
    admin_url = f"{settings.ADMIN_PREFIX}/"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>见缝插针游戏后端</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            .api-link {{ display: inline-block; margin: 10px; padding: 10px 20px;
                       background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            .status {{ background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>见缝插针游戏后端服务</h1>
            <p><span class="status">服务运行中</span> 后端服务正在运行中...</p>
            <div>
                <a href="/docs" class="api-link">API文档</a>
            </div>
            <h3>主要功能</h3>
            <ul>
                <li>用户注册登录系统</li>
                <li>自定义激励视频广告</li>
                <li>金币奖励系统</li>
                <li>提现管理</li>
                <li>游戏数据统计</li>
                <li>管理后台</li>
            </ul>
            <h3>访问地址</h3>
            <ul>
                <li><strong>API文档</strong>: <a href="/docs">/docs</a></li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": settings.APP_VERSION}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 