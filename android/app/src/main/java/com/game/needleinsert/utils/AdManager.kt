package com.game.needleinsert.utils

import android.content.Context
import android.util.Log
import com.game.needleinsert.model.*
import kotlinx.coroutines.*
import kotlin.random.Random

object AdManager {
    private var currentAd: AdConfig? = null
    private var adWatchStartTime: Long = 0
    private var lastAdRequestTime: Long = 0
    private val adCooldownTime = 30 * 1000L // 30秒冷却时间
    
    // 模拟广告数据（实际应该从后端获取）
    private val mockAds = listOf(
        AdConfig("ad1", "游戏推荐广告", "https://example.com/video1.mp4", "https://example.com/image1.jpg", 50),
        AdConfig("ad2", "应用下载广告", "https://example.com/video2.mp4", "https://example.com/image2.jpg", 80),
        AdConfig("ad3", "商品推广广告", "https://example.com/video3.mp4", "https://example.com/image3.jpg", 100),
        AdConfig("ad4", "特殊活动广告", "https://example.com/video4.mp4", "https://example.com/image4.jpg", 150)
    )
    
    /**
     * 检查是否可以显示广告
     */
    fun canShowAd(): Boolean {
        val currentTime = System.currentTimeMillis()
        return currentTime - lastAdRequestTime > adCooldownTime
    }
    
    /**
     * 获取随机广告
     */
    suspend fun getRandomAd(): AdConfig? {
        return try {
            delay(500) // 模拟网络请求
            if (Random.nextFloat() < 0.8f) { // 80%概率有广告
                val ad = mockAds.random()
                currentAd = ad
                lastAdRequestTime = System.currentTimeMillis()
                Log.d("AdManager", "获取广告成功: ${ad.title}")
                ad
            } else {
                Log.d("AdManager", "暂无可用广告")
                null
            }
        } catch (e: Exception) {
            Log.e("AdManager", "获取广告失败: ${e.message}")
            null
        }
    }
    
    /**
     * 开始观看广告
     */
    fun startWatchingAd() {
        adWatchStartTime = System.currentTimeMillis()
        Log.d("AdManager", "开始观看广告")
    }
    
    /**
     * 完成观看广告并获取奖励
     */
    suspend fun completeAdWatch(userId: String): AdReward? {
        val ad = currentAd ?: return null
        val watchDuration = System.currentTimeMillis() - adWatchStartTime
        
        return try {
            // 模拟广告观看验证（至少观看15秒）
            if (watchDuration >= 15000) {
                val reward = AdReward(
                    coins = ad.rewardCoins,
                    message = "观看广告奖励 ${ad.rewardCoins} 金币！"
                )
                
                             // TODO: 真实情况下应该调用后端API验证
             // val request = AdWatchRequest(userId, ad.id, watchDuration)
             // val response = RetrofitClient.getApiService().submitAdWatch("token", request)
             // return RetrofitClient.getResponseData(response)
                
                Log.d("AdManager", "广告观看完成，奖励: ${reward.coins} 金币")
                currentAd = null
                reward
            } else {
                Log.w("AdManager", "观看时间不足: ${watchDuration}ms")
                null
            }
        } catch (e: Exception) {
            Log.e("AdManager", "提交广告观看记录失败: ${e.message}")
            null
        }
    }
    
    /**
     * 取消观看广告
     */
    fun cancelAdWatch() {
        Log.d("AdManager", "取消观看广告")
        currentAd = null
        adWatchStartTime = 0
    }
    
    /**
     * 模拟视频广告播放
     */
    suspend fun simulateVideoPlayback(
        onProgress: (Int) -> Unit,
        onComplete: () -> Unit,
        onSkip: () -> Unit
    ) {
        val totalDuration = 30 // 30秒广告
        var currentSecond = 0
        var canSkip = false
        
        while (currentSecond <= totalDuration) {
            delay(1000) // 每秒更新一次
            currentSecond++
            
            // 15秒后可以跳过
            if (currentSecond >= 15 && !canSkip) {
                canSkip = true
            }
            
            onProgress(currentSecond)
            
            // 播放完成
            if (currentSecond >= totalDuration) {
                onComplete()
                break
            }
        }
    }
    
    /**
     * 检查每日广告观看限制
     */
    fun checkDailyAdLimit(): Boolean {
        // TODO: 实现每日限制检查
        // 可以使用SharedPreferences存储今日观看次数
        return true
    }
} 