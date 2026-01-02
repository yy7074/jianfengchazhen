# 🚨 紧急响应工具包说明

本文档说明所有紧急响应工具的使用方法和部署步骤。

---

## 📦 工具清单

### 1. 诊断工具

#### `emergency_diagnosis.py` - 紧急诊断脚本
**作用**: 分析当前系统状态，识别恶意活动

**使用方法**:
```bash
python3 emergency_diagnosis.py
# 或保存结果
python3 emergency_diagnosis.py > diagnosis_result.txt
```

**检查内容**:
- ✅ 今日注册数量
- ✅ 可疑IP检测（关联多个用户的IP）
- ✅ 异常广告观看行为
- ✅ 数据库规模和连接数
- ✅ 重复设备ID检测

---

#### `check_historical_attacks.py` - 历史攻击分析
**作用**: 分析过去7天的攻击模式

**使用方法**:
```bash
python3 check_historical_attacks.py
# 或保存结果
python3 check_historical_attacks.py > attack_history.txt
```

**输出内容**:
- 📊 每日注册趋势
- 📊 每日广告观看趋势
- 📊 历史最恶意的IP列表

---

### 2. 防护工具

#### `emergency_block_ips.py` - IP封禁工具
**作用**: 快速封禁恶意IP地址

**使用方法**:
```bash
# 1. 交互模式（推荐）- 显示列表并确认
python3 emergency_block_ips.py

# 2. 自动模式 - 无需确认，直接封禁
python3 emergency_block_ips.py --all

# 3. 封禁单个IP
python3 emergency_block_ips.py --ip 1.2.3.4

# 4. 自定义阈值（默认阈值为5个用户）
python3 emergency_block_ips.py --threshold 3
```

**封禁规则**:
- 默认封禁时长: 7天
- 检测阈值: 单IP关联 ≥5 个用户
- 封禁类型: auto（自动）或 manual（手动）

---

#### `middleware/rate_limiter.py` - 速率限制中间件
**作用**: 防止未来的批量攻击

**默认限制规则**:
- 注册接口: 5次/小时
- 登录接口: 10次/分钟
- 广告接口: 100次/小时
- 其他接口: 60次/分钟

**集成方法**:
在 `main.py` 中添加以下代码：

```python
# 在文件顶部导入
from middleware.rate_limiter import RateLimitMiddleware

# 在 app 创建后添加（在 CORS 中间件之后）
app.add_middleware(
    RateLimitMiddleware,
    limits={
        'register': {'requests': 5, 'window': 3600},
        'login': {'requests': 10, 'window': 60},
        'ad_watch': {'requests': 100, 'window': 3600},
        'default': {'requests': 60, 'window': 60}
    }
)
```

**位置参考**（在 main.py 第39行后添加）:
```python
# 现有的 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)

# 添加速率限制中间件（新增）
app.add_middleware(RateLimitMiddleware)

# 现有的 IP 拦截中间件
app.add_middleware(IPBlockMiddleware)
```

---

### 3. 清理工具

#### `cleanup_malicious_data.py` - 恶意数据清理
**作用**: 清除被封禁IP相关的所有恶意数据

**使用方法**:
```bash
# 1. 预览模式（推荐先运行）- 查看将删除什么
python3 cleanup_malicious_data.py --dry-run

# 2. 交互模式 - 显示统计并确认
python3 cleanup_malicious_data.py

# 3. 自动模式 - 无需确认
python3 cleanup_malicious_data.py --auto
```

**清理内容**:
- ❌ 恶意用户账号
- ❌ 广告观看记录
- ❌ 金币交易记录
- ❌ 游戏记录

⚠️ **警告**: 此操作不可逆，建议先运行 `--dry-run` 预览

---

### 4. 代码防护

#### `routers/user_router.py` - 注册接口防护
**已添加的防护措施**:

1. **IP封禁检查**:
   ```python
   if IPService.is_ip_blocked(db, client_ip):
       raise HTTPException(403, "您的IP已被封禁")
   ```

2. **注册频率限制**:
   ```python
   if not check_registration_limit(db, client_ip):
       raise HTTPException(429, "注册过于频繁，请稍后再试")
   ```

3. **频率限制规则**:
   - 每个IP在1小时内最多注册5个账号
   - 通过广告观看记录关联IP和用户

---

## 🚀 完整部署流程

### 步骤1: 登录服务器
```bash
ssh root@8.137.103.175
cd /path/to/backend  # 替换为实际路径
```

### 步骤2: 诊断问题
```bash
python3 emergency_diagnosis.py > diagnosis.txt
cat diagnosis.txt
```

