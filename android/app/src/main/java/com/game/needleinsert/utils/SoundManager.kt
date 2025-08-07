package com.game.needleinsert.utils

import android.content.Context
import android.media.AudioAttributes
import android.media.SoundPool
import android.util.Log

object SoundManager {
    private var soundPool: SoundPool? = null
    private var isInitialized = false
    
    // 音效ID（预留）
    private var needleLaunchSoundId: Int = 0
    private var needleHitSoundId: Int = 0
    private var gameOverSoundId: Int = 0
    private var levelCompleteSoundId: Int = 0
    
    fun init(context: Context) {
        if (isInitialized) return
        
        try {
            val audioAttributes = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()
            
            soundPool = SoundPool.Builder()
                .setMaxStreams(5)
                .setAudioAttributes(audioAttributes)
                .build()
            
            // TODO: 加载音效文件
            // needleLaunchSoundId = soundPool?.load(context, R.raw.needle_launch, 1) ?: 0
            // needleHitSoundId = soundPool?.load(context, R.raw.needle_hit, 1) ?: 0
            // gameOverSoundId = soundPool?.load(context, R.raw.game_over, 1) ?: 0
            // levelCompleteSoundId = soundPool?.load(context, R.raw.level_complete, 1) ?: 0
            
            isInitialized = true
            Log.d("SoundManager", "音效系统初始化成功")
        } catch (e: Exception) {
            Log.e("SoundManager", "音效系统初始化失败: ${e.message}")
        }
    }
    
    fun playNeedleLaunch() {
        try {
            // soundPool?.play(needleLaunchSoundId, 1f, 1f, 1, 0, 1f)
            Log.d("SoundManager", "播放针发射音效")
        } catch (e: Exception) {
            Log.e("SoundManager", "播放针发射音效失败: ${e.message}")
        }
    }
    
    fun playNeedleHit() {
        try {
            // soundPool?.play(needleHitSoundId, 1f, 1f, 1, 0, 1f)
            Log.d("SoundManager", "播放针命中音效")
        } catch (e: Exception) {
            Log.e("SoundManager", "播放针命中音效失败: ${e.message}")
        }
    }
    
    fun playGameOver() {
        try {
            // soundPool?.play(gameOverSoundId, 1f, 1f, 1, 0, 1f)
            Log.d("SoundManager", "播放游戏结束音效")
        } catch (e: Exception) {
            Log.e("SoundManager", "播放游戏结束音效失败: ${e.message}")
        }
    }
    
    fun playLevelComplete() {
        try {
            // soundPool?.play(levelCompleteSoundId, 1f, 1f, 1, 0, 1f)
            Log.d("SoundManager", "播放关卡完成音效")
        } catch (e: Exception) {
            Log.e("SoundManager", "播放关卡完成音效失败: ${e.message}")
        }
    }
    
    fun release() {
        try {
            soundPool?.release()
            soundPool = null
            isInitialized = false
            Log.d("SoundManager", "音效系统已释放")
        } catch (e: Exception) {
            Log.e("SoundManager", "音效系统释放失败: ${e.message}")
        }
    }
} 