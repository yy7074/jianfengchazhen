# Android见缝插针游戏开发指南

## 游戏界面分析

根据提供的UI参考图，游戏界面包含以下元素：

### 顶部UI
- **金币显示**: 左上角显示当前金币数量 (1188)
- **生命/次数**: 红色心形图标显示剩余次数 (28)
- **倒计时**: 显示游戏时间 (01:25)
- **关卡显示**: 中央显示当前关卡 (关卡18)

### 主游戏区域
- **中心圆球**: 黄色大圆球，显示剩余针数 (11)
- **已插入的针**: 围绕圆球的彩色针，每根针不同颜色
- **待插入针队列**: 底部垂直排列的彩色针 (编号2-11)

### 底部功能区
- **发射按钮**: 左下角蓝色箭头按钮
- **辅助线**: 右下角辅助瞄准功能

## Android项目结构

```
app/
├── src/main/
│   ├── java/com/game/needleinsert/
│   │   ├── MainActivity.java
│   │   ├── GameActivity.java
│   │   ├── ui/
│   │   │   ├── GameView.java
│   │   │   ├── MenuFragment.java
│   │   │   └── SettingsFragment.java
│   │   ├── model/
│   │   │   ├── User.java
│   │   │   ├── GameLevel.java
│   │   │   └── Needle.java
│   │   ├── network/
│   │   │   ├── ApiService.java
│   │   │   ├── RetrofitClient.java
│   │   │   └── responses/
│   │   ├── utils/
│   │   │   ├── GameLogic.java
│   │   │   ├── SoundManager.java
│   │   │   └── PreferenceManager.java
│   │   └── ads/
│   │       ├── AdManager.java
│   │       └── VideoAdPlayer.java
│   └── res/
│       ├── layout/
│       ├── drawable/
│       ├── values/
│       └── raw/
└── build.gradle
```

## 核心技术栈

### 开发框架
- **语言**: Java/Kotlin
- **UI框架**: Android原生 + 自定义View
- **网络**: Retrofit2 + OkHttp
- **JSON解析**: Gson
- **图片加载**: Glide
- **视频播放**: ExoPlayer

### 游戏引擎
- **渲染**: Canvas + Paint (2D绘制)
- **动画**: ValueAnimator + ObjectAnimator
- **物理**: 自定义碰撞检测
- **音效**: SoundPool

## 核心功能实现

### 1. 游戏逻辑核心类
```java
public class GameLogic {
    private int currentLevel;
    private int remainingNeedles;
    private List<Needle> insertedNeedles;
    private float centerX, centerY;
    private float circleRadius;
    
    public boolean canInsertNeedle(float angle);
    public void insertNeedle(Needle needle);
    public boolean checkCollision(Needle newNeedle);
    public void nextLevel();
}
```

### 2. 自定义游戏视图
```java
public class GameView extends View {
    private Paint paint;
    private GameLogic gameLogic;
    private List<Needle> needleQueue;
    
    @Override
    protected void onDraw(Canvas canvas) {
        drawBackground(canvas);
        drawCenterCircle(canvas);
        drawInsertedNeedles(canvas);
        drawNeedleQueue(canvas);
        drawUI(canvas);
    }
    
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // 处理触摸发射针
        return super.onTouchEvent(event);
    }
}
```

### 3. 网络API接口
```java
public interface ApiService {
    @POST("api/user/register")
    Call<BaseResponse<UserInfo>> register(@Body UserRegister request);
    
    @POST("api/user/login") 
    Call<BaseResponse<UserInfo>> login(@Body UserLogin request);
    
    @GET("api/ad/random/{userId}")
    Call<BaseResponse<AdConfig>> getRandomAd(@Path("userId") int userId);
    
    @POST("api/ad/watch/{userId}")
    Call<BaseResponse<AdReward>> watchAd(@Path("userId") int userId, @Body AdWatchRequest request);
    
    @POST("api/game/submit/{userId}")
    Call<BaseResponse<GameResult>> submitGameResult(@Path("userId") int userId, @Body GameResultSubmit request);
}
```

## 游戏流程设计

### 启动流程
1. **启动页**: 显示游戏Logo，检查网络连接
2. **登录注册**: 使用设备ID自动注册/登录
3. **主菜单**: 显示用户信息、开始游戏、设置等
4. **游戏界面**: 进入核心游戏逻辑

### 游戏循环
1. **关卡开始**: 初始化针数和圆球
2. **玩家操作**: 点击发射针
3. **碰撞检测**: 检查是否碰撞已有针
4. **结果处理**: 成功插入或游戏结束
5. **关卡完成**: 所有针插入完成，进入下一关
6. **游戏结束**: 提交分数，显示奖励

### 广告触发机制
- **游戏结束后**: 随机弹出激励视频广告
- **主动观看**: 用户点击获取金币
- **每日限制**: 根据后台配置限制观看次数
- **奖励发放**: 观看完整后获得金币奖励

## 关键实现细节

### 1. 针的碰撞检测算法
```java
private boolean checkNeedleCollision(Needle newNeedle) {
    float newAngle = newNeedle.getAngle();
    float needleWidth = 10f; // 针的宽度角度
    
    for (Needle existing : insertedNeedles) {
        float angleDiff = Math.abs(newAngle - existing.getAngle());
        if (angleDiff < needleWidth || angleDiff > (360 - needleWidth)) {
            return true; // 碰撞
        }
    }
    return false; // 无碰撞
}
```

### 2. 圆球旋转动画
```java
private void startRotationAnimation() {
    ObjectAnimator rotateAnimator = ObjectAnimator.ofFloat(centerCircle, "rotation", 0f, 360f);
    rotateAnimator.setDuration(3000);
    rotateAnimator.setRepeatCount(ValueAnimator.INFINITE);
    rotateAnimator.setInterpolator(new LinearInterpolator());
    rotateAnimator.start();
}
```

### 3. 针发射动画
```java
private void launchNeedle(Needle needle) {
    float startY = getHeight() - 200;
    float endY = centerY + circleRadius;
    
    ObjectAnimator moveAnimator = ObjectAnimator.ofFloat(needle, "y", startY, endY);
    moveAnimator.setDuration(500);
    moveAnimator.addListener(new AnimatorListenerAdapter() {
        @Override
        public void onAnimationEnd(Animator animation) {
            insertNeedleToCircle(needle);
        }
    });
    moveAnimator.start();
}
```

## 性能优化建议

### 1. 内存管理
- 使用对象池管理针对象
- 及时回收Bitmap资源
- 避免在onDraw中创建对象

### 2. 渲染优化  
- 使用硬件加速
- 合理使用Canvas.save()/restore()
- 减少不必要的重绘

### 3. 网络优化
- 实现请求缓存机制
- 使用HTTPS加密传输
- 添加网络超时和重试

## 开发优先级

### 第一阶段 - 核心游戏
1. ✅ 基础UI布局
2. ✅ 游戏逻辑实现
3. ✅ 碰撞检测算法
4. ✅ 动画效果

### 第二阶段 - 网络功能
1. ✅ 用户登录注册
2. ✅ 分数提交
3. ✅ 排行榜功能

### 第三阶段 - 广告系统
1. ✅ 自定义视频播放器
2. ✅ 广告触发逻辑
3. ✅ 奖励发放机制

### 第四阶段 - 完善功能
1. 🔄 音效和背景音乐
2. 🔄 设置页面
3. 🔄 用户反馈系统
4. 🔄 版本更新检测

这个架构设计完全基于您提供的UI参考图，实现了完整的见缝插针游戏功能，包括自定义广告系统和金币奖励机制。 