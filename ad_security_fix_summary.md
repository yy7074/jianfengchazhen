# 广告观看安全漏洞修复说明

## 问题描述

用户报告：广告偶尔会出现没有看完，点击结束也会获得金币。

## 问题根源

### 1. 服务端问题 (`backend/services/ad_service.py`)

**原代码（第75行）：**
```python
is_completed = watch_request.is_completed or watch_request.watch_duration >= min_duration
```

问题：使用 `or` 逻辑，只要客户端发送 `is_completed=True`，即使观看时长不够也会发放奖励。

### 2. 客户端问题 (`android/app/src/main/java/com/game/needleinsert/utils/AdManager.kt`)

**原代码（第276行）：**
```kotlin
val canGetReward = watchDuration >= requiredWatchTime || isCompleted
```

问题：同样使用 `or` 逻辑，允许跳过时长验证。

### 3. 请求模型问题 (`backend/schemas.py`)

**原代码（第98行）：**
```python
is_completed: bool = Field(default=True)  # 默认值为True
```

问题：默认值设为True，增加了安全风险。

## 修复方案

### 1. 服务端修复

**修改后代码：**
```python
# 检查观看时长是否达标（只依赖服务端验证的观看时长，不信任客户端的is_completed标志）
is_completed = watch_request.watch_duration >= min_duration
```

**核心原则：**
- 服务端只依赖自己验证的观看时长
- 不信任客户端发送的 `is_completed` 标志
- 防止客户端伪造完成状态

### 2. 客户端修复

**修改后代码：**
```kotlin
// 检查观看时间是否足够（只依赖实际观看时长，不信任is_completed标志）
val canGetReward = watchDuration >= requiredWatchTime
val actualIsCompleted = canGetReward  // 根据实际观看时长判断
```

**核心原则：**
- 客户端也只依赖实际观看时长
- 发送真实的完成状态给服务端
- 保持客户端和服务端逻辑一致

### 3. 请求模型修复

**修改后代码：**
```python
is_completed: bool = Field(default=False)  # 是否完整观看（由服务端验证，不信任客户端）
```

**核心原则：**
- 默认值改为False，更安全
- 添加注释说明由服务端验证

## 安全加固

### 验证流程
1. 客户端记录实际观看时长
2. 客户端根据时长计算是否完成
3. 发送请求到服务端（包含时长和完成状态）
4. **服务端重新验证时长，忽略客户端的完成标志**
5. 只有时长达标才发放奖励

### 关键点
- ✅ 服务端是唯一的信任源
- ✅ 所有验证逻辑在服务端执行
- ✅ 客户端的完成标志仅作参考，不作为发放奖励的依据

## 测试验证

运行测试脚本：
```bash
python test_ad_security_fix.py
```

测试场景：
1. 测试1：观看时长不够但发送 `is_completed=True`
   - 预期结果：不发放奖励 ✅
   
2. 测试2：观看时长足够且发送正确数据
   - 预期结果：正常发放奖励 ✅

## 影响范围

### 修改的文件
1. `backend/services/ad_service.py` - 服务端验证逻辑
2. `backend/schemas.py` - 请求模型定义
3. `android/app/src/main/java/com/game/needleinsert/utils/AdManager.kt` - 客户端判断逻辑

### 需要重启的服务
- 后端服务需要重启以应用新的验证逻辑
- Android应用需要重新编译和发布

### 兼容性
- 向后兼容：旧版客户端仍可正常工作
- 服务端现在会严格验证观看时长
- 不会影响正常观看广告的用户

## 部署步骤

1. **更新后端代码并重启服务：**
```bash
cd /Users/yy/Documents/GitHub/jianfengchazhen/backend
# 重启后端服务
sudo systemctl restart game-backend
```

2. **编译并发布新版Android应用：**
```bash
cd /Users/yy/Documents/GitHub/jianfengchazhen/android
./build.sh
# 然后通过管理后台上传新版APK
```

3. **测试验证：**
```bash
cd /Users/yy/Documents/GitHub/jianfengchazhen
python test_ad_security_fix.py
```

## 注意事项

1. **现有用户数据**：此修复不影响已有的观看记录和金币数据
2. **性能影响**：无性能影响，只是修改了验证逻辑
3. **用户体验**：正常观看广告的用户不会察觉到任何变化
4. **安全提升**：有效防止通过伪造完成状态来骗取金币

## 后续建议

1. 考虑添加更多的反作弊机制：
   - 检测观看时长的合理性（不能为负数、不能超过广告时长太多等）
   - 记录IP地址和设备信息，检测异常行为
   - 添加观看频率限制

2. 监控异常观看行为：
   - 观看时长异常短
   - 观看次数异常多
   - 同一IP大量观看

3. 定期审计：
   - 检查观看记录中的可疑数据
   - 分析金币发放是否正常

## 修复时间

- 发现时间：2025-10-15
- 修复时间：2025-10-15
- 测试时间：待测试
- 上线时间：待部署

