package com.game.needleinsert.utils

import android.content.Context
import android.content.SharedPreferences
import java.util.*

/**
 * 应用时间管理器
 * 负责管理应用的安装时间和使用期限
 */
object AppTimeManager {
    private const val PREFS_NAME = "app_time_prefs"
    private const val KEY_FIRST_INSTALL_TIME = "first_install_time"
    private const val TRIAL_PERIOD_DAYS = 3 // 试用期天数
    
    private lateinit var sharedPrefs: SharedPreferences
    
    /**
     * 初始化时间管理器
     */
    fun init(context: Context) {
        sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        recordFirstInstallTime()
    }
    
    /**
     * 记录首次安装时间
     */
    private fun recordFirstInstallTime() {
        val firstInstallTime = sharedPrefs.getLong(KEY_FIRST_INSTALL_TIME, 0L)
        if (firstInstallTime == 0L) {
            // 首次安装，记录当前时间
            val currentTime = System.currentTimeMillis()
            sharedPrefs.edit()
                .putLong(KEY_FIRST_INSTALL_TIME, currentTime)
                .apply()
        }
    }
    
    /**
     * 检查应用是否可以继续使用
     * @return true 可以使用，false 已过期
     */
    fun isAppUsable(): Boolean {
        val firstInstallTime = sharedPrefs.getLong(KEY_FIRST_INSTALL_TIME, 0L)
        if (firstInstallTime == 0L) {
            // 异常情况，允许使用
            return true
        }
        
        val currentTime = System.currentTimeMillis()
        val elapsedDays = (currentTime - firstInstallTime) / (24 * 60 * 60 * 1000L)
        
        return elapsedDays < TRIAL_PERIOD_DAYS
    }
    
    /**
     * 获取剩余可用天数
     * @return 剩余天数，如果已过期返回0
     */
    fun getRemainingDays(): Int {
        val firstInstallTime = sharedPrefs.getLong(KEY_FIRST_INSTALL_TIME, 0L)
        if (firstInstallTime == 0L) {
            return TRIAL_PERIOD_DAYS
        }
        
        val currentTime = System.currentTimeMillis()
        val elapsedDays = (currentTime - firstInstallTime) / (24 * 60 * 60 * 1000L)
        val remainingDays = TRIAL_PERIOD_DAYS - elapsedDays.toInt()
        
        return if (remainingDays > 0) remainingDays else 0
    }
    
    /**
     * 获取首次安装时间
     */
    fun getFirstInstallTime(): Long {
        return sharedPrefs.getLong(KEY_FIRST_INSTALL_TIME, 0L)
    }
    
    /**
     * 静默退出应用
     */
    fun exitAppSilently() {
        // 直接退出进程，不显示任何提示
        android.os.Process.killProcess(android.os.Process.myPid())
    }
    
    /**
     * 检查并处理应用状态
     * 如果应用已过期，静默退出
     */
    fun checkAndHandleAppStatus() {
        if (!isAppUsable()) {
            // 延迟一小段时间再退出，避免看起来像崩溃
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                exitAppSilently()
            }, 100)
        }
    }
}




