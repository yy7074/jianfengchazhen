package com.game.needleinsert.utils

import android.content.Context
import android.util.Log
import com.game.needleinsert.model.AppConfig
import com.game.needleinsert.network.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * 应用配置管理器
 * 负责从后端获取和缓存应用配置信息
 */
object ConfigManager {
    private const val TAG = "ConfigManager"
    private const val PREFS_NAME = "app_config"
    private const val KEY_MIN_WITHDRAW_AMOUNT = "min_withdraw_amount"
    private const val KEY_MAX_WITHDRAW_AMOUNT = "max_withdraw_amount"
    private const val KEY_COIN_TO_RMB_RATE = "coin_to_rmb_rate"
    private const val KEY_WITHDRAWAL_FEE_RATE = "withdrawal_fee_rate"
    private const val KEY_DAILY_WITHDRAW_LIMIT = "daily_withdraw_limit"
    private const val KEY_LAST_UPDATE_TIME = "last_update_time"
    
    // 缓存更新间隔（毫秒）- 1小时
    private const val CACHE_EXPIRE_TIME = 60 * 60 * 1000L
    
    // 默认配置值（与后端保持一致）
    private const val DEFAULT_MIN_WITHDRAW_AMOUNT = 10.0
    private const val DEFAULT_MAX_WITHDRAW_AMOUNT = 500.0
    private const val DEFAULT_COIN_TO_RMB_RATE = 3300
    private const val DEFAULT_WITHDRAWAL_FEE_RATE = 0.0
    private const val DEFAULT_DAILY_WITHDRAW_LIMIT = 1
    
    private var cachedConfig: AppConfig? = null
    
    /**
     * 获取最小提现金额
     */
    suspend fun getMinWithdrawAmount(context: Context): Double {
        val config = getAppConfig(context)
        return config?.minWithdrawAmount ?: DEFAULT_MIN_WITHDRAW_AMOUNT
    }
    
    /**
     * 获取最大提现金额
     */
    suspend fun getMaxWithdrawAmount(context: Context): Double {
        val config = getAppConfig(context)
        return config?.maxWithdrawAmount ?: DEFAULT_MAX_WITHDRAW_AMOUNT
    }
    
    /**
     * 获取金币兑换人民币比率
     */
    suspend fun getCoinToRmbRate(context: Context): Int {
        val config = getAppConfig(context)
        return config?.coinToRmbRate ?: DEFAULT_COIN_TO_RMB_RATE
    }
    
    /**
     * 获取提现手续费率
     */
    suspend fun getWithdrawalFeeRate(context: Context): Double {
        val config = getAppConfig(context)
        return config?.withdrawalFeeRate ?: DEFAULT_WITHDRAWAL_FEE_RATE
    }
    
    /**
     * 获取每日提现次数限制
     */
    suspend fun getDailyWithdrawLimit(context: Context): Int {
        val config = getAppConfig(context)
        return config?.dailyWithdrawLimit ?: DEFAULT_DAILY_WITHDRAW_LIMIT
    }
    
    /**
     * 获取应用配置
     * 优先使用缓存，缓存过期时从服务器获取
     */
    suspend fun getAppConfig(context: Context): AppConfig? {
        return withContext(Dispatchers.IO) {
            try {
                // 检查缓存是否有效
                if (isCacheValid(context)) {
                    Log.d(TAG, "使用缓存的配置")
                    return@withContext getCachedConfig(context)
                }
                
                // 从服务器获取配置
                Log.d(TAG, "从服务器获取配置")
                val config = fetchConfigFromServer()
                
                if (config != null) {
                    // 缓存配置
                    cacheConfig(context, config)
                    cachedConfig = config
                    Log.d(TAG, "配置获取成功并已缓存")
                    return@withContext config
                } else {
                    // 服务器获取失败，使用本地缓存
                    Log.w(TAG, "服务器获取配置失败，使用本地缓存")
                    return@withContext getCachedConfig(context)
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "获取应用配置失败", e)
                return@withContext getCachedConfig(context)
            }
        }
    }
    
