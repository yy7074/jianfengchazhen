package com.game.needleinsert.viewmodel

import android.util.Log
import androidx.compose.runtime.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.game.needleinsert.model.*
import com.game.needleinsert.utils.AdManager
import com.game.needleinsert.utils.SoundManager
import com.game.needleinsert.utils.UserManager
import com.game.needleinsert.network.RetrofitClient
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.*
import kotlin.random.Random

class GameViewModel : ViewModel() {
    
    // 游戏状态
    var gameData by mutableStateOf(GameData())
        private set
    
    // 已插入的针
    var insertedNeedles by mutableStateOf<List<Needle>>(emptyList())
        private set
    
    // 当前准备插入的针
    var currentNeedle by mutableStateOf<Needle?>(null)
        private set
    
    // 针发射动画状态
    var isNeedleLaunching by mutableStateOf(false)
        private set
    
    // 当前广告
    var currentAd by mutableStateOf<AdConfig?>(null)
        private set
    
    // 广告奖励显示
    var adReward by mutableStateOf<AdReward?>(null)
        private set
    
    // 圆盘旋转角度
    var diskRotation by mutableFloatStateOf(0f)
        private set
    
    // 游戏中心坐标
    var centerX by mutableFloatStateOf(0f)
    var centerY by mutableFloatStateOf(0f)
    
    // 圆盘半径 - 增大圆盘
    val diskRadius = 150f
    
    // 针的长度
    val needleLength = 80f
    
    // 安全间距(角度) - 降低难度，增大安全距离
    private val safeAngleDistance = 0.4f // 约23度
    
    // 初始化游戏
    fun initGame(screenWidth: Float, screenHeight: Float) {
        centerX = screenWidth / 2
        centerY = screenHeight / 2
        
        // 从UserManager获取最新的用户金币
        val currentUser = UserManager.getCurrentUser()
        val userCoins = currentUser?.coins ?: 0
        
        // 更新gameData中的金币数量
        gameData = gameData.copy(coins = userCoins)
        
        Log.d("GameViewModel", "游戏初始化，用户金币: $userCoins")
        
        // 如果是第一次初始化或者从第1关开始，才调用startNewGame
        if (gameData.level <= 1) {
            startNewGame()
        } else {
            // 否则只是恢复当前关卡的游戏
            resumeCurrentLevel()
        }
    }
    
    // 开始新游戏
    fun startNewGame() {
        val level = getCurrentLevel()
        val needleQueue = (1..level.needleCount).toList()
        val currentLevel = gameData.level
        val currentCoins = gameData.coins
        
        gameData = GameData(
            level = currentLevel,
            needlesRequired = level.needleCount,
            rotationSpeed = level.rotationSpeed,
            state = GameState.PLAYING,
            currentLevelType = level.levelType,
            needleQueue = needleQueue,
            isReversed = level.levelType == LevelType.REVERSE,
            coins = currentCoins, // 保持金币数量
            canShowAd = AdManager.canShowAd(),
            adState = AdState.NONE
        )
        insertedNeedles = emptyList()
        prepareNextNeedle()
        startDiskRotation()
        
        // 随机触发广告机会（关卡开始时）
        checkAndTriggerAd()
    }
    
    // 恢复当前关卡（用于从广告返回后恢复游戏状态）
    private fun resumeCurrentLevel() {
        val level = getCurrentLevel()
        val needleQueue = (1..level.needleCount).toList()
        
        // 恢复当前关卡状态，保持关卡和金币不变
        gameData = gameData.copy(
            needlesRequired = level.needleCount,
            needlesInserted = 0,
            rotationSpeed = level.rotationSpeed,
            state = GameState.PLAYING,
            currentLevelType = level.levelType,
            needleQueue = needleQueue,
            isReversed = level.levelType == LevelType.REVERSE,
            canShowAd = AdManager.canShowAd(),
            adState = AdState.NONE,
            score = gameData.score // 保持分数
        )
        insertedNeedles = emptyList()
        prepareNextNeedle()
        startDiskRotation()
        
        // 随机触发广告机会（关卡开始时）
        checkAndTriggerAd()
    }
    
