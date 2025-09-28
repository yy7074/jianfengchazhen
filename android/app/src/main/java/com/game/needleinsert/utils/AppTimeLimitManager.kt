package com.game.needleinsert.utils

import android.content.Context
import android.content.SharedPreferences
import com.game.needleinsert.config.AppConfig

/**
 * 应用时间限制管理器
 * 用于管理首次安装后的时间限制功能
 */
object AppTimeLimitManager {
    
    private const val PREFS_NAME = "app_time_limit_prefs"
    private const val KEY_FIRST_INSTALL_TIME = "first_install_time"
    private const val KEY_TIME_LIMIT_SECONDS = "time_limit_seconds"
    private const val KEY_IS_TIME_LIMIT_ENABLED = "is_time_limit_enabled"
    
    // 从配置文件获取默认时间限制
    private val DEFAULT_TIME_LIMIT_SECONDS = AppConfig.TimeLimits.DEFAULT_TRIAL_PERIOD_SECONDS
    
    private lateinit var prefs: SharedPreferences
    
    /**
     * 初始化时间限制管理器
     */
    fun init(context: Context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        
        // 如果是首次启动，记录安装时间
        if (!prefs.contains(KEY_FIRST_INSTALL_TIME)) {
            val currentTime = System.currentTimeMillis() / 1000 // 转换为秒
            prefs.edit()
                .putLong(KEY_FIRST_INSTALL_TIME, currentTime)
                .putLong(KEY_TIME_LIMIT_SECONDS, DEFAULT_TIME_LIMIT_SECONDS)
                .putBoolean(KEY_IS_TIME_LIMIT_ENABLED, AppConfig.getEffectiveTimeLimitEnabled())
                .apply()
        }
    }
    
    /**
     * 检查是否已超过时间限制
     * @return true 如果超过限制，false 如果在限制内
     */
    fun isTimeLimitExceeded(): Boolean {
        if (!isTimeLimitEnabled()) {
            return false
        }
        
        val firstInstallTime = getFirstInstallTime()
        val timeLimitSeconds = getTimeLimitSeconds()
        val currentTime = System.currentTimeMillis() / 1000
        
        return (currentTime - firstInstallTime) > timeLimitSeconds
    }
    
    /**
     * 获取首次安装时间（秒）
     */
    fun getFirstInstallTime(): Long {
        return prefs.getLong(KEY_FIRST_INSTALL_TIME, 0L)
    }
    
    /**
     * 获取时间限制（秒）
     */
    fun getTimeLimitSeconds(): Long {
        return prefs.getLong(KEY_TIME_LIMIT_SECONDS, DEFAULT_TIME_LIMIT_SECONDS)
    }
    
    /**
     * 设置时间限制（秒）
     */
    fun setTimeLimitSeconds(seconds: Long) {
        prefs.edit()
            .putLong(KEY_TIME_LIMIT_SECONDS, seconds)
            .apply()
    }
    
    /**
     * 检查时间限制是否启用
     */
    fun isTimeLimitEnabled(): Boolean {
        return prefs.getBoolean(KEY_IS_TIME_LIMIT_ENABLED, AppConfig.getEffectiveTimeLimitEnabled())
    }
    
    /**
     * 设置时间限制启用状态
     */
    fun setTimeLimitEnabled(enabled: Boolean) {
        prefs.edit()
            .putBoolean(KEY_IS_TIME_LIMIT_ENABLED, enabled)
            .apply()
    }
    
    /**
     * 获取剩余时间（秒）
     * @return 剩余秒数，如果已超时返回0
     */
    fun getRemainingTimeSeconds(): Long {
        if (!isTimeLimitEnabled()) {
            return Long.MAX_VALUE
        }
        
        val firstInstallTime = getFirstInstallTime()
        val timeLimitSeconds = getTimeLimitSeconds()
        val currentTime = System.currentTimeMillis() / 1000
        val elapsedTime = currentTime - firstInstallTime
        
        return maxOf(0L, timeLimitSeconds - elapsedTime)
    }
    
    /**
     * 获取剩余时间的友好显示文本
     */
    fun getRemainingTimeText(): String {
        val remainingSeconds = getRemainingTimeSeconds()
        
        if (remainingSeconds == Long.MAX_VALUE) {
            return "无限制"
        }
        
        if (remainingSeconds <= 0) {
            return "已过期"
        }
        
        val days = remainingSeconds / (24 * 60 * 60)
        val hours = (remainingSeconds % (24 * 60 * 60)) / (60 * 60)
        val minutes = (remainingSeconds % (60 * 60)) / 60
        val seconds = remainingSeconds % 60
        
        return when {
            days > 0 -> "${days}天${hours}小时"
            hours > 0 -> "${hours}小时${minutes}分钟"
            minutes > 0 -> "${minutes}分钟${seconds}秒"
            else -> "${seconds}秒"
        }
    }
    
    /**
     * 重置首次安装时间（调试用）
     */
    fun resetInstallTime() {
        val currentTime = System.currentTimeMillis() / 1000
        prefs.edit()
            .putLong(KEY_FIRST_INSTALL_TIME, currentTime)
            .apply()
    }
    
    /**
     * 清除所有时间限制数据（调试用）
     */
    fun clearAllData() {
        prefs.edit().clear().apply()
    }
    
    /**
     * 强制触发时间限制（调试用）
     * 将首次安装时间设置为很久以前
     */
    fun forceTimeLimit() {
        val pastTime = System.currentTimeMillis() / 1000 - getTimeLimitSeconds() - 1
        prefs.edit()
            .putLong(KEY_FIRST_INSTALL_TIME, pastTime)
            .apply()
    }
    
    /**
     * 获取安装时间的友好显示（调试用）
     */
    fun getInstallTimeInfo(): String {
        val firstInstallTime = getFirstInstallTime()
        val currentTime = System.currentTimeMillis() / 1000
        val elapsedTime = currentTime - firstInstallTime
        val remainingTime = getRemainingTimeSeconds()
        
        return "安装时间: $firstInstallTime, 已用时: ${elapsedTime}秒, 剩余: ${remainingTime}秒"
    }
}
