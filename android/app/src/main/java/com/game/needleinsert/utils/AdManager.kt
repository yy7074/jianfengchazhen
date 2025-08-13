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
    
    // 缓存的广告列表（从后端获取）
    private var cachedAds: List<AdConfig> = emptyList()
    private var adsCacheTime: Long = 0
    private val cacheExpireTime = 10 * 60 * 1000L // 10分钟缓存过期
    
    // 模拟广告数据（作为后备数据）
    private val fallbackAds = listOf(
        AdConfig(
            id = "ad1", 
            title = "精品游戏推荐", 
            description = "发现更多好玩的游戏",
            videoUrl = "https://example.com/video1.mp4", 
            imageUrl = "https://example.com/image1.jpg", 
            rewardCoins = 80,
            duration = 30,
            skipTime = 15,
            advertiser = "游戏联盟"
        ),
        AdConfig(
            id = "ad2", 
            title = "热门应用下载", 
            description = "最新最热门的手机应用",
            videoUrl = "https://example.com/video2.mp4", 
            imageUrl = "https://example.com/image2.jpg", 
            rewardCoins = 100,
            duration = 25,
            skipTime = 12,
            advertiser = "应用商店"
        ),
        AdConfig(
            id = "ad3", 
            title = "限时特价商品", 
            description = "超值优惠，不容错过",
            videoUrl = "https://example.com/video3.mp4", 
            imageUrl = "https://example.com/image3.jpg", 
            rewardCoins = 120,
            duration = 35,
            skipTime = 18,
            advertiser = "购物平台"
        ),
        AdConfig(
            id = "ad4", 
            title = "新用户专享福利", 
            description = "注册即送大礼包",
            videoUrl = "https://example.com/video4.mp4", 
            imageUrl = "https://example.com/image4.jpg", 
            rewardCoins = 150,
            duration = 28,
            skipTime = 15,
            advertiser = "福利中心"
        )
    )
    
    /**
     * 检查是否可以显示广告
     */
    fun canShowAd(): Boolean {
        val currentTime = System.currentTimeMillis()
        return currentTime - lastAdRequestTime > adCooldownTime
    }
    
    /**
     * 从后端获取广告列表
     */
    suspend fun loadAdsFromBackend(userId: String, deviceId: String, userLevel: Int): List<AdConfig> {
        return try {
            // 检查缓存是否有效
            val currentTime = System.currentTimeMillis()
            if (cachedAds.isNotEmpty() && (currentTime - adsCacheTime) < cacheExpireTime) {
                Log.d("AdManager", "使用缓存的广告列表")
                return cachedAds
            }
            
            // TODO: 实际调用后端API
            // val request = AdListRequest(userId, deviceId, userLevel, lastAdRequestTime)
            // val response = RetrofitClient.getApiService().getAvailableAds("token", request)
            // val ads = RetrofitClient.getResponseData(response) ?: fallbackAds
            
            // 模拟网络请求延迟
            delay(800)
            
            // 模拟后端返回的广告配置（根据用户等级和行为）
            val backendAds = when {
                userLevel >= 5 -> fallbackAds + AdConfig(
                    id = "vip_ad1",
                    title = "VIP专属福利",
                    description = "高级用户专享超级奖励",
                    videoUrl = "https://example.com/vip_video.mp4",
                    imageUrl = "https://example.com/vip_image.jpg",
                    rewardCoins = 200,
                    duration = 20,
                    skipTime = 10,
                    advertiser = "VIP俱乐部"
                )
                userLevel >= 3 -> fallbackAds.take(3)
                else -> fallbackAds.take(2)
            }
            
            // 过滤激活的广告
            val activeAds = backendAds.filter { it.isActive }
            
            // 更新缓存
            cachedAds = activeAds
            adsCacheTime = currentTime
            
            Log.d("AdManager", "从后端获取到 ${activeAds.size} 个广告")
            activeAds
            
        } catch (e: Exception) {
            Log.e("AdManager", "获取后端广告失败: ${e.message}")
            fallbackAds // 失败时返回后备广告
        }
    }
    
    /**
     * 根据权重获取随机广告
     */
    suspend fun getRandomAd(userId: String = "default", deviceId: String = "default", userLevel: Int = 1): AdConfig? {
        return try {
            val availableAds = loadAdsFromBackend(userId, deviceId, userLevel)
            if (availableAds.isEmpty()) {
                Log.d("AdManager", "暂无可用广告")
                return null
            }
            
            // 根据权重选择广告
            val totalWeight = availableAds.sumOf { it.weight }
            val randomWeight = Random.nextInt(totalWeight)
            var currentWeight = 0
            
            for (ad in availableAds) {
                currentWeight += ad.weight
                if (randomWeight < currentWeight) {
                    currentAd = ad
                    lastAdRequestTime = System.currentTimeMillis()
                    Log.d("AdManager", "获取广告成功: ${ad.title} (权重: ${ad.weight})")
                    return ad
                }
            }
            
            // 如果权重计算失败，随机选择一个
            val ad = availableAds.random()
            currentAd = ad
            lastAdRequestTime = System.currentTimeMillis()
            Log.d("AdManager", "随机选择广告: ${ad.title}")
            ad
            
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
    suspend fun completeAdWatch(userId: String, isCompleted: Boolean = true, skipTime: Long = 0): AdReward? {
        val ad = currentAd ?: return null
        val watchDuration = System.currentTimeMillis() - adWatchStartTime
        val requiredWatchTime = ad.skipTime * 1000L // 转换为毫秒
        
        return try {
            // 检查观看时间是否足够
            val canGetReward = watchDuration >= requiredWatchTime || isCompleted
            
            if (canGetReward) {
                val reward = AdReward(
                    coins = ad.rewardCoins,
                    message = "观看广告奖励 ${ad.rewardCoins} 金币！"
                )
                
                // TODO: 提交到后端验证
                // val request = AdWatchRequest(
                //     userId = userId,
                //     adId = ad.id,
                //     watchDuration = watchDuration,
                //     isCompleted = isCompleted,
                //     skipTime = skipTime,
                //     deviceInfo = getDeviceInfo()
                // )
                // val response = RetrofitClient.getApiService().submitAdWatch("token", request)
                // return RetrofitClient.getResponseData(response)
                
                Log.d("AdManager", "广告观看完成: ${ad.title}, 观看时长: ${watchDuration}ms, 奖励: ${reward.coins} 金币")
                currentAd = null
                reward
            } else {
                Log.w("AdManager", "观看时间不足: ${watchDuration}ms, 需要: ${requiredWatchTime}ms")
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