    // 准备下一个针
    private fun prepareNextNeedle() {
        if (gameData.needlesInserted < gameData.needlesRequired) {
            val nextNeedleNumber = gameData.needleQueue.getOrNull(gameData.needlesInserted) ?: (gameData.needlesInserted + 1)
            val needleColor = getNeedleColor(nextNeedleNumber)
            
            currentNeedle = Needle(
                id = nextNeedleNumber,
                angle = PI.toFloat() / 2, // 从正下方开始
                radius = diskRadius + needleLength + 100f, // 距离更远，准备发射
                color = needleColor,
                number = nextNeedleNumber
            )
        } else {
            // 游戏完成，进入下一关
            nextLevel()
        }
    }
    
    // 获取针的颜色
    private fun getNeedleColor(number: Int): androidx.compose.ui.graphics.Color {
        val colors = listOf(
            androidx.compose.ui.graphics.Color(0xFF2196F3), // 蓝色
            androidx.compose.ui.graphics.Color(0xFFF44336), // 红色
            androidx.compose.ui.graphics.Color(0xFFFFEB3B), // 黄色
            androidx.compose.ui.graphics.Color(0xFF9C27B0), // 紫色
            androidx.compose.ui.graphics.Color(0xFF00BCD4), // 青色
            androidx.compose.ui.graphics.Color(0xFF4CAF50), // 绿色
            androidx.compose.ui.graphics.Color(0xFFFF9800), // 橙色
            androidx.compose.ui.graphics.Color(0xFFE91E63), // 粉色
            androidx.compose.ui.graphics.Color(0xFF795548), // 棕色
            androidx.compose.ui.graphics.Color(0xFF607D8B)  // 蓝灰色
        )
        return colors[(number - 1) % colors.size]
    }
    
    // 插入针
    fun insertNeedle() {
        val needle = currentNeedle ?: return
        if (gameData.state != GameState.PLAYING || isNeedleLaunching) return
        
        // 开始发射动画
        isNeedleLaunching = true
        SoundManager.playNeedleLaunch()
        
        viewModelScope.launch {
            // 动画持续时间和步数 - 更快的发射速度
            val animationDuration = 200L // 200毫秒，更快
            val steps = 25
            val stepDuration = animationDuration / steps
            
            val startRadius = needle.radius
            val targetRadius = diskRadius
            val radiusStep = (startRadius - targetRadius) / steps
            
            // 执行发射动画
            repeat(steps) { step ->
                val newRadius = startRadius - (radiusStep * (step + 1))
                currentNeedle = needle.copy(radius = newRadius)
                delay(stepDuration)
            }
            
            // 动画结束，检查碰撞
            if (canInsertNeedle(needle)) {
                // 成功插入
                SoundManager.playNeedleHit()
                val insertedNeedle = needle.copy(
                    radius = diskRadius,
                    isInserted = true
                )
                insertedNeedles = insertedNeedles + insertedNeedle
                
                gameData = gameData.copy(
                    needlesInserted = gameData.needlesInserted + 1,
                    score = gameData.score + 10
                )
                
                isNeedleLaunching = false
                prepareNextNeedle()
            } else {
                // 碰撞，游戏结束
                SoundManager.playGameOver()
                isNeedleLaunching = false
                gameOver()
            }
        }
    }
    
    // 检查是否可以插入针
    private fun canInsertNeedle(needle: Needle): Boolean {
        return insertedNeedles.all { existingNeedle ->
            val angleDiff = abs(normalizeAngle(needle.angle - existingNeedle.angle))
            angleDiff > safeAngleDistance
        }
    }
    
    // 标准化角度到 [0, 2π]
    private fun normalizeAngle(angle: Float): Float {
        var normalized = angle % (2 * PI.toFloat())
        if (normalized < 0) normalized += 2 * PI.toFloat()
        if (normalized > PI) normalized = 2 * PI.toFloat() - normalized
        return normalized
    }
    
