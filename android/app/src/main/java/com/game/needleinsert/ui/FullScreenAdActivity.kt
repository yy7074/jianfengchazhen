package com.game.needleinsert.ui

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
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
}

@Composable
fun FullScreenAdPlayer(
    adConfig: AdConfig,
    onAdCompleted: (Int, String) -> Unit,
    onAdSkipped: (Int, String) -> Unit,
    onAdCancelled: () -> Unit
) {
    var currentProgress by remember { mutableStateOf(0) }
    var isPlaying by remember { mutableStateOf(false) }
    var canSkip by remember { mutableStateOf(false) }
    var showCloseConfirm by remember { mutableStateOf(false) }
    
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    // 广告播放逻辑
    LaunchedEffect(isPlaying) {
        if (isPlaying) {
            AdManager.startWatchingAd()
            
            // 模拟视频播放进度
            repeat(adConfig.duration) { second ->
                delay(1000)
                currentProgress = second + 1
                
                // 检查是否可以跳过
                if (currentProgress >= adConfig.skipTime) {
                    canSkip = true
                }
                
                // 播放完成
                if (currentProgress >= adConfig.duration) {
                    val reward = AdManager.completeAdWatch("user_id", true)
                    if (reward != null) {
                        onAdCompleted(reward.coins, reward.message)
                    } else {
                        onAdCancelled()
                    }
                    return@repeat
                }
            }
        }
    }
    
    // 全屏广告界面 - 使用动画背景
    AnimatedBackground(
        modifier = Modifier.fillMaxSize(),
        particleCount = 100
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.radialGradient(
                        colors = listOf(
                            Color.Black.copy(alpha = 0.7f),
                            Color.Transparent
                        )
                    )
                )
        ) {
        // 广告内容区域
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // 广告标题
            Text(
                text = adConfig.title,
                color = Color.White,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // 广告描述
            Text(
                text = adConfig.description,
                color = Color.White.copy(alpha = 0.8f),
                fontSize = 16.sp
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // 模拟视频播放区域
            Box(
                modifier = Modifier
                    .fillMaxWidth(0.9f)
                    .aspectRatio(16f / 9f)
                    .background(Color.Gray, RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                if (!isPlaying) {
                    // 播放按钮
                    Button(
                        onClick = { isPlaying = true },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF4CAF50)
                        )
                    ) {
                        Text("▶ 开始播放广告", fontSize = 18.sp)
                    }
                } else {
                    // 播放中界面
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "🎬",
                            fontSize = 64.sp,
                            color = Color.White
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Text(
                            text = "${adConfig.advertiser}",
                            color = Color.White,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(24.dp))
                        
                        // 进度条
                        LinearProgressIndicator(
                            progress = currentProgress.toFloat() / adConfig.duration,
                            modifier = Modifier
                                .fillMaxWidth(0.8f)
                                .height(8.dp),
                            color = Color(0xFF4CAF50)
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            text = "${currentProgress}/${adConfig.duration}秒",
                            color = Color.White,
                            fontSize = 14.sp
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // 奖励信息
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF4CAF50).copy(alpha = 0.2f)
                ),
                modifier = Modifier.padding(horizontal = 32.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "🎁 观看奖励",
                        color = Color.White,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "💰 ${adConfig.rewardCoins} 金币",
                        color = Color(0xFFFFD700),
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                    
                    if (isPlaying && !canSkip) {
                        Text(
                            text = "${adConfig.skipTime - currentProgress}秒后可跳过",
                            color = Color.White.copy(alpha = 0.7f),
                            fontSize = 12.sp
                        )
                    }
                }
            }
        }
        
        // 顶部关闭按钮
        if (!isPlaying) {
            IconButton(
                onClick = { showCloseConfirm = true },
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            ) {
                Text(
                    text = "✕",
                    color = Color.White,
                    fontSize = 24.sp
                )
            }
        }
        
        // 底部跳过按钮
        if (isPlaying && canSkip) {
            Row(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(32.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Button(
                    onClick = {
                        coroutineScope.launch {
                            val reward = AdManager.completeAdWatch("user_id", false, currentProgress * 1000L)
                            if (reward != null) {
                                onAdSkipped(reward.coins, reward.message)
                            } else {
                                onAdCancelled()
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.Gray
                    )
                ) {
                    Text("跳过广告")
                }
                
                Button(
                    onClick = {
                        // 继续观看到结束
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    )
                ) {
                    Text("继续观看")
                }
            }
        }
    }
    
    // 关闭确认对话框
    if (showCloseConfirm) {
        AlertDialog(
            onDismissRequest = { showCloseConfirm = false },
            title = {
                Text("确认关闭")
            },
            text = {
                Text("关闭广告将无法获得 ${adConfig.rewardCoins} 金币奖励")
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showCloseConfirm = false
                        onAdCancelled()
                    }
                ) {
                    Text("确认关闭")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showCloseConfirm = false }
                ) {
                    Text("继续观看")
                }
            }
        )
    }
    }
} 