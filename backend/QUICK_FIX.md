# 🚨 紧急修复 - 5分钟快速指南

**服务器**: 8.137.103.175
**问题**: 恶意批量注册导致后台无法访问

---

## ⚡ 立即执行（按顺序）

### 1️⃣ 登录服务器（30秒）
```bash
ssh root@8.137.103.175
# 密码: Jndc@12345

cd /path/to/backend  # 替换为实际路径
```

### 2️⃣ 诊断问题（1分钟）
```bash
# 运行诊断
python3 emergency_diagnosis.py > diagnosis.txt
cat diagnosis.txt

# 发给我看诊断结果！
```

### 3️⃣ 封禁恶意IP（1分钟）
```bash
# 自动检测并封禁（推荐）
python3 emergency_block_ips.py

# 看到列表后输入 yes 确认
```

### 4️⃣ 更新代码（2分钟）
```bash
# 拉取最新代码（包含防护措施）
git stash
git pull origin main

# 重启服务
pkill -f "python.*main.py"
nohup python3 main.py > server.log 2>&1 &
```

### 5️⃣ 验证修复（30秒）
```bash
# 检查服务是否运行
ps aux | grep python

# 测试API
curl http://localhost:3000/health

# 查看日志
tail -f server.log
```

---

## 📋 完成检查清单

- [ ] 服务器已登录
- [ ] 诊断结果已查看
- [ ] 恶意IP已封禁
- [ ] 代码已更新
- [ ] 服务已重启
- [ ] 后台可以打开了

---

## 🆘 如果还是打不开

### 数据库连接满了
```bash
# 查看连接数
mysql -u root -p -e "SHOW FULL PROCESSLIST;"

# 重启MySQL（谨慎！）
sudo systemctl restart mysql
```

### 服务器资源耗尽
```bash
# 查看资源
free -h
df -h
top

# 最后手段：重启服务器
sudo reboot
```

### 攻击还在继续
```bash
# 查看实时连接
netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n | tail -20

# 手动封禁IP（替换为实际IP）
python3 emergency_block_ips.py --ip 1.2.3.4
```

---

## 📞 需要帮助？

把以下信息发给我：

1. **诊断结果**:
   ```bash
   cat diagnosis.txt
   ```

2. **服务器日志**:
   ```bash
   tail -100 server.log
   ```

3. **MySQL状态**:
   ```bash
   mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
   ```

---

## 💡 修复后建议

```bash
# 清理恶意数据
python3 cleanup_malicious_data.py

# 启用速率限制（在 main.py 中添加）
# from middleware.rate_limiter import RateLimitMiddleware
# app.add_middleware(RateLimitMiddleware)
```

---

**详细指南**: 查看 `SERVER_EMERGENCY_GUIDE.md`
