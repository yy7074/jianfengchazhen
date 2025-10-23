# 管理员修改密码功能说明

## 📋 功能概述

在后台管理系统中添加了修改管理员密码的功能，管理员可以自助修改密码，无需技术人员介入。

## ✨ 新增内容

### 1. 后端API接口

**路径**：`POST /admin/api/change-password`

**功能**：修改当前登录管理员的密码

**请求参数**：
```json
{
  "old_password": "旧密码",
  "new_password": "新密码",
  "confirm_password": "确认新密码"
}
```

**验证规则**：
- ✅ 所有字段必填
- ✅ 旧密码必须正确
- ✅ 新密码长度至少6位
- ✅ 两次输入的新密码必须一致

**返回结果**：
```json
{
  "success": true,
  "message": "密码修改成功，请重新登录"
}
```

### 2. 前端界面

**位置**：管理后台首页 → 快速操作区域

**按钮**：🔐 修改密码

**功能**：
1. 点击按钮弹出修改密码对话框
2. 填写原密码、新密码、确认新密码
3. 提交后自动验证
4. 修改成功后自动跳转到登录页

## 🎯 使用步骤

### 步骤1：登录管理后台
访问：`http://your-server:port/admin/`
使用当前管理员账号密码登录

### 步骤2：打开修改密码对话框
在首页找到**快速操作**区域，点击 **🔐 修改密码** 按钮

### 步骤3：填写密码信息
- **原密码**：输入当前使用的密码
- **新密码**：输入新的密码（至少6位）
- **确认新密码**：再次输入新密码

### 步骤4：提交修改
点击 **确认修改** 按钮

### 步骤5：重新登录
修改成功后会自动跳转到登录页，使用新密码登录即可

## ⚠️ 注意事项

### 安全提示
1. **请妥善保管新密码**，丢失后需要数据库管理员重置
2. **建议定期修改密码**，提高账号安全性
3. **密码至少6位**，建议使用字母+数字+符号组合
4. **不要使用简单密码**，如123456、admin等

### 常见问题

**Q1：忘记原密码怎么办？**
A1：需要通过数据库直接修改，或联系技术人员重置。

**Q2：修改密码后其他设备会被登出吗？**
A2：会的，所有已登录的设备都需要重新登录。

**Q3：密码有复杂度要求吗？**
A3：当前只要求至少6位，建议使用复杂密码增强安全性。

**Q4：可以修改回原来的密码吗？**
A4：可以，系统不限制使用旧密码。

## 🔧 文件修改清单

### 后端文件
- `backend/routers/admin_router.py`
  - 新增 `change_admin_password()` 函数
  - 处理密码修改请求
  - 验证旧密码并更新新密码

### 前端文件
- `backend/templates/admin/dashboard.html`
  - 新增"修改密码"按钮
  - 新增修改密码模态框HTML
  - 新增 `showChangePasswordModal()` 函数
  - 新增 `hideChangePasswordModal()` 函数
  - 新增 `changePassword()` 函数

## 🚀 部署步骤

### 1. 更新代码
```bash
git pull origin main
```

### 2. 重启后端服务
```bash
cd backend
sudo systemctl restart game-backend
```

### 3. 验证功能
1. 登录管理后台
2. 点击"修改密码"按钮
3. 测试修改密码功能

## 🛡️ 安全性

### 密码加密
- 使用 SHA-256 哈希算法
- 密码不以明文存储
- 即使数据库泄露也无法还原原始密码

### 会话管理
- 修改密码后自动清除当前会话
- 强制用户重新登录
- 防止密码修改后的安全隐患

### 权限控制
- 只有已登录的管理员才能修改密码
- 必须验证原密码才能修改
- 防止未授权的密码修改

## 📝 代码示例

### 后端API调用示例
```python
# 修改密码API
@router.post("/api/change-password")
async def change_admin_password(request: Request, db: Session = Depends(get_db)):
    # 验证登录状态
    admin_id = verify_admin(request)
    if not admin_id:
        return JSONResponse(
            content={"success": False, "message": "未登录或登录已过期"},
            status_code=401
        )
    
    # 获取请求参数
    body = await request.json()
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")
    
    # 验证旧密码
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    old_password_hash = hash_password(old_password)
    if admin.password_hash != old_password_hash:
        return JSONResponse(
            content={"success": False, "message": "原密码错误"},
            status_code=400
        )
    
    # 更新密码
    new_password_hash = hash_password(new_password)
    admin.password_hash = new_password_hash
    db.commit()
    
    return JSONResponse(
        content={"success": True, "message": "密码修改成功"}
    )
```

### 前端调用示例
```javascript
async function changePassword(event) {
    event.preventDefault();
    
    const response = await fetch('/admin/api/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword,
            confirm_password: confirmPassword
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        alert('密码修改成功，请重新登录');
        window.location.href = '/admin/login';
    } else {
        alert(data.message);
    }
}
```

## 🎨 界面截图说明

1. **快速操作区域**
   - 显示"🔐 修改密码"按钮
   - 与其他快速操作按钮并列

2. **修改密码对话框**
   - 输入原密码
   - 输入新密码（至少6位）
   - 确认新密码
   - 显示注意事项
   - 取消/确认修改按钮

3. **成功提示**
   - 显示"密码修改成功，请重新登录"
   - 自动跳转到登录页

## 📞 技术支持

如有问题，请联系技术支持或查看日志：
```bash
# 查看后端日志
sudo journalctl -u game-backend -f
```

---

**修改时间**：2025-10-21  
**版本**：v1.0  
**状态**：✅ 已完成