    // 开始圆盘旋转
    private fun startDiskRotation() {
        viewModelScope.launch {
            var randomSpeedTimer = 0L
            var currentSpeed = gameData.rotationSpeed
            
            while (gameData.state == GameState.PLAYING) {
                // 根据关卡类型调整旋转行为
                when (gameData.currentLevelType) {
                    LevelType.RANDOM -> {
                        randomSpeedTimer += 16
                        if (randomSpeedTimer >= 1000) { // 每秒变速
                            currentSpeed = gameData.rotationSpeed * (0.5f + Random.nextFloat() * 1.5f)
                            randomSpeedTimer = 0L
                        }
                    }
                    LevelType.PRECISION -> {
                        // 精确模式：间歇性旋转
                        currentSpeed = if ((System.currentTimeMillis() / 500) % 2 == 0L) {
                            gameData.rotationSpeed
                        } else {
                            0f
                        }
                    }
                    else -> {
                        currentSpeed = gameData.rotationSpeed
                    }
                }
                
                val rotationDirection = if (gameData.isReversed) -1f else 1f
                diskRotation += currentSpeed * 2f * rotationDirection
                
                if (diskRotation >= 360f) {
                    diskRotation -= 360f
                } else if (diskRotation < 0f) {
                    diskRotation += 360f
                }
                
                // 同时旋转已插入的针
                insertedNeedles = insertedNeedles.map { needle ->
                    needle.copy(
                        angle = needle.angle + Math.toRadians((currentSpeed * 2.0 * rotationDirection).toDouble()).toFloat()
                    )
                }
                
                delay(16) // 约60 FPS
            }
        }
    }
    
    // 获取当前关卡配置 - 降低难度，减少针数，降低速度
    private fun getCurrentLevel(): GameLevel {
        return when (gameData.level) {
            1 -> GameLevel(1, 6, 0.8f, levelType = LevelType.NORMAL, description = "入门关卡")
            2 -> GameLevel(2, 8, 1f, levelType = LevelType.NORMAL, description = "初级挑战")
            3 -> GameLevel(3, 10, 1.2f, levelType = LevelType.SPEED, description = "高速旋转")
            4 -> GameLevel(4, 12, 1.4f, levelType = LevelType.REVERSE, description = "反向旋转")
            5 -> GameLevel(5, 14, 1.6f, levelType = LevelType.RANDOM, description = "变速挑战")
            6 -> GameLevel(6, 16, 1.2f, obstacles = 1, levelType = LevelType.OBSTACLE, description = "障碍关卡")
            7 -> GameLevel(7, 18, 1.8f, levelType = LevelType.LARGE, description = "大量针考验")
            8 -> GameLevel(8, 10, 0.8f, levelType = LevelType.PRECISION, description = "精确插入")
            9 -> GameLevel(9, 20, 2f, levelType = LevelType.SPEED, description = "极速挑战")
            10 -> GameLevel(10, 25, 1.6f, obstacles = 2, levelType = LevelType.OBSTACLE, description = "终极考验")
            else -> {
                val baseCount = 30 + (gameData.level - 10) * 3
                val baseSpeed = 2f + (gameData.level - 10) * 0.2f
                GameLevel(
                    gameData.level, 
                    baseCount, 
                    baseSpeed, 
                    obstacles = (gameData.level - 10) / 4,
                    levelType = LevelType.values().random(),
                    description = "无尽挑战"
                )
            }
        }
    }
    
    // 下一关
    private fun nextLevel() {
        SoundManager.playLevelComplete()
        gameData = gameData.copy(
            level = gameData.level + 1,
            score = gameData.score + 50 // 通关奖励
        )
        
        val level = getCurrentLevel()
        val needleQueue = (1..level.needleCount).toList()
        gameData = gameData.copy(
            needlesRequired = level.needleCount,
            needlesInserted = 0,
            rotationSpeed = level.rotationSpeed,
            currentLevelType = level.levelType,
            needleQueue = needleQueue,
            isReversed = level.levelType == LevelType.REVERSE
        )
        
        insertedNeedles = emptyList()
        prepareNextNeedle()
    }
    
    // 游戏结束
    private fun gameOver() {
        gameData = gameData.copy(state = GameState.GAME_OVER)
        currentNeedle = null
    }
    
