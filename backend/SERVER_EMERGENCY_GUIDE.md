# 🚨 服务器紧急修复指南

**服务器IP**: 8.137.103.175
**问题**: 恶意批量注册导致后台无法访问
**执行时间**: 立即

---

## 📋 快速修复步骤（5分钟）

### 第一步：登录服务器并检查

```bash
# 1. 登录服务器
ssh root@8.137.103.175
# 密码: Jndc@12345

# 2. 进入项目目录
cd /path/to/backend  # 替换为实际路径

# 3. 检查当前进程
ps aux | grep python
ps aux | grep uvicorn

# 4. 查看系统资源
top
# 按 q 退出

# 5. 检查MySQL连接数
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

### 第二步：紧急诊断

```bash
# 1. 运行诊断脚本
python3 emergency_diagnosis.py > diagnosis_result.txt

# 2. 查看诊断结果
cat diagnosis_result.txt

# 3. 检查历史攻击
python3 check_historical_attacks.py > attack_history.txt
cat attack_history.txt
```

**📤 把诊断结果发给我，我帮你分析！**

---

### 第三步：立即封禁恶意IP

```bash
# 方式1: 自动检测并封禁（推荐）
python3 emergency_block_ips.py

# 看到提示后输入 yes 确认

# 方式2: 无需确认，直接封禁
python3 emergency_block_ips.py --all

# 方式3: 封禁特定IP
python3 emergency_block_ips.py --ip 1.2.3.4
```

---

### 第四步：更新代码（添加防护）

```bash
# 1. 备份当前代码
cp routers/user_router.py routers/user_router.py.backup

# 2. 从Git拉取最新代码（包含防护措施）
git stash
git pull origin main

# 3. 重启服务器
# 如果使用 systemd
sudo systemctl restart backend

# 或者手动重启
pkill -f "python.*main.py"
nohup python3 main.py > server.log 2>&1 &

# 或使用 start.py
pkill -f "python.*main.py"
nohup python3 start.py > server.log 2>&1 &
```

---

### 第五步：验证修复

```bash
# 1. 检查服务是否运行
ps aux | grep python

# 2. 检查端口
netstat -tlnp | grep 3000

# 3. 测试API
curl http://localhost:3000/health

# 4. 查看实时日志
tail -f server.log

# 5. 检查Redis缓存
redis-cli --scan --pattern "ip_blocked:*"
```

---

## 🛡️ 如果后台还是打不开

### 情况1: 数据库连接耗尽

```bash
# 1. 查看MySQL进程
mysql -u root -p -e "SHOW FULL PROCESSLIST;"

# 2. 杀死异常连接
mysql -u root -p -e "KILL <process_id>;"  # 替换process_id

# 3. 重启MySQL（谨慎！）
sudo systemctl restart mysql
```

### 情况2: 服务器资源耗尽

```bash
# 1. 查看内存使用
free -h

# 2. 查看磁盘使用
df -h

# 3. 清理日志（如果磁盘满了）
find /var/log -type f -name "*.log" -mtime +7 -delete

# 4. 重启服务器（最后手段）
sudo reboot
```

### 情况3: 恶意请求持续攻击

```bash
# 1. 临时防火墙封禁
# 查看当前连接最多的IP
netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n | tail -20

# 2. 封禁特定IP
iptables -A INPUT -s 1.2.3.4 -j DROP

# 3. 保存防火墙规则
iptables-save > /etc/iptables/rules.v4

# 4. 查看防火墙规则
iptables -L -n
```

---

## 📊 数据清理（可选）

如果发现大量恶意数据：

```bash
# 创建数据库备份（先备份！）
mysqldump -u root -p game_db > backup_$(date +%Y%m%d).sql

# 运行清理脚本
python3 cleanup_malicious_data.py
```

---

## 🔍 持续监控

### 监控脚本
```bash
# 1. 查看实时连接
watch -n 5 'mysql -u root -p<密码> -e "SHOW STATUS LIKE \"Threads_connected\";"'

# 2. 监控Redis
watch -n 5 'redis-cli INFO stats | grep keyspace'

# 3. 监控CPU/内存
htop

# 4. 监控日志
tail -f server.log | grep -E "ERROR|WARNING|封禁|异常"
```

---

## ⚠️ 紧急联系

如果以上步骤都无法解决，执行以下操作：

### 临时关闭注册功能
```bash
# 编辑配置文件
vi config.py

# 添加一行
REGISTRATION_ENABLED = False

# 重启服务
sudo systemctl restart backend
```

### 临时关闭所有API（仅保留管理后台）
```bash
# 使用Nginx反向代理限制
vi /etc/nginx/sites-available/default

# 添加限流配置
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

location /api/ {
    limit_req zone=mylimit burst=20;
    proxy_pass http://localhost:3000;
}

# 重启Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📱 完成后确认清单

- [ ] 诊断脚本已运行，结果已查看
- [ ] 恶意IP已封禁
- [ ] 代码已更新（包含防护）
- [ ] 服务已重启
- [ ] 健康检查通过 (/health)
- [ ] 后台可以正常打开
- [ ] Redis缓存正常
- [ ] MySQL连接数正常
- [ ] 日志无ERROR

---

## 📝 后续优化建议

1. **添加Nginx限流** - 限制单IP请求速率
2. **添加验证码** - 注册和登录接口
3. **CDN防护** - 使用Cloudflare等
4. **监控告警** - 设置异常告警
5. **定期清理** - 清理僵尸账号

---

**需要帮助随时联系！** 🆘
