# 速率限制中间件集成指南

## 📌 快速集成（2分钟）

### 方法1: 修改 main.py（推荐）

在 `main.py` 文件中进行以下修改：

#### 步骤1: 添加导入（第16行后）
```python
from services.ip_service import IPService
from middleware.rate_limiter import RateLimitMiddleware  # 新增这行
```

#### 步骤2: 注册中间件（第38行后，CORS中间件之后）
```python
# 现有的 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 【新增】速率限制中间件
app.add_middleware(RateLimitMiddleware)

# 现有的 IP 拦截中间件
app.add_middleware(IPBlockMiddleware)
```

---

### 方法2: 自定义限制规则

如果需要自定义限流规则，使用以下代码：

```python
from middleware.rate_limiter import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    limits={
        'register': {'requests': 3, 'window': 3600},    # 更严格：每小时3次
        'login': {'requests': 10, 'window': 60},        # 登录：每分钟10次
        'ad_watch': {'requests': 50, 'window': 3600},   # 广告：每小时50次
        'default': {'requests': 30, 'window': 60}       # 默认：每分钟30次
    }
)
```

---

## 📝 完整的 main.py 修改示例

```python
# ... 前面的导入保持不变 ...

from config import settings
from database import get_db, Base, engine
from services.config_service import ConfigService
from services.ad_service import AdService
from services.ip_service import IPService
from middleware.rate_limiter import RateLimitMiddleware  # ← 新增

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 【新增】速率限制中间件 ← 在这里添加
app.add_middleware(RateLimitMiddleware)

# IP黑名单拦截中间件（保持不变）
class IPBlockMiddleware(BaseHTTPMiddleware):
    # ... 代码保持不变 ...
    pass

# 注册IP拦截中间件
app.add_middleware(IPBlockMiddleware)

# ... 后面的代码保持不变 ...
```

---

## 🧪 测试速率限制

### 测试注册接口限流
```bash
# 连续发送6次注册请求（超过5次限制）
for i in {1..6}; do
  curl -X POST http://localhost:3000/api/user/register \
    -H "Content-Type: application/json" \
    -d "{\"device_id\": \"test_device_$i\", \"nickname\": \"test$i\"}"
  echo ""
  sleep 1
done

# 预期结果：前5次成功，第6次返回429错误
```

### 测试登录接口限流
```bash
# 1分钟内发送11次登录请求（超过10次限制）
for i in {1..11}; do
  curl -X POST http://localhost:3000/api/user/login \
    -H "Content-Type: application/json" \
    -d "{\"device_id\": \"test_device\"}"
  echo ""
done

# 预期结果：前10次正常，第11次返回429错误
```

---

## 🔍 验证部署

### 步骤1: 修改代码
按照上述方法修改 `main.py`

### 步骤2: 重启服务
```bash
# 停止现有服务
pkill -f "python.*main.py"

# 启动服务
nohup python3 main.py > server.log 2>&1 &
```

### 步骤3: 检查日志
```bash
tail -f server.log

# 应该看到类似输出：
# INFO: Application startup complete.
# 没有关于速率限制的错误信息
```

### 步骤4: 测试限流
```bash
# 快速连续请求
for i in {1..10}; do curl http://localhost:3000/health; done

# 如果看到 429 响应，说明限流生效
```

---

## ⚙️ 限流规则说明

| 接口类型 | 路径匹配 | 限制 | 时间窗口 | 说明 |
|---------|---------|------|---------|------|
| 注册 | `/register`, `/user/register` | 5次 | 1小时 | 防止批量注册 |
| 登录 | `/login` | 10次 | 1分钟 | 防止暴力破解 |
| 广告 | `/ad/*` | 100次 | 1小时 | 防止刷广告 |
| 默认 | 其他所有接口 | 60次 | 1分钟 | 通用防护 |

---

## 🚨 429错误响应格式

当触发速率限制时，返回：

```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后再试",
  "data": {
    "ip": "1.2.3.4",
    "retry_after": "60秒"
  }
}
```

---

## 💡 自定义限流规则

### 为特定IP放行（白名单）

在 `middleware/rate_limiter.py` 的 `check_rate_limit` 方法中添加：

```python
def check_rate_limit(self, request: Request, client_ip: str) -> bool:
    # 白名单IP直接放行
    WHITELIST_IPS = ["127.0.0.1", "localhost", "你的信任IP"]
    if client_ip in WHITELIST_IPS:
        return True

    # ... 其余代码保持不变 ...
```

### 为管理后台接口放行

中间件已自动处理，管理后台接口不受限流影响。

---

## ⚡ 性能影响

- **Redis查询**: 每个请求增加 ~0.1ms
- **内存占用**: 每个IP约占用 100 bytes
- **CPU开销**: 可忽略不计

✅ **优雅降级**: Redis故障时自动跳过限流，不影响正常服务

---

## 🔧 故障排查

### 问题1: 速率限制不生效

**检查Redis连接**:
```bash
redis-cli ping
# 应返回: PONG
```

**检查Redis键**:
```bash
redis-cli --scan --pattern "rate_limit:*"
# 应看到类似: rate_limit:1.2.3.4:_api_user_register
```

### 问题2: 正常用户被误拦截

**临时解决**: 清除Redis中的限流记录
```bash
redis-cli DEL rate_limit:用户IP:路径
```

**永久解决**: 调整限流阈值（增加 `requests` 值）

### 问题3: 导入错误

```bash
ModuleNotFoundError: No module named 'middleware'
```

**解决**: 确保 `middleware/__init__.py` 文件存在
```bash
touch middleware/__init__.py
```

---

## ✅ 集成检查清单

部署后确认：

- [ ] `main.py` 已添加导入语句
- [ ] 中间件已注册（在CORS之后，IPBlock之前）
- [ ] 服务已重启
- [ ] Redis连接正常
- [ ] 测试限流功能正常
- [ ] 日志无错误
- [ ] 正常用户不受影响

---

## 📚 相关文档

- `middleware/rate_limiter.py` - 中间件源码
- `EMERGENCY_TOOLS_README.md` - 工具包总览
- `SERVER_EMERGENCY_GUIDE.md` - 紧急操作指南
- `QUICK_FIX.md` - 快速修复指南

---

**最后更新**: 2026-01-02