    /**
     * 清除本地缓存
     */
    fun clearCache(context: Context) {
        try {
            Log.d(TAG, "清除配置缓存")
            val sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            sharedPrefs.edit().clear().apply()
            cachedConfig = null
            Log.d(TAG, "配置缓存已清除")
        } catch (e: Exception) {
            Log.e(TAG, "清除缓存失败", e)
        }
    }
    
    /**
     * 强制刷新配置
     */
    suspend fun refreshConfig(context: Context): AppConfig? {
        return withContext(Dispatchers.IO) {
            try {
                Log.d(TAG, "强制刷新配置")
                val config = fetchConfigFromServer()
                
                if (config != null) {
                    cacheConfig(context, config)
                    cachedConfig = config
                    Log.d(TAG, "配置刷新成功")
                }
                
                return@withContext config
                
            } catch (e: Exception) {
                Log.e(TAG, "刷新配置失败", e)
                return@withContext null
            }
        }
    }
    
    /**
     * 从服务器获取配置
     */
    private suspend fun fetchConfigFromServer(): AppConfig? {
        return try {
            val apiService = RetrofitClient.getApiService()
            val response = apiService.getAppConfig()
            
            if (response.isSuccessful) {
                val baseResponse = response.body()
                if (baseResponse?.code == 200) {
                    baseResponse.data
                } else {
                    Log.e(TAG, "服务器返回错误: ${baseResponse?.message}")
                    null
                }
            } else {
                Log.e(TAG, "HTTP请求失败: ${response.code()}")
                null
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "网络请求异常", e)
            null
        }
    }
    
    /**
     * 检查缓存是否有效
     */
    private fun isCacheValid(context: Context): Boolean {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val lastUpdateTime = prefs.getLong(KEY_LAST_UPDATE_TIME, 0)
        val currentTime = System.currentTimeMillis()
        
        return (currentTime - lastUpdateTime) < CACHE_EXPIRE_TIME && cachedConfig != null
    }
    
    /**
     * 获取缓存的配置
     */
    private fun getCachedConfig(context: Context): AppConfig? {
        if (cachedConfig != null) {
            return cachedConfig
        }
        
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        
        return try {
            AppConfig(
                minWithdrawAmount = prefs.getFloat(KEY_MIN_WITHDRAW_AMOUNT, DEFAULT_MIN_WITHDRAW_AMOUNT.toFloat()).toDouble(),
                maxWithdrawAmount = prefs.getFloat(KEY_MAX_WITHDRAW_AMOUNT, DEFAULT_MAX_WITHDRAW_AMOUNT.toFloat()).toDouble(),
                coinToRmbRate = prefs.getInt(KEY_COIN_TO_RMB_RATE, DEFAULT_COIN_TO_RMB_RATE),
                withdrawalFeeRate = prefs.getFloat(KEY_WITHDRAWAL_FEE_RATE, DEFAULT_WITHDRAWAL_FEE_RATE.toFloat()).toDouble(),
                dailyWithdrawLimit = prefs.getInt(KEY_DAILY_WITHDRAW_LIMIT, DEFAULT_DAILY_WITHDRAW_LIMIT)
            ).also {
                cachedConfig = it
            }
        } catch (e: Exception) {
            Log.e(TAG, "读取缓存配置失败", e)
            null
        }
    }
    
    /**
     * 缓存配置到本地
     */
    private fun cacheConfig(context: Context, config: AppConfig) {
        try {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().apply {
                putFloat(KEY_MIN_WITHDRAW_AMOUNT, config.minWithdrawAmount.toFloat())
                putFloat(KEY_MAX_WITHDRAW_AMOUNT, config.maxWithdrawAmount.toFloat())
                putInt(KEY_COIN_TO_RMB_RATE, config.coinToRmbRate)
                putFloat(KEY_WITHDRAWAL_FEE_RATE, config.withdrawalFeeRate.toFloat())
                putInt(KEY_DAILY_WITHDRAW_LIMIT, config.dailyWithdrawLimit)
                putLong(KEY_LAST_UPDATE_TIME, System.currentTimeMillis())
                apply()
            }
            Log.d(TAG, "配置已缓存到本地")
        } catch (e: Exception) {
            Log.e(TAG, "缓存配置失败", e)
        }
    }
}