    // 重新开始游戏 - 现在需要先观看广告
    fun restartGame() {
        // 设置重启所需的广告状态
        gameData = gameData.copy(
            adState = AdState.RESTART_REQUIRED,
            isRestartAd = true
        )
        // 请求广告
        requestRestartAd()
    }
    
    // 请求重启游戏前的广告
    private fun requestRestartAd() {
        gameData = gameData.copy(adState = AdState.LOADING)
        
        viewModelScope.launch {
            try {
                val response = RetrofitClient.getApiService().getRandomAdForUser(UserManager.getCurrentUser()?.id ?: "0")
                if (response.isSuccessful && response.body()?.code == 200) {
                    val ad = response.body()?.data
                    if (ad != null) {
                        currentAd = ad
                        gameData = gameData.copy(
                            adState = AdState.READY,
                            isRestartAd = true  // 保持重启广告标志
                        )
                    } else {
                        // 没有广告可播放，直接重新开始游戏
                        proceedWithRestart()
                    }
                } else {
                    // 广告加载失败，直接重新开始游戏
                    proceedWithRestart()
                }
            } catch (e: Exception) {
                // 网络错误，直接重新开始游戏
                proceedWithRestart()
            }
        }
    }
    
    // 执行实际的游戏重启
    private fun proceedWithRestart() {
        val currentLevel = gameData.level // 保存当前关卡
        val currentCoins = gameData.coins // 保存当前金币
        gameData = GameData(
            level = currentLevel,
            coins = currentCoins
        )
        insertedNeedles = emptyList()
        diskRotation = 0f
        isNeedleLaunching = false
        startNewGame()
    }
    
    // 观看重启广告完成后的回调
    fun onRestartAdCompleted() {
        proceedWithRestart()
    }
    
    // 暂停/恢复游戏
    fun togglePause() {
        gameData = when (gameData.state) {
            GameState.PLAYING -> gameData.copy(state = GameState.PAUSED)
            GameState.PAUSED -> {
                startDiskRotation()
                gameData.copy(state = GameState.PLAYING)
            }
            else -> gameData
        }
    }
    
    // 检查并触发广告
    private fun checkAndTriggerAd() {
        // 80%概率在关卡开始时显示广告机会（方便测试）
        if (Random.nextFloat() < 0.8f && AdManager.canShowAd()) {
            gameData = gameData.copy(canShowAd = true)
        }
    }
    
    // 请求观看广告
    fun requestWatchAd() {
        if (!gameData.canShowAd || gameData.adState != AdState.NONE) return
        
        viewModelScope.launch {
            gameData = gameData.copy(adState = AdState.LOADING)
            
            // 清除广告缓存，确保获取最新的可用广告
            AdManager.clearAdCache()
            
            val currentUser = UserManager.getCurrentUser()
            val userId = currentUser?.id ?: "1"
            val deviceId = currentUser?.deviceId ?: "device_123"
            
            Log.d("GameViewModel", "请求广告，用户ID: $userId")
            
            val ad = AdManager.getRandomAd(userId, deviceId, gameData.level)
            if (ad != null) {
                Log.d("GameViewModel", "获取到广告: ID=${ad.id}, 标题=${ad.title}")
                currentAd = ad
                gameData = gameData.copy(
                    adState = AdState.READY,
                    canShowAd = false
                )
            } else {
                Log.w("GameViewModel", "没有获取到可用广告")
                gameData = gameData.copy(
                    adState = AdState.FAILED,
                    canShowAd = false
                )
            }
        }
    }
    
    // 开始播放广告
    fun startPlayingAd() {
        if (gameData.adState != AdState.READY) return
        
        gameData = gameData.copy(adState = AdState.PLAYING)
        AdManager.startWatchingAd()
    }
    
