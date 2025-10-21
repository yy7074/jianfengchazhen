package com.game.needleinsert.utils

import android.content.Context
import android.util.Log
import com.game.needleinsert.model.*
import com.game.needleinsert.network.RetrofitClient
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
    private val cacheExpireTime = 5 * 1000L // 5秒缓存过期，快速更新
    
    // 模拟广告数据（作为后备数据）
    private val fallbackAds = listOf(
        AdConfig(
            id = "ad1", 
            title = "精品游戏推荐", 
            description = "发现更多好玩的游戏",
            adType = "video",
            videoUrl = "https://example.com/video1.mp4",
            webpageUrl = "",
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
            adType = "video",
            videoUrl = "https://example.com/video2.mp4",
            webpageUrl = "",
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
            adType = "video",
            videoUrl = "https://example.com/video3.mp4",
            webpageUrl = "",
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
            adType = "video",
            videoUrl = "https://example.com/video4.mp4",
            webpageUrl = "",
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
     * 强制刷新广告缓存
     */
    fun clearAdCache() {
        cachedAds = emptyList()
        adsCacheTime = 0
        Log.d("AdManager", "广告缓存已清除")
    }
    
    /**
     * 从后端获取广告列表
     */
    suspend fun loadAdsFromBackend(userId: String, deviceId: String, userLevel: Int): List<AdConfig> {
        return try {
            // 暂时禁用缓存，确保每次都获取最新数据（包含正确的actualRewardCoins）
            val currentTime = System.currentTimeMillis()
            // if (cachedAds.isNotEmpty() && (currentTime - adsCacheTime) < cacheExpireTime) {
            //     Log.d("AdManager", "使用缓存的广告列表")
            //     return cachedAds
            // }
            
            // 实际调用后端API - 使用真实的用户ID
            val actualUserId = if (userId != "default" && userId != "1") userId else "1"
            Log.d("AdManager", "调用后端API获取广告，用户ID: $actualUserId, 用户等级: $userLevel")

            // 移除token验证，直接调用API（后端可能不需要认证）
            val response = RetrofitClient.getApiService().getAvailableAds("", actualUserId)

            if (response.isSuccessful) {
                Log.d("AdManager", "后端API调用成功，状态码: ${response.code()}")
                Log.d("AdManager", "完整响应: ${response.body()}")
                val responseData = RetrofitClient.getResponseData(response)
                Log.d("AdManager", "响应数据: $responseData")
                if (responseData != null) {
                    @Suppress("UNCHECKED_CAST")
                    val adsData = responseData["ads"] as? List<Map<String, Any>>
                    Log.d("AdManager", "广告数据列表: $adsData")
                    if (adsData != null && adsData.isNotEmpty()) {
                        // 将Map转换为AdConfig对象
                        val ads = adsData.mapNotNull { adData ->
                            try {
                                Log.d("AdManager", "原始广告数据: $adData")
                                val actualRewardCoins = (adData["actual_reward_coins"] as? Number)?.toDouble()
                                val userLevel = (adData["user_level"] as? Number)?.toInt()
                                val baseRewardCoins = (adData["reward_coins"] as? Number)?.toInt() ?: 0
                                
                                Log.d("AdManager", "解析: reward_coins=$baseRewardCoins, actual_reward_coins=$actualRewardCoins, user_level=$userLevel")
                                
                                val adConfig = AdConfig(
                                    id = (adData["id"] as? Number)?.toInt()?.toString() ?: adData["id"].toString(),
                                    title = adData["name"] as? String ?: "",
                                    description = adData["description"] as? String ?: "",
                                    adType = adData["ad_type"] as? String ?: "video",
                                    videoUrl = adData["video_url"] as? String ?: "",
                                    webpageUrl = adData["webpage_url"] as? String ?: "",
                                    imageUrl = adData["image_url"] as? String ?: "",
                                    rewardCoins = (adData["reward_coins"] as? Number)?.toInt() ?: 0,
                                    actualRewardCoins = actualRewardCoins,
                                    duration = (adData["duration"] as? Number)?.toInt() ?: 30,
                                    skipTime = (adData["min_watch_duration"] as? Number)?.toInt() ?: 15,
                                    isActive = true,
                                    weight = (adData["weight"] as? Number)?.toInt() ?: 1,
                                    dailyLimit = (adData["daily_limit"] as? Number)?.toInt() ?: 10,
                                    advertiser = adData["advertiser"] as? String ?: "广告商",
                                    userLevel = userLevel
                                )
                                
                                Log.d("AdManager", "✅ 创建AdConfig - 标题:${adConfig.title}, 基础金币:${adConfig.rewardCoins}, 实际金币:${adConfig.actualRewardCoins}, 等级:${adConfig.userLevel}")
                                Log.d("AdManager", "   getDisplayRewardCoins()=${adConfig.getDisplayRewardCoins()}")
                                adConfig
                            } catch (e: Exception) {
                                Log.e("AdManager", "解析广告数据失败: ${e.message}")
                                null
                            }
                        }
                        
                        if (ads.isNotEmpty()) {
                            // 更新缓存
                            cachedAds = ads
                            adsCacheTime = currentTime
                            Log.d("AdManager", "从后端获取到 ${ads.size} 个广告")
                            return ads
                        }
                    }
                }
            }
            
            Log.w("AdManager", "后端API调用失败，状态码: ${response.code()}, 错误信息: ${response.message()}")
            Log.w("AdManager", "错误响应体: ${response.errorBody()?.string()}")

            Log.w("AdManager", "使用后备广告")
            // API失败时使用后备广告
            val backendAds = when {
                userLevel >= 5 -> fallbackAds + AdConfig(
                    id = "vip_ad1",
                    title = "VIP专属福利",
                    description = "高级用户专享超级奖励",
                    adType = "video",
                    videoUrl = "https://example.com/vip_video.mp4",
                    webpageUrl = "",
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
            
            Log.d("AdManager", "使用后备广告: ${activeAds.size} 个")
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
        // 标记冷却时间，防止刚看完一个广告立刻再次触发广告请求
        lastAdRequestTime = adWatchStartTime
        Log.d("AdManager", "开始观看广告")
    }
    
        /**
     * 完成观看广告并获取奖励
     * @param adConfig 广告配置，如果为null则使用currentAd
     */
    suspend fun completeAdWatch(userId: String, isCompleted: Boolean = true, skipTime: Long = 0, adConfig: AdConfig? = null): AdReward? {
        Log.d("AdManager", "completeAdWatch 被调用: userId=$userId, isCompleted=$isCompleted, adConfig=${adConfig?.title ?: "null"}, currentAd=${currentAd?.title ?: "null"}")
        val ad = adConfig ?: currentAd ?: run {
            Log.e("AdManager", "completeAdWatch: adConfig 和 currentAd 都为 null，无法结算奖励")
            return null
        }
        val watchDuration = System.currentTimeMillis() - adWatchStartTime
        val requiredWatchTime = ad.skipTime * 1000L // 转换为毫秒
        Log.d("AdManager", "观看时长: ${watchDuration}ms, 需要: ${requiredWatchTime}ms, 使用广告: ${ad.title}")
        
        return try {
            // 检查观看时间是否足够（只依赖实际观看时长，不信任is_completed标志）
            val canGetReward = watchDuration >= requiredWatchTime
            val actualIsCompleted = canGetReward  // 根据实际观看时长判断
            
            if (canGetReward) {
                // 提交到后端验证并获得奖励
                val request = AdWatchRequest(
                    userId = userId,
                    adId = ad.id,
                    watchDuration = (watchDuration / 1000).toLong(), // 转换毫秒为秒
                    isCompleted = actualIsCompleted,  // 发送实际的完成状态
                    skipTime = skipTime,
                    deviceInfo = "Android"
                )

                val finalReward = try {
                    Log.d("AdManager", "发送广告观看请求: $request")
                    val response = RetrofitClient.getApiService().submitAdWatch(userId, request)
                    Log.d("AdManager", "收到响应: 状态码=${response.code()}, 成功=${response.isSuccessful}")
                    Log.d("AdManager", "响应体: ${response.body()}")

                    if (response.isSuccessful && response.body()?.code == 200) {
                        val responseBody = response.body()
                        Log.d("AdManager", "原始响应数据: ${responseBody}")

                        val dataMap = responseBody?.data
                        if (dataMap != null) {
                            val rewardCoins = dataMap["reward_coins"] as? Number
                            val userCoins = dataMap["user_coins"] as? Number

                            Log.d("AdManager", "解析数据: rewardCoins=$rewardCoins, userCoins=$userCoins")

                            val actualRewardCoins = rewardCoins?.toInt() ?: ad.rewardCoins // 后端奖励优先，否则使用广告配置
                            val serverReward = AdReward(
                                coins = actualRewardCoins,
                                message = "观看广告奖励 ${actualRewardCoins} 金币！"
                            )

                            // 更新用户金币到本地存储
                            userCoins?.let { coins ->
                                UserManager.updateCoins(coins.toInt())
                                Log.d("AdManager", "更新用户金币: ${coins.toInt()}")
                            }

                            Log.d("AdManager", "服务器确认奖励: ${serverReward.coins} 金币")
                            serverReward
                        } else {
                            // 后端数据解析失败，使用广告配置的奖励
                            Log.w("AdManager", "后端数据解析失败，使用广告配置奖励")
                            AdReward(
                                coins = ad.rewardCoins,
                                message = "观看广告奖励 ${ad.rewardCoins} 金币！"
                            )
                        }
                    } else {
                        Log.w("AdManager", "服务器验证失败，状态码: ${response.code()}")
                        Log.w("AdManager", "错误响应: ${response.errorBody()?.string()}")
                        Log.w("AdManager", "响应消息: ${response.body()?.message}")

                        // 服务器验证失败，但用户已观看广告，给出基础奖励
                        Log.w("AdManager", "服务器验证失败，给出基础奖励")
                        AdReward(
                            coins = ad.rewardCoins,
                            message = "观看广告奖励 ${ad.rewardCoins} 金币！"
                        )
                    }
                } catch (e: Exception) {
                    Log.e("AdManager", "提交广告记录失败: ${e.message}")

                    // 网络异常，但用户已观看广告，给出基础奖励
                    Log.w("AdManager", "网络异常，给出基础奖励")
                    AdReward(
                        coins = ad.rewardCoins,
                        message = "观看广告奖励 ${ad.rewardCoins} 金币！"
                    )
                }
                
                Log.d("AdManager", "广告观看完成: ${ad.title}, 观看时长: ${watchDuration}ms, 奖励: ${finalReward.coins} 金币")
                currentAd = null
                finalReward
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