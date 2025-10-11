from sqlalchemy.orm import Session
from models import WithdrawRequest, User, TransactionType, WithdrawStatus
from schemas import WithdrawRequest as WithdrawRequestSchema
from services.user_service import UserService
from services.config_service import ConfigService
from datetime import datetime, date
from typing import Dict, Optional
from sqlalchemy import func
from decimal import Decimal

class WithdrawService:
    
    @staticmethod
    def submit_withdraw_request(db: Session, user_id: int, withdraw_data: WithdrawRequestSchema) -> Dict:
        """提交提现申请"""
        # 验证用户存在
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        # 获取系统配置
        min_amount = float(ConfigService.get_min_withdraw_amount(db))
        max_amount = float(ConfigService.get_max_withdraw_amount(db))
        coin_rate = float(ConfigService.get_coin_to_rmb_rate(db))
        min_coins = float(ConfigService.get_withdrawal_min_coins(db))
        fee_rate = float(ConfigService.get_withdrawal_fee_rate(db))
        
        # 验证提现金额
        if withdraw_data.amount < min_amount:
            return {"success": False, "message": f"提现金额不能少于{min_amount}元"}
        
        if withdraw_data.amount > max_amount:
            return {"success": False, "message": f"提现金额不能超过{max_amount}元"}
        
        # 计算需要消耗的金币（包含手续费）
        withdraw_amount = float(withdraw_data.amount)
        base_coins = withdraw_amount * coin_rate  # 基础金币需求
        fee_coins = (base_coins * fee_rate / 100.0) if fee_rate > 0 else 0.0
        coins_needed = base_coins + fee_coins
        
        # 验证用户金币是否达到最小提现要求
        if float(user.coins) < min_coins:
            return {
                "success": False, 
                "message": f"金币余额不足，最少需要{min_coins}金币才能提现，当前余额{user.coins}金币"
            }
        
        # 验证用户金币余额
        if float(user.coins) < coins_needed:
            fee_message = f"（含手续费{fee_coins:.2f}金币）" if fee_rate > 0 else ""
            return {
                "success": False, 
                "message": f"金币余额不足，需要{coins_needed:.2f}金币{fee_message}，当前余额{user.coins}金币"
            }
        
        # 检查每日提现次数限制
        daily_limit = int(ConfigService.get_daily_withdraw_limit(db))
        today = date.today()
        today_withdraws = db.query(func.count(WithdrawRequest.id)).filter(
            WithdrawRequest.user_id == user_id,
            func.date(WithdrawRequest.request_time) == today
        ).scalar() or 0
        
        if today_withdraws >= daily_limit:
            if daily_limit == 1:
                return {"success": False, "message": "您今天已提现过，请明天再来"}
            else:
                return {"success": False, "message": f"您今天已达到提现次数上限({daily_limit}次)，请明天再来"}
        
        # 检查是否有未处理的提现申请
        pending_request = db.query(WithdrawRequest).filter(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == WithdrawStatus.PENDING
        ).first()
        
        if pending_request:
            return {"success": False, "message": "您有未处理的提现申请，请等待审核完成"}
        
        # 扣除金币
        success = UserService.deduct_coins(
            db, user_id, coins_needed,
            TransactionType.WITHDRAW,
            f"提现申请 - {withdraw_data.amount}元"
        )
        
        if not success:
            return {"success": False, "message": "金币扣除失败"}
        
        # 创建提现申请
        withdraw_request = WithdrawRequest(
            user_id=user_id,
            amount=Decimal(str(withdraw_data.amount)),
            coins_used=Decimal(str(coins_needed)),
            alipay_account=withdraw_data.alipay_account,
            real_name=withdraw_data.real_name,
            status=WithdrawStatus.PENDING
        )
        
        db.add(withdraw_request)
        db.commit()
        db.refresh(withdraw_request)
        
        # 构建返回信息
        fee_message = f"，手续费{fee_coins:.2f}金币" if fee_rate > 0 else ""
        
        return {
            "success": True,
            "message": f"提现申请提交成功，请等待审核。消耗金币{coins_needed:.2f}{fee_message}",
            "data": {
                "request_id": withdraw_request.id,
                "amount": float(withdraw_request.amount),
                "coins_used": float(withdraw_request.coins_used),
                "fee_coins": float(fee_coins),
                "fee_rate": float(fee_rate),
                "status": withdraw_request.status.value
            }
        }
    
    @staticmethod
    def approve_withdraw(db: Session, withdraw_id: int, admin_note: str = None) -> Dict:
        """批准提现申请"""
        withdraw_request = db.query(WithdrawRequest).filter(
            WithdrawRequest.id == withdraw_id
        ).first()
        
        if not withdraw_request:
            return {"success": False, "message": "提现申请不存在"}
        
        if withdraw_request.status != WithdrawStatus.PENDING:
            return {"success": False, "message": "该申请已处理"}
        
        # 更新申请状态
        withdraw_request.status = WithdrawStatus.APPROVED
        withdraw_request.admin_note = admin_note
        withdraw_request.process_time = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "提现申请已批准",
            "data": {
                "request_id": withdraw_request.id,
                "amount": float(withdraw_request.amount),
                "status": withdraw_request.status.value
            }
        }
    
    @staticmethod
    def reject_withdraw(db: Session, withdraw_id: int, admin_note: str) -> Dict:
        """拒绝提现申请"""
        withdraw_request = db.query(WithdrawRequest).filter(
            WithdrawRequest.id == withdraw_id
        ).first()
        
        if not withdraw_request:
            return {"success": False, "message": "提现申请不存在"}
        
        if withdraw_request.status != WithdrawStatus.PENDING:
            return {"success": False, "message": "该申请已处理"}
        
        # 退还金币给用户
        UserService.add_coins(
            db, withdraw_request.user_id, float(withdraw_request.coins_used),
            TransactionType.ADMIN_ADJUST,
            f"提现申请被拒绝，退还金币 - 申请ID: {withdraw_id}",
            withdraw_id
        )
        
        # 更新申请状态
        withdraw_request.status = WithdrawStatus.REJECTED
        withdraw_request.admin_note = admin_note
        withdraw_request.process_time = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "提现申请已拒绝，金币已退还",
            "data": {
                "request_id": withdraw_request.id,
                "coins_returned": float(withdraw_request.coins_used),
                "status": withdraw_request.status.value
            }
        }
    
    @staticmethod
    def complete_withdraw(db: Session, withdraw_id: int, admin_note: str = None) -> Dict:
        """完成提现（标记为已支付）"""
        withdraw_request = db.query(WithdrawRequest).filter(
            WithdrawRequest.id == withdraw_id
        ).first()
        
        if not withdraw_request:
            return {"success": False, "message": "提现申请不存在"}
        
        if withdraw_request.status != WithdrawStatus.APPROVED:
            return {"success": False, "message": "该申请未批准或已处理"}
        
        # 更新申请状态
        withdraw_request.status = WithdrawStatus.COMPLETED
        if admin_note:
            withdraw_request.admin_note = admin_note
        withdraw_request.process_time = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "提现已完成",
            "data": {
                "request_id": withdraw_request.id,
                "amount": float(withdraw_request.amount),
                "status": withdraw_request.status.value
            }
        }
    
    @staticmethod
    def get_withdraw_request(db: Session, withdraw_id: int) -> Optional[WithdrawRequest]:
        """获取提现申请详情"""
        return db.query(WithdrawRequest).filter(WithdrawRequest.id == withdraw_id).first()
    
    @staticmethod
    def get_user_withdraw_stats(db: Session, user_id: int) -> Dict:
        """获取用户提现统计"""
        from sqlalchemy import func
        
        # 总提现次数和金额
        total_requests = db.query(func.count(WithdrawRequest.id)).filter(
            WithdrawRequest.user_id == user_id
        ).scalar() or 0
        
        total_amount = db.query(func.sum(WithdrawRequest.amount)).filter(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == WithdrawStatus.COMPLETED
        ).scalar() or 0
        
        # 各状态统计
        pending_count = db.query(func.count(WithdrawRequest.id)).filter(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == WithdrawStatus.PENDING
        ).scalar() or 0
        
        approved_count = db.query(func.count(WithdrawRequest.id)).filter(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == WithdrawStatus.APPROVED
        ).scalar() or 0
        
        completed_count = db.query(func.count(WithdrawRequest.id)).filter(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == WithdrawStatus.COMPLETED
        ).scalar() or 0
        
        rejected_count = db.query(func.count(WithdrawRequest.id)).filter(
            WithdrawRequest.user_id == user_id,
            WithdrawRequest.status == WithdrawStatus.REJECTED
        ).scalar() or 0
        
        # 最近一次提现
        latest_request = db.query(WithdrawRequest).filter(
            WithdrawRequest.user_id == user_id
        ).order_by(WithdrawRequest.request_time.desc()).first()
        
        return {
            "total_requests": total_requests,
            "total_amount": float(total_amount),
            "status_counts": {
                "pending": pending_count,
                "approved": approved_count,
                "completed": completed_count,
                "rejected": rejected_count
            },
            "latest_request": {
                "id": latest_request.id,
                "amount": float(latest_request.amount),
                "status": latest_request.status.value,
                "request_time": latest_request.request_time
            } if latest_request else None,
            "can_withdraw": pending_count == 0  # 没有待处理申请时才能提现
        } 