### 步骤3: 封禁恶意IP
```bash
python3 emergency_block_ips.py
# 输入 yes 确认封禁
```

### 步骤4: 更新代码
```bash
# 备份当前代码
cp routers/user_router.py routers/user_router.py.backup

# 拉取最新代码
git stash
git pull origin main
```

### 步骤5: 集成速率限制
编辑 `main.py`，在第39行后添加:
```python
from middleware.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)
```

### 步骤6: 重启服务
```bash
# 停止现有服务
pkill -f "python.*main.py"

# 启动新服务
nohup python3 main.py > server.log 2>&1 &

# 查看日志
tail -f server.log
```

### 步骤7: 验证修复
```bash
# 检查服务运行
ps aux | grep python

# 测试健康检查
curl http://localhost:3000/health

# 测试后台访问
curl http://localhost:3000/admin/
```

### 步骤8: 清理恶意数据（可选）
```bash
# 先预览
python3 cleanup_malicious_data.py --dry-run

# 确认后执行
python3 cleanup_malicious_data.py
```

---

## 📊 监控命令

### 实时监控
```bash
# 监控MySQL连接数
watch -n 5 'mysql -u root -p<密码> -e "SHOW STATUS LIKE \"Threads_connected\";"'

# 监控Redis缓存
watch -n 5 'redis-cli INFO stats | grep keyspace'

# 监控日志
tail -f server.log | grep -E "ERROR|WARNING|封禁|异常"

# 监控当前IP连接
netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n | tail -20
```

---

## 🔧 故障排查

### 后台还是打不开

#### 情况1: 数据库连接耗尽
```bash
# 查看连接
mysql -u root -p -e "SHOW FULL PROCESSLIST;"

# 杀死异常连接
mysql -u root -p -e "KILL <process_id>;"

# 重启MySQL
sudo systemctl restart mysql
```

#### 情况2: 服务器资源耗尽
```bash
# 检查资源
free -h
df -h
top

# 清理日志
find /var/log -type f -name "*.log" -mtime +7 -delete

# 重启服务器（最后手段）
sudo reboot
```

#### 情况3: 攻击持续进行
```bash
# 临时防火墙封禁
iptables -A INPUT -s 1.2.3.4 -j DROP
iptables-save > /etc/iptables/rules.v4

# 查看防火墙规则
iptables -L -n
```

---

## 📁 文件位置

```
backend/
├── emergency_diagnosis.py           # 诊断工具
├── emergency_block_ips.py          # IP封禁工具
├── check_historical_attacks.py     # 历史分析工具
├── cleanup_malicious_data.py       # 数据清理工具
├── middleware/
│   └── rate_limiter.py             # 速率限制中间件
├── routers/
│   └── user_router.py              # 用户路由（已加防护）
├── services/
│   └── ip_service.py               # IP管理服务
├── SERVER_EMERGENCY_GUIDE.md       # 详细操作指南
├── QUICK_FIX.md                    # 快速修复指南
└── EMERGENCY_TOOLS_README.md       # 本文件
```

---

## ✅ 验证清单

部署完成后，请确认:

- [ ] 诊断脚本运行正常
- [ ] 恶意IP已封禁
- [ ] 代码已更新到最新版本
- [ ] 速率限制中间件已集成
- [ ] 服务已重启
- [ ] 后台可以正常访问
- [ ] `/health` 接口返回正常
- [ ] Redis缓存工作正常
- [ ] MySQL连接数正常
- [ ] 日志无ERROR

---

## 💡 后续优化建议

1. **Nginx层面限流**:
   ```nginx
   limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

   location /api/ {
       limit_req zone=mylimit burst=20;
       proxy_pass http://localhost:3000;
   }
   ```

2. **添加验证码**: 在注册和登录接口添加图形验证码

3. **CDN防护**: 使用Cloudflare等CDN服务

4. **监控告警**: 配置异常活动告警（如注册数突增）

5. **定期清理**: 定时任务清理僵尸账号

6. **数据库优化**: 为常用查询字段添加索引

---

## 🆘 需要帮助？

如果遇到问题，请提供:

1. **诊断结果**: `cat diagnosis.txt`
2. **服务日志**: `tail -100 server.log`
3. **系统状态**: `free -h && df -h`
4. **MySQL状态**: `mysql -u root -p -e "SHOW STATUS;"`

---

**工具版本**: v1.0
**创建时间**: 2026-01-02
**适用场景**: 恶意批量注册攻击应急响应
