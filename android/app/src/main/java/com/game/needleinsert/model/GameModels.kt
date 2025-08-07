package com.game.needleinsert.model

import com.google.gson.annotations.SerializedName
import kotlin.math.cos
import kotlin.math.sin

// 针的数据模型
data class Needle(
    val id: Int,
    val angle: Float,  // 角度(弧度)
    val radius: Float = 150f,  // 距离圆心的距离
    var isInserted: Boolean = false,
    val color: androidx.compose.ui.graphics.Color = androidx.compose.ui.graphics.Color(0xFF00d4aa),
    val number: Int = id  // 针上显示的数字
) {
    // 计算针尖位置
    fun getTipPosition(centerX: Float, centerY: Float): Pair<Float, Float> {
        val x = centerX + cos(angle) * radius
        val y = centerY + sin(angle) * radius
        return Pair(x, y)
    }
    
    // 计算针尾位置
    fun getTailPosition(centerX: Float, centerY: Float): Pair<Float, Float> {
        val needleLength = 80f
        val x = centerX + cos(angle) * (radius - needleLength)
        val y = centerY + sin(angle) * (radius - needleLength)
        return Pair(x, y)
    }
}

// 游戏状态
enum class GameState {
    READY,      // 准备状态
    PLAYING,    // 游戏中
    GAME_OVER,  // 游戏结束
    PAUSED      // 暂停
}

// 游戏关卡
data class GameLevel(
    val level: Int,
    val needleCount: Int,      // 需要插入的针数
    val rotationSpeed: Float,  // 旋转速度
    val obstacles: Int = 0,    // 障碍物数量
    val levelType: LevelType = LevelType.NORMAL,  // 关卡类型
    val description: String = ""  // 关卡描述
)

// 关卡类型
enum class LevelType {
    NORMAL,      // 普通关卡
    SPEED,       // 高速旋转
    REVERSE,     // 反向旋转
    RANDOM,      // 随机速度变化
    OBSTACLE,    // 有障碍物
    LARGE,       // 大量针
    PRECISION    // 精确插入
}

// 游戏数据
data class GameData(
    val level: Int = 1,
    val score: Int = 0,
    val needlesInserted: Int = 0,
    val needlesRequired: Int = 10,
    val rotationSpeed: Float = 1f,
    val state: GameState = GameState.READY,
    val currentLevelType: LevelType = LevelType.NORMAL,
    val needleQueue: List<Int> = emptyList(),  // 待发射的针队列
    val isReversed: Boolean = false,  // 是否反向旋转
    val coins: Int = 0,  // 用户金币
    val canShowAd: Boolean = false,  // 是否可以显示广告
    val adState: AdState = AdState.NONE  // 广告状态
)

// API相关模型
data class User(
    @SerializedName("id") val id: String = "",
    @SerializedName("device_id") val deviceId: String = "",
    @SerializedName("nickname") val nickname: String = "",
    @SerializedName("coins") val coins: Int = 0,
    @SerializedName("level") val level: Int = 1,
    @SerializedName("total_score") val totalScore: Int = 0
)

data class UserRegister(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("nickname") val nickname: String = "玩家${System.currentTimeMillis() % 10000}"
)

data class UserLogin(
    @SerializedName("device_id") val deviceId: String
)

data class GameResultSubmit(
    @SerializedName("user_id") val userId: String,
    @SerializedName("level") val level: Int,
    @SerializedName("score") val score: Int,
    @SerializedName("needles_inserted") val needlesInserted: Int,
    @SerializedName("game_duration") val gameDuration: Long
)

data class AdConfig(
    @SerializedName("id") val id: String,
    @SerializedName("title") val title: String,
    @SerializedName("video_url") val videoUrl: String,
    @SerializedName("image_url") val imageUrl: String,
    @SerializedName("reward_coins") val rewardCoins: Int
)

data class AdWatchRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("ad_id") val adId: String,
    @SerializedName("watch_duration") val watchDuration: Long
)

data class AdReward(
    @SerializedName("coins") val coins: Int,
    @SerializedName("message") val message: String
)

// 广告观看状态
enum class AdState {
    NONE,        // 无广告
    LOADING,     // 加载中
    READY,       // 准备播放
    PLAYING,     // 播放中
    COMPLETED,   // 播放完成
    FAILED       // 播放失败
}

data class BaseResponse<T>(
    @SerializedName("code") val code: Int,
    @SerializedName("message") val message: String,
    @SerializedName("data") val data: T? = null
) 