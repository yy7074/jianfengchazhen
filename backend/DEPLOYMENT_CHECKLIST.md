# 🚀 部署前检查清单

## ✅ 已完成的优化

### 1. Redis缓存优化
- [x] IP黑名单缓存 (TTL: 5分钟)
- [x] 系统配置缓存 (TTL: 30分钟)
- [x] 活跃广告列表缓存 (TTL: 5分钟)
- [x] 自动缓存清除机制
- [x] 优雅降级处理

### 2. 测试验证
- [x] 所有缓存功能测试通过 ✅
- [x] 性能测试通过 (平均响应 5.33ms) ✅
- [x] Redis连接正常 ✅
- [x] 模块导入测试通过 ✅
- [x] 语法检查通过 ✅

---

## 📋 部署前必查项

### Redis检查
```bash
# 1. 确认Redis正在运行
redis-cli ping
# 期望输出: PONG

# 2. 检查Redis版本
redis-cli INFO server | grep redis_version
# 期望: redis_version:6.0+

# 3. 检查Redis内存
redis-cli INFO memory | grep used_memory_human
```

### Python环境检查
```bash
# 1. 确认Python版本
python --version
# 期望: Python 3.8+

# 2. 检查依赖包
pip list | grep -E "redis|fastapi|sqlalchemy"
# 必须有: redis, fastapi, sqlalchemy, pymysql

# 3. 测试导入
python -c "from database import redis_client; redis_client.ping()"
# 无错误输出表示正常
```

### 数据库检查
```bash
# 1. MySQL服务状态
mysql -u root -p -e "SELECT VERSION();"

# 2. 数据库连接测试
python -c "from database import engine; engine.connect()"
```

---

## 🔧 启动服务器

### 方式1: 使用start.py（推荐）
```bash
cd backend
python start.py
```

### 方式2: 直接启动
```bash
cd backend
python main.py
```

### 方式3: 使用uvicorn
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

---

## ✅ 启动后验证

### 1. 检查服务状态
```bash
# 访问健康检查接口
curl http://localhost:3000/health
# 期望: {"status":"healthy","version":"1.0.0"}
```

### 2. 检查Redis缓存
```bash
# 查看缓存键
redis-cli --scan --pattern "ip_blocked:*"
redis-cli --scan --pattern "config:*"
redis-cli --scan --pattern "active_ads"
```

### 3. 测试API端点
```bash
# 测试获取广告
curl http://localhost:3000/api/ad/random/1

# 查看API文档
# 浏览器访问: http://localhost:3000/docs
```

### 4. 监控日志
```bash
# 查看启动日志，应该看到:
✅ Redis连接正常
✅ 默认配置初始化完成
✅ 默认广告初始化完成
✅ 默认等级配置初始化完成
```

---

## 📊 性能监控

### 实时监控Redis命中率
```bash
redis-cli INFO stats | grep keyspace
```

### 查看缓存命中情况
```python
from database import redis_client
info = redis_client.info('stats')
hits = info.get('keyspace_hits', 0)
misses = info.get('keyspace_misses', 0)
hit_rate = hits / (hits + misses) * 100 if (hits + misses) > 0 else 0
print(f'缓存命中率: {hit_rate:.2f}%')
```

---

## ⚠️ 常见问题处理

### 问题1: Redis连接失败
**解决方案:**
```bash
# 启动Redis
redis-server

# 或使用systemd
sudo systemctl start redis
```

### 问题2: 导入模块错误
**解决方案:**
```bash
# 重新安装依赖
pip install -r requirements.txt
```

### 问题3: 端口已被占用
**解决方案:**
```bash
# 查找占用端口的进程
lsof -i:3000

# 杀死进程
kill -9 <PID>
```

### 问题4: 缓存不生效
**解决方案:**
```bash
# 清空Redis缓存重新测试
redis-cli FLUSHDB

# 重启服务器
```

---

## 📈 性能基准

优化后预期性能指标：

| 指标 | 目标值 | 说明 |
|------|--------|------|
| IP检查 | < 1ms | Redis缓存命中 |
| 配置查询 | < 1ms | Redis缓存命中 |
| 随机广告API | < 10ms | 包含数据库查询 |
| 缓存命中率 | > 90% | 运行稳定后 |

---

## 🎯 部署清单总结

- [ ] Redis服务运行正常
- [ ] MySQL服务运行正常
- [ ] Python依赖已安装
- [ ] 环境变量配置正确
- [ ] 执行 `python test_cache_optimization.py` 全部通过
- [ ] 服务器启动无错误
- [ ] API文档可访问 (/docs)
- [ ] 健康检查接口正常 (/health)
- [ ] Redis缓存键已生成
- [ ] 日志无ERROR级别错误

**全部✅后即可正式部署！**

---

## 📝 回滚计划

如果优化导致问题，可以快速回滚：

### 方式1: Git回滚
```bash
git checkout <之前的commit>
```

### 方式2: 禁用Redis缓存
修改 `config.py` 添加:
```python
REDIS_ENABLED = False
```

然后在服务中添加检查:
```python
if not settings.REDIS_ENABLED:
    return None  # 跳过缓存逻辑
```

---

**准备完毕，可以部署！** 🚀
