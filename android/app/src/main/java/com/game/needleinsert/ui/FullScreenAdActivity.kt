package com.game.needleinsert.ui

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowCompat
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.game.needleinsert.model.AdConfig
import com.game.needleinsert.ui.theme.NeedleInsertTheme
import com.game.needleinsert.ui.theme.GameColors
import com.game.needleinsert.ui.components.AnimatedBackground
import com.game.needleinsert.ui.components.VideoAdPlayer
import com.game.needleinsert.ui.components.WebpageAdPlayer
import com.game.needleinsert.utils.AdManager
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope

class FullScreenAdActivity : ComponentActivity() {
    
    companion object {
        const val EXTRA_AD_CONFIG = "ad_config"
        const val RESULT_AD_COMPLETED = "ad_completed"
        const val RESULT_AD_SKIPPED = "ad_skipped"
        const val RESULT_AD_COINS = "ad_coins"
        const val RESULT_AD_MESSAGE = "ad_message"
        
        fun startForResult(context: Context, adConfig: AdConfig, requestCode: Int) {
            val intent = Intent(context, FullScreenAdActivity::class.java).apply {
                putExtra(EXTRA_AD_CONFIG, adConfig)
            }
            if (context is Activity) {
                context.startActivityForResult(intent, requestCode)
            }
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 获取广告配置
        val adConfig = intent.getSerializableExtra(EXTRA_AD_CONFIG) as? AdConfig
        if (adConfig == null) {
            finish()
            return
        }
        
        setContent {
            NeedleInsertTheme {
                FullScreenAdPlayer(
                    adConfig = adConfig,
                    onAdCompleted = { coins, message ->
                        setResult(RESULT_OK, Intent().apply {
                            putExtra(RESULT_AD_COMPLETED, true)
                            putExtra(RESULT_AD_COINS, coins)
                            putExtra(RESULT_AD_MESSAGE, message)
                        })
                        finish()
                    },
                    onAdSkipped = { coins, message ->
                        setResult(RESULT_OK, Intent().apply {
                            putExtra(RESULT_AD_COMPLETED, false)
                            putExtra(RESULT_AD_COINS, coins)
                            putExtra(RESULT_AD_MESSAGE, message)
                        })
                        finish()
                    },
                    onAdCancelled = {
                        setResult(RESULT_CANCELED)
                        finish()
                    }
                )
            }
        }
    }
    
    private fun setupFullscreen() {
        try {
            // 启用沉浸式全屏模式
            WindowCompat.setDecorFitsSystemWindows(window, false)
            
            // 隐藏系统UI
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
                window.insetsController?.let { controller ->
                    controller.hide(WindowInsets.Type.systemBars())
                    controller.systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                }
            } else {
                @Suppress("DEPRECATION")
                window.decorView.systemUiVisibility = (
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_FULLSCREEN
                )
            }
            
            // 强制全屏标志
            window.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
            window.addFlags(WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS)
            
            // 保持屏幕常亮
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            
            // 设置亮度为最大
            val layoutParams = window.attributes
            layoutParams.screenBrightness = 1.0f
            window.attributes = layoutParams
            
            // 设置状态栏和导航栏透明
            window.statusBarColor = android.graphics.Color.TRANSPARENT
            window.navigationBarColor = android.graphics.Color.TRANSPARENT
        } catch (e: Exception) {
            // 如果全屏设置失败，至少设置基本的全屏标志
            window.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }
    }
    
    override fun onResume() {
        super.onResume()
        setupFullscreen()
    }
    
    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) {
            setupFullscreen()
        }
    }
}

@Composable
fun FullScreenAdPlayer(
    adConfig: AdConfig,
    onAdCompleted: (Int, String) -> Unit,
    onAdSkipped: (Int, String) -> Unit,
    onAdCancelled: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    
    // 根据广告类型显示不同的界面
    when (adConfig.adType) {
        "webpage" -> {
            WebpageAdPlayer(
                adConfig = adConfig,
                onAdStarted = {
                    // 广告开始播放时记录开始时间
                    AdManager.startWatchingAd()
                },
                onAdCompleted = { isCompleted ->
                    coroutineScope.launch {
                        val reward = AdManager.completeAdWatch("9", isCompleted)
                        if (reward != null) {
                            if (isCompleted) {
                                onAdCompleted(reward.coins, reward.message ?: "观看完成")
                            } else {
                                onAdSkipped(reward.coins, reward.message ?: "观看完成")
                            }
                        } else {
                            onAdCancelled()
                        }
                    }
                },
                onAdClosed = { onAdCancelled() },
                modifier = Modifier.fillMaxSize()
            )
        }
        else -> {
            // 使用真实的视频播放器
            VideoAdPlayer(
                videoUrl = adConfig.videoUrl,
                duration = adConfig.duration,
                skipTime = adConfig.skipTime,
                rewardCoins = adConfig.rewardCoins,
                advertiser = adConfig.advertiser.ifEmpty { "广告商" },
                onAdStarted = {
                    // 广告开始播放时记录开始时间
                    AdManager.startWatchingAd()
                },
                onAdCompleted = { isCompleted ->
                    coroutineScope.launch {
                        val reward = AdManager.completeAdWatch("9", isCompleted)
                        if (reward != null) {
                            if (isCompleted) {
                                onAdCompleted(reward.coins, reward.message ?: "观看完成")
                            } else {
                                onAdSkipped(reward.coins, reward.message ?: "观看完成")
                            }
                        } else {
                            onAdCancelled()
                        }
                    }
                },
                onAdClosed = {
                    onAdCancelled()
                },
                modifier = Modifier.fillMaxSize()
            )
        }
    }
}

 