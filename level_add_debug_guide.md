# 等级添加功能调试指南

## 如何查看详细错误信息

### 1. 打开浏览器开发者工具
- **Chrome/Edge**: 按 `F12` 或 `Ctrl+Shift+I` (Mac: `Cmd+Option+I`)
- **Firefox**: 按 `F12` 或 `Ctrl+Shift+K`

### 2. 查看 Console 标签页
点击添加等级并保存时，控制台会显示：
```javascript
发送数据: {level: 1, level_name: "...", ...}
请求URL: /admin/api/levels
请求方法: POST
响应状态: 200 或 400 或 500
响应数据: {...}
```

### 3. 查看 Network 标签页
- 找到对 `/admin/api/levels` 的 POST 请求
- 查看 **Request** 部分的数据
- 查看 **Response** 部分的返回信息

## 常见问题排查

### 问题1: 响应状态 401
**错误信息**: "需要管理员权限"
**原因**: 管理员认证失败
**解决**: 当前代码中已设置 `verify_admin()` 返回 True，不应该出现此问题

### 问题2: 响应状态 400
**可能原因**:
1. **等级已存在**: "该等级已存在"
2. **数据验证失败**: 检查以下字段
   - `level`: 必须是1-100之间的整数
   - `level_name`: 必填，最大50字符
   - `ad_coin_multiplier`: 0.1-10之间的数字
   - `game_coin_multiplier`: 0.1-10之间的数字
   - `min_experience`: 必须>=0的整数
   - `max_experience`: 可选，必须>=0的整数
   - `is_active`: 0或1

### 问题3: 响应状态 404
**错误信息**: "Not Found"
**原因**: API路径不正确
**检查**: 
- URL应该是 `/admin/api/levels`
- 检查后端日志确认请求到达

### 问题4: 响应状态 500
**错误信息**: 服务器内部错误
**原因**: 后端代码执行异常
**解决**: 查看后端日志获取详细错误堆栈

## 测试数据示例

```javascript
{
  "level": 8,
  "level_name": "钻石段位",
  "ad_coin_multiplier": 2.0,
  "game_coin_multiplier": 2.5,
  "min_experience": 5000,
  "max_experience": 10000,
  "description": "高级玩家",
  "is_active": 1
}
```

## 后端API规范

### POST /admin/api/levels

**请求体**:
```json
{
  "level": 1-100的整数,
  "level_name": "等级名称(必填)",
  "ad_coin_multiplier": 0.1-10之间的数字,
  "game_coin_multiplier": 0.1-10之间的数字,
  "min_experience": >=0的整数,
  "max_experience": >=0的整数或null,
  "description": "描述(可选)",
  "is_active": 0或1
}
```

**成功响应**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 新建的等级ID,
    ...其他字段
  }
}
```

**失败响应**:
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

## 下一步操作

1. 尝试添加等级
2. 复制控制台中的所有日志信息
3. 提供给开发人员进行进一步调试

## 验证步骤

### 手动API测试
使用curl命令测试：

```bash
curl -X POST https://8089.dachaonet.com/admin/api/levels \
  -H "Content-Type: application/json" \
  -d '{
    "level": 8,
    "level_name": "测试等级",
    "ad_coin_multiplier": 1.5,
    "game_coin_multiplier": 1.5,
    "min_experience": 1000,
    "max_experience": 2000,
    "description": "测试",
    "is_active": 1
  }'
```

或使用Postman/Insomnia等API测试工具。

