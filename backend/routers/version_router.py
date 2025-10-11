from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from schemas import *
from services.version_service import VersionService
from models import *
import os
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 简单的管理员认证（生产环境应使用更安全的方式）
def verify_admin():
    # 这里应该实现真正的管理员认证
    # 暂时返回True，实际项目中需要JWT或Session认证
    return True

# ==================== 版本管理相关API ====================

@router.get("/admin/versions", response_class=HTMLResponse)
async def version_management_page(request: Request):
    """版本管理页面"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    return templates.TemplateResponse("admin/version_management.html", {"request": request})

@router.get("/api/versions")
async def get_versions_list(platform: str = None, db: Session = Depends(get_db)):
    """获取版本列表"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    try:
        if platform:
            versions = VersionService.get_versions_by_platform(db, platform)
        else:
            versions = VersionService.get_all_versions(db)
        
        versions_data = []
        for version in versions:
            version_data = {
                "id": version.id,
                "version_name": version.version_name,
                "version_code": version.version_code,
                "platform": version.platform,
                "download_url": version.download_url,
                "file_size": version.file_size,
                "file_name": version.file_name,
                "update_content": version.update_content,
                "is_force_update": version.is_force_update,
                "min_support_version": version.min_support_version,
                "status": version.status.value if hasattr(version.status, 'value') else str(version.status),
                "publish_time": version.publish_time.isoformat() if version.publish_time else None,
                "created_time": version.created_time.isoformat(),
                "updated_time": version.updated_time.isoformat()
            }
            versions_data.append(version_data)
        
        return BaseResponse(
            message="获取成功",
            data=versions_data
        )
        
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"获取版本列表失败: {str(e)}"
        )

@router.post("/api/versions")
async def create_version(version_data: AppVersionCreate, db: Session = Depends(get_db)):
    """创建新版本"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    try:
        version = VersionService.create_version(db, version_data)
        
        return BaseResponse(
            message="版本创建成功",
            data={
                "id": version.id,
                "version_name": version.version_name,
                "version_code": version.version_code,
                "platform": version.platform
            }
        )
        
    except ValueError as e:
        return BaseResponse(
            code=400,
            message=str(e)
        )
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"创建版本失败: {str(e)}"
        )

@router.get("/api/versions/{version_id}")
async def get_version_by_id(version_id: int, db: Session = Depends(get_db)):
    """获取单个版本详情"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    try:
        version = VersionService.get_version_by_id(db, version_id)
        if not version:
            return BaseResponse(
                code=404,
                message="版本不存在"
            )
        
        version_data = {
            "id": version.id,
            "version_name": version.version_name,
            "version_code": version.version_code,
            "platform": version.platform,
            "download_url": version.download_url,
            "file_size": version.file_size,
            "file_name": version.file_name,
            "update_content": version.update_content,
            "is_force_update": version.is_force_update,
            "min_support_version": version.min_support_version,
            "status": version.status.value if hasattr(version.status, 'value') else str(version.status),
            "publish_time": version.publish_time.isoformat() if version.publish_time else None,
            "created_time": version.created_time.isoformat() if version.created_time else None,
            "updated_time": version.updated_time.isoformat() if version.updated_time else None
        }
        
        return BaseResponse(
            message="获取版本详情成功",
            data=version_data
        )
        
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"获取版本详情失败: {str(e)}"
        )

@router.put("/api/versions/{version_id}")
async def update_version(version_id: int, version_data: AppVersionUpdate, db: Session = Depends(get_db)):
    """更新版本信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    try:
        version = VersionService.update_version(db, version_id, version_data)
        if not version:
            return BaseResponse(
                code=404,
                message="版本不存在"
            )
        
        return BaseResponse(
            message="版本更新成功",
            data={
                "id": version.id,
                "version_name": version.version_name,
                "status": version.status.value if hasattr(version.status, 'value') else str(version.status)
            }
        )
        
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"更新版本失败: {str(e)}"
        )

@router.delete("/api/versions/{version_id}")
async def delete_version(version_id: int, db: Session = Depends(get_db)):
    """删除版本"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    try:
        success = VersionService.delete_version(db, version_id)
        if not success:
            return BaseResponse(
                code=404,
                message="版本不存在"
            )
        
        return BaseResponse(
            message="版本删除成功"
        )
        
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"删除版本失败: {str(e)}"
        )

@router.get("/api/version-stats")
async def get_version_stats(db: Session = Depends(get_db)):
    """获取版本统计信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    stats = VersionService.get_version_stats(db)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    )

@router.post("/api/upload-apk")
async def upload_apk(file: UploadFile = File(...)):
    """上传APK文件"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    try:
        # 检查文件类型
        if not file.filename.endswith('.apk'):
            return BaseResponse(
                code=400,
                message="只支持APK文件"
            )
        
        # 创建上传目录
        upload_dir = "uploads/apk"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件名（时间戳 + 原文件名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, file_name)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 获取文件大小
        file_size = len(content)
        
        # 生成下载URL
        download_url = f"/uploads/apk/{file_name}"
        
        return BaseResponse(
            message="文件上传成功",
            data={
                "file_name": file_name,
                "file_size": file_size,
                "download_url": download_url,
                "original_name": file.filename
            }
        )
        
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"文件上传失败: {str(e)}"
        )

# ==================== 客户端版本检查API ====================

@router.post("/api/check-update")
async def check_version_update(request: VersionCheckRequest, db: Session = Depends(get_db)):
    """检查版本更新"""
    try:
        result = VersionService.check_version_update(db, request.platform, request.current_version_code)
        
        return BaseResponse(
            message="检查完成",
            data=result
        )
        
    except Exception as e:
        return BaseResponse(
            code=500,
            message=f"检查版本更新失败: {str(e)}"
        )