    // 重置广告状态（用于全屏广告）
    fun resetAdState() {
        // 检查是否是重启广告
        val wasRestartAd = gameData.isRestartAd
        
        // 刷新用户金币（从本地存储获取最新值）
        val currentUser = UserManager.getCurrentUser()
        val oldCoins = gameData.coins
        val latestCoins = currentUser?.coins ?: gameData.coins
        
        Log.d("GameViewModel", "重置广告状态，刷新金币: $oldCoins -> $latestCoins, 是否重启广告: $wasRestartAd")
        
        // 更新金币并检查是否有增加
        val coinDiff = latestCoins - oldCoins
        gameData = gameData.copy(
            coins = latestCoins,
            adState = AdState.NONE,
            canShowAd = false,
            isRestartAd = false  // 重置重启广告标志
        )
        
        // 如果金币增加了，先显示奖励提示（即便是重启广告也提示再重启）
        if (coinDiff > 0) {
            adReward = AdReward(
                coins = coinDiff,
                message = "观看广告获得 $coinDiff 金币！"
            )
            Log.d("GameViewModel", "显示奖励提示: +$coinDiff 金币")
        }
        
        // 如果是重启广告，观看完成后执行游戏重启（延迟一点点，给提示渲染机会）
        if (wasRestartAd) {
            Log.d("GameViewModel", "重启广告观看完成，准备重启游戏")
            viewModelScope.launch {
                delay(300) // 短暂延时避免立即再次触发广告逻辑或UI闪烁
                onRestartAdCompleted()
            }
            return
        }
        
        // 非重启广告时，若显示了奖励提示，则3秒后隐藏
        if (coinDiff > 0) {
            viewModelScope.launch {
                delay(3000)
                adReward = null
                Log.d("GameViewModel", "隐藏奖励提示")
            }
        }
        
        currentAd = null
    }
    
    // 完成观看广告
    fun completeAdWatch() {
        if (gameData.adState != AdState.PLAYING) return
        
        viewModelScope.launch {
            val currentUser = UserManager.getCurrentUser()
            val userId = currentUser?.id?.toString() ?: "1"
            
            Log.d("GameViewModel", "开始观看广告完成处理，用户ID: $userId")
            Log.d("GameViewModel", "观看前金币: ${gameData.coins}")
            
            val reward = AdManager.completeAdWatch(userId)
            if (reward != null) {
                // 获取最新的用户金币数量
                val updatedUser = UserManager.getCurrentUser()
                val oldCoins = gameData.coins
                val newCoins = updatedUser?.coins ?: (gameData.coins + reward.coins)
                val actualReward = newCoins - oldCoins
                
                Log.d("GameViewModel", "AdManager返回奖励: ${reward.coins}")
                Log.d("GameViewModel", "UserManager中的金币: ${updatedUser?.coins}")
                Log.d("GameViewModel", "观看前金币: $oldCoins, 观看后金币: $newCoins")
                Log.d("GameViewModel", "实际获得奖励: $actualReward")
                
                // 使用实际奖励数量更新显示
                val finalReward = AdReward(
                    coins = actualReward,
                    message = "观看广告奖励 $actualReward 金币！"
                )
                
                // 发放奖励并更新UI
                gameData = gameData.copy(
                    coins = newCoins,
                    adState = AdState.COMPLETED
                )
                adReward = finalReward
                
                Log.d("GameViewModel", "UI更新完成，显示金币: ${gameData.coins}, 奖励提示: ${finalReward.message}")
                
                // 3秒后隐藏奖励提示
                delay(3000)
                adReward = null
                gameData = gameData.copy(adState = AdState.NONE)
            } else {
                Log.w("GameViewModel", "广告观看失败，没有获得奖励")
                gameData = gameData.copy(adState = AdState.FAILED)
            }
            currentAd = null
        }
    }
    
    // 取消观看广告
    fun cancelAdWatch() {
        AdManager.cancelAdWatch()
        currentAd = null
        gameData = gameData.copy(
            adState = AdState.NONE,
            canShowAd = false,
            isRestartAd = false  // 重置重启广告标志
        )
    }
    
    // 关闭广告奖励提示
    fun dismissAdReward() {
        adReward = null
    }

    // 从全屏广告Activity回传时，兜底显示奖励提示（不修改金币，仅提示）
    fun showAdRewardFallback(coins: Int, message: String?) {
        if (coins <= 0) return
        adReward = AdReward(
            coins = coins,
            message = message ?: "观看广告获得 $coins 金币！"
        )
        viewModelScope.launch {
            delay(3000)
            adReward = null
        }
    }
} 