package com.game.needleinsert.viewmodel

import androidx.compose.runtime.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.game.needleinsert.model.*
import com.game.needleinsert.utils.SoundManager
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
    
    // 圆盘旋转角度
    var diskRotation by mutableFloatStateOf(0f)
        private set
    
    // 游戏中心坐标
    var centerX by mutableFloatStateOf(0f)
    var centerY by mutableFloatStateOf(0f)
    
    // 圆盘半径
    val diskRadius = 120f
    
    // 针的长度
    val needleLength = 80f
    
    // 安全间距(角度)
    private val safeAngleDistance = 0.3f // 约17度
    
    // 初始化游戏
    fun initGame(screenWidth: Float, screenHeight: Float) {
        centerX = screenWidth / 2
        centerY = screenHeight / 2
        startNewGame()
    }
    
    // 开始新游戏
    fun startNewGame() {
        val level = getCurrentLevel()
        gameData = GameData(
            level = level.level,
            needlesRequired = level.needleCount,
            rotationSpeed = level.rotationSpeed,
            state = GameState.PLAYING
        )
        insertedNeedles = emptyList()
        prepareNextNeedle()
        startDiskRotation()
    }
    
    // 准备下一个针
    private fun prepareNextNeedle() {
        if (gameData.needlesInserted < gameData.needlesRequired) {
            currentNeedle = Needle(
                id = gameData.needlesInserted + 1,
                angle = PI.toFloat() / 2, // 从正下方开始
                radius = diskRadius + needleLength + 100f // 距离更远，准备发射
            )
        } else {
            // 游戏完成，进入下一关
            nextLevel()
        }
    }
    
    // 插入针
    fun insertNeedle() {
        val needle = currentNeedle ?: return
        if (gameData.state != GameState.PLAYING || isNeedleLaunching) return
        
        // 开始发射动画
        isNeedleLaunching = true
        SoundManager.playNeedleLaunch()
        
        viewModelScope.launch {
            // 动画持续时间和步数
            val animationDuration = 300L // 300毫秒
            val steps = 30
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
            while (gameData.state == GameState.PLAYING) {
                diskRotation += gameData.rotationSpeed * 2f // 旋转速度
                if (diskRotation >= 360f) {
                    diskRotation -= 360f
                }
                
                // 同时旋转已插入的针
                insertedNeedles = insertedNeedles.map { needle ->
                    needle.copy(
                        angle = needle.angle + Math.toRadians(gameData.rotationSpeed * 2.0).toFloat()
                    )
                }
                
                delay(16) // 约60 FPS
            }
        }
    }
    
    // 获取当前关卡配置
    private fun getCurrentLevel(): GameLevel {
        return when (gameData.level) {
            1 -> GameLevel(1, 8, 1f)
            2 -> GameLevel(2, 10, 1.2f)
            3 -> GameLevel(3, 12, 1.5f)
            4 -> GameLevel(4, 15, 1.8f)
            5 -> GameLevel(5, 18, 2f)
            else -> GameLevel(gameData.level, 20 + gameData.level * 2, 2f + gameData.level * 0.2f)
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
        gameData = gameData.copy(
            needlesRequired = level.needleCount,
            needlesInserted = 0,
            rotationSpeed = level.rotationSpeed
        )
        
        insertedNeedles = emptyList()
        prepareNextNeedle()
    }
    
    // 游戏结束
    private fun gameOver() {
        gameData = gameData.copy(state = GameState.GAME_OVER)
        currentNeedle = null
    }
    
    // 重新开始游戏
    fun restartGame() {
        gameData = GameData()
        insertedNeedles = emptyList()
        diskRotation = 0f
        isNeedleLaunching = false
        startNewGame()
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
} 