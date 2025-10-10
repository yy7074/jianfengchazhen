package com.game.needleinsert.config

/**
 * 应用配置类
 * 包含应用的各种配置参数
 */
object AppConfig {
    
    /**
     * 时间限制配置
     */
    object TimeLimits {
        // 默认试用期：7天 (7 * 24 * 60 * 60 = 6048000秒)
        const val DEFAULT_TRIAL_PERIOD_SECONDS = 6048000L
        
        // 开发者联系方式
        const val DEVELOPER_EMAIL = "developer@example.com"
        const val DEVELOPER_WECHAT = "your_wechat_id"
        const val DEVELOPER_QQ = "your_qq_number"
        
        // 是否启用时间限制（发布版本设为true，开发版本可设为false）
        const val ENABLE_TIME_LIMIT = true
        
        // 预设的时间限制选项（秒）
        val PRESET_TIME_LIMITS = mapOf(
            "1小时" to 3600L,
            "1天" to 86400L,
            "3天" to 259200L,
            "7天" to 604800L,
            "30天" to 2592000L,
            "无限制" to Long.MAX_VALUE
        )
    }
    
    /**
     * 应用信息配置
     */
    object AppInfo {
        const val APP_NAME = "见缝插针"
        const val VERSION = "1.0.0"
        const val BUILD_TYPE = "debug" // "debug" or "release"
    }
    
    /**
     * 游戏配置
     */
    object Game {
        // 游戏相关配置可以添加在这里
        const val DEFAULT_COINS_PER_AD = 10
        const val MIN_WITHDRAWAL_AMOUNT = 100
    }
    
    /**
     * 网络配置
     */
    object Network {
        // const val BASE_URL = "http://8.137.103.175:3001/"
        const val BASE_URL = "https://8089.dachaonet.com"
        const val CONNECTION_TIMEOUT = 30L // 秒
        const val READ_TIMEOUT = 30L // 秒
    }
    
    /**
     * 根据构建类型判断是否为调试模式
     */
    fun isDebugMode(): Boolean {
        return AppInfo.BUILD_TYPE == "debug"
    }
    
    /**
     * 获取实际的时间限制设置
     * 为了测试功能，即使在调试模式下也启用时间限制
     */
    fun getEffectiveTimeLimitEnabled(): Boolean {
        return TimeLimits.ENABLE_TIME_LIMIT // 总是使用配置的设置，不区分调试/发布模式
    }
}
