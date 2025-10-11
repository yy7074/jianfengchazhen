from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import AppVersion, VersionStatus
from schemas import AppVersionCreate, AppVersionUpdate, VersionCheckRequest
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VersionService:
    
    @staticmethod
    def create_version(db: Session, version_data: AppVersionCreate) -> AppVersion:
        """创建新版本"""
        try:
            # 检查版本号是否已存在
            existing = db.query(AppVersion).filter(
                AppVersion.platform == version_data.platform,
                AppVersion.version_code == version_data.version_code
            ).first()
            
            if existing:
                raise ValueError(f"版本号 {version_data.version_code} 在平台 {version_data.platform} 上已存在")
            
            version = AppVersion(
                version_name=version_data.version_name,
                version_code=version_data.version_code,
                platform=version_data.platform,
                download_url=version_data.download_url,
                file_size=version_data.file_size,
                file_name=version_data.file_name,
                update_content=version_data.update_content,
                is_force_update=version_data.is_force_update,
                min_support_version=version_data.min_support_version,
                publish_time=version_data.publish_time or datetime.now(),
                status=VersionStatus.ACTIVE
            )
            
            db.add(version)
            db.commit()
            db.refresh(version)
            
            logger.info(f"创建新版本: {version_data.platform} v{version_data.version_name} ({version_data.version_code})")
            return version
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建版本失败: {e}")
            raise
    
    @staticmethod
    def update_version(db: Session, version_id: int, version_data: AppVersionUpdate) -> Optional[AppVersion]:
        """更新版本信息"""
        try:
            version = db.query(AppVersion).filter(AppVersion.id == version_id).first()
            if not version:
                return None
            
            # 更新字段
            for field, value in version_data.dict(exclude_unset=True).items():
                if field == 'status':
                    # 处理状态字段
                    if value == 'active':
                        setattr(version, field, VersionStatus.ACTIVE)
                    elif value == 'inactive':
                        setattr(version, field, VersionStatus.INACTIVE)
                else:
                    setattr(version, field, value)
            
            db.commit()
            db.refresh(version)
            
            logger.info(f"更新版本: ID {version_id}")
            return version
            
        except Exception as e:
            db.rollback()
            logger.error(f"更新版本失败: {e}")
            raise
    
    @staticmethod
    def delete_version(db: Session, version_id: int) -> bool:
        """删除版本"""
        try:
            version = db.query(AppVersion).filter(AppVersion.id == version_id).first()
            if not version:
                return False
            
            db.delete(version)
            db.commit()
            
            logger.info(f"删除版本: ID {version_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"删除版本失败: {e}")
            raise
    
    @staticmethod
    def get_version_by_id(db: Session, version_id: int) -> Optional[AppVersion]:
        """根据ID获取版本信息"""
        return db.query(AppVersion).filter(AppVersion.id == version_id).first()
    
    @staticmethod
    def get_versions_by_platform(db: Session, platform: str, limit: int = 20, offset: int = 0) -> List[AppVersion]:
        """获取指定平台的版本列表"""
        return db.query(AppVersion).filter(
            AppVersion.platform == platform
        ).order_by(desc(AppVersion.version_code)).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_all_versions(db: Session, limit: int = 50, offset: int = 0) -> List[AppVersion]:
        """获取所有版本列表"""
        return db.query(AppVersion).order_by(
            desc(AppVersion.platform), desc(AppVersion.version_code)
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_latest_version(db: Session, platform: str) -> Optional[AppVersion]:
        """获取指定平台的最新版本"""
        return db.query(AppVersion).filter(
            AppVersion.platform == platform,
            AppVersion.status == VersionStatus.ACTIVE
        ).order_by(desc(AppVersion.version_code)).first()
    
    @staticmethod
    def check_version_update(db: Session, platform: str, current_version_code: int) -> dict:
        """检查版本更新"""
        try:
            latest_version = VersionService.get_latest_version(db, platform)
            
            if not latest_version:
                return {
                    "has_update": False,
                    "is_force_update": False,
                    "latest_version": None
                }
            
            has_update = latest_version.version_code > current_version_code
            is_force_update = False
            
            if has_update and latest_version.is_force_update:
                # 检查是否需要强制更新
                if latest_version.min_support_version:
                    is_force_update = current_version_code < latest_version.min_support_version
                else:
                    is_force_update = latest_version.is_force_update == 1
            
            # 转换为Pydantic模型以便序列化
            latest_version_info = None
            if has_update and latest_version:
                latest_version_info = {
                    "id": latest_version.id,
                    "version_name": latest_version.version_name,
                    "version_code": latest_version.version_code,
                    "platform": latest_version.platform,
                    "download_url": latest_version.download_url,
                    "file_size": latest_version.file_size,
                    "file_name": latest_version.file_name,
                    "update_content": latest_version.update_content,
                    "is_force_update": latest_version.is_force_update,
                    "min_support_version": latest_version.min_support_version,
                    "status": latest_version.status.value if latest_version.status else None,
                    "publish_time": latest_version.publish_time.isoformat() if latest_version.publish_time else None,
                    "created_time": latest_version.created_time.isoformat() if latest_version.created_time else None,
                    "updated_time": latest_version.updated_time.isoformat() if latest_version.updated_time else None
                }
            
            return {
                "has_update": has_update,
                "is_force_update": is_force_update,
                "latest_version": latest_version_info
            }
            
        except Exception as e:
            logger.error(f"检查版本更新失败: {e}")
            return {
                "has_update": False,
                "is_force_update": False,
                "latest_version": None
            }
    
    @staticmethod
    def get_version_stats(db: Session) -> dict:
        """获取版本统计信息"""
        try:
            total_versions = db.query(AppVersion).filter(AppVersion.platform == "android").count()
            android_versions = total_versions  # 只有Android版本
            active_versions = db.query(AppVersion).filter(
                AppVersion.platform == "android",
                AppVersion.status == VersionStatus.ACTIVE
            ).count()
            
            latest_android = VersionService.get_latest_version(db, "android")
            
            return {
                "total_versions": total_versions,
                "android_versions": android_versions,
                "active_versions": active_versions,
                "latest_android_version": latest_android.version_name if latest_android else None
            }
            
        except Exception as e:
            logger.error(f"获取版本统计失败: {e}")
            return {
                "total_versions": 0,
                "android_versions": 0,
                "active_versions": 0,
                "latest_android_version": None
            }
