package com.game.needleinsert.ui.components

import android.app.Activity
import android.content.Context
import android.net.Uri
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.zIndex
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun VideoAdPlayer(
    videoUrl: String,
    duration: Int,
    skipTime: Int,
    rewardCoins: Int,
    advertiser: String,
    onAdStarted: () -> Unit = {},
    onAdCompleted: (Boolean) -> Unit, // 参数表示是否完整观看
    onAdClosed: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    var exoPlayer by remember { mutableStateOf<ExoPlayer?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var currentProgress by remember { mutableStateOf(0) }
    var canSkip by remember { mutableStateOf(false) }
    var showCloseDialog by remember { mutableStateOf(false) }
    var showControls by remember { mutableStateOf(true) }
    var isVideoReady by remember { mutableStateOf(false) }
    var hasError by remember { mutableStateOf(false) }
    var adCompleted by remember { mutableStateOf(false) } // 防止重复调用
    
    // 初始化ExoPlayer
    LaunchedEffect(videoUrl) {
        try {
            val player = ExoPlayer.Builder(context).build()
            val mediaItem = MediaItem.fromUri(Uri.parse(videoUrl))
            player.setMediaItem(mediaItem)
            player.prepare()
            
            // 添加播放器监听器
            player.addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(state: Int) {
                    when (state) {
                        Player.STATE_READY -> {
                            isVideoReady = true
                            hasError = false
                            // 视频准备好后自动开始播放
                            if (!isPlaying) {
                                player.play()
                                isPlaying = true
                                onAdStarted()
                            }
                        }
                        Player.STATE_ENDED -> {
                            if (!adCompleted) {
                                adCompleted = true
                                onAdCompleted(true)
                            }
                        }
                        Player.STATE_IDLE -> {}
                        Player.STATE_BUFFERING -> {}
                    }
                }
                
                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    hasError = true
                }
            })
            
            exoPlayer = player
        } catch (e: Exception) {
            hasError = true
        }
    }
    
    // 清理资源
    DisposableEffect(Unit) {
        onDispose {
            exoPlayer?.release()
        }
    }
    
    // 进度计时器
    LaunchedEffect(isPlaying) {
        while (isPlaying && currentProgress < duration) {
            delay(1000)
            currentProgress++
            
            if (currentProgress >= skipTime && !canSkip) {
                canSkip = true
            }
            
            // 隐藏控制栏（但在可跳过时显示）
            if (currentProgress > 3 && !canSkip) {
                showControls = false
            }
        }
    }
    
    // 自动隐藏控制栏
    LaunchedEffect(showControls) {
        if (showControls && isPlaying && !canSkip) {
            delay(3000) // 3秒后自动隐藏
            showControls = false
        }
    }
    
    // 全屏视频播放界面
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Color.Black)
            .clickable { showControls = !showControls }
    ) {
        if (hasError) {
            // 错误状态
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "😞",
                    fontSize = 64.sp,
                    color = Color.White
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "视频加载失败",
                    color = Color.White,
                    fontSize = 18.sp
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                Button(
                    onClick = { onAdClosed() },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    )
                ) {
                    Text("返回游戏")
                }
            }
        } else {
            // 视频播放器
            exoPlayer?.let { player ->
                AndroidView(
                    factory = { ctx ->
                        PlayerView(ctx).apply {
                            this.player = player
                            useController = false // 使用自定义控制器
                            resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_ZOOM // 缩放填充整个屏幕
                            
                            // 确保完全填充屏幕
                            layoutParams = FrameLayout.LayoutParams(
                                ViewGroup.LayoutParams.MATCH_PARENT,
                                ViewGroup.LayoutParams.MATCH_PARENT
                            )
                            
                            // 设置背景色为黑色
                            setBackgroundColor(android.graphics.Color.BLACK)
                            
                            // 禁用默认控制器
                            controllerAutoShow = false
                            controllerHideOnTouch = true
                        }
                    },
                    modifier = Modifier.fillMaxSize()
                )
            }
            
            // 如果视频还没准备好，显示加载界面
            if (!isVideoReady) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator(
                            color = Color(0xFF4CAF50)
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Text(
                            text = "正在加载广告视频...",
                            color = Color.White,
                            fontSize = 16.sp
                        )
                    }
                }
            }
            
            // 顶部信息栏（始终显示）
            if (showControls || !isPlaying) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            androidx.compose.ui.graphics.Brush.verticalGradient(
                                colors = listOf(
                                    Color.Black.copy(alpha = 0.8f),
                                    Color.Transparent
                                )
                            )
                        )
                        .padding(16.dp)
                        .zIndex(2f)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // 广告标识
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier
                                    .background(
                                        Color(0xFFFFD700),
                                        RoundedCornerShape(4.dp)
                                    )
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    text = "AD",
                                    color = Color.Black,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            
                            Spacer(modifier = Modifier.width(8.dp))
                            
                            Text(
                                text = advertiser,
                                color = Color.White,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                        
                        // 关闭按钮
                        if (!isPlaying) {
                            IconButton(
                                onClick = { showCloseDialog = true },
                                modifier = Modifier
                                    .background(
                                        Color.Black.copy(alpha = 0.6f),
                                        CircleShape
                                    )
                                    .size(40.dp)
                            ) {
                                Text(
                                    text = "✕",
                                    color = Color.White,
                                    fontSize = 18.sp
                                )
                            }
                        }
                    }
                }
            }
            
            // 播放控制界面
            if (showControls && isVideoReady) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            if (!isPlaying) Color.Black.copy(alpha = 0.3f) else Color.Transparent
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    if (!isPlaying) {
                        // 播放按钮
                        IconButton(
                            onClick = {
                                exoPlayer?.play()
                                isPlaying = true
                                onAdStarted()
                            },
                            modifier = Modifier
                                .size(80.dp)
                                .background(
                                    Color(0xFF4CAF50).copy(alpha = 0.8f),
                                    CircleShape
                                )
                        ) {
                            Text(
                                text = "▶",
                                color = Color.White,
                                fontSize = 32.sp
                            )
                        }
                    }
                }
            }
            
            // 底部控制栏
            if (isPlaying && (showControls || canSkip)) {
                Column(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .fillMaxWidth()
                        .background(
                            androidx.compose.ui.graphics.Brush.verticalGradient(
                                colors = listOf(
                                    Color.Transparent,
                                    Color.Black.copy(alpha = 0.8f)
                                )
                            )
                        )
                        .padding(16.dp)
                ) {
                    // 进度条
                    LinearProgressIndicator(
                        progress = currentProgress.toFloat() / duration,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(4.dp),
                        color = Color(0xFF4CAF50),
                        trackColor = Color.White.copy(alpha = 0.3f)
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // 时间和奖励信息
                        Column {
                            Text(
                                text = "${currentProgress}s / ${duration}s",
                                color = Color.White,
                                fontSize = 12.sp
                            )
                            Text(
                                text = "奖励：${rewardCoins} 金币",
                                color = Color(0xFFFFD700),
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        
                        // 跳过按钮
                        if (canSkip && !adCompleted) {
                            Button(
                                onClick = { 
                                    if (!adCompleted) {
                                        adCompleted = true
                                        exoPlayer?.pause()
                                        onAdCompleted(false)
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color.White.copy(alpha = 0.8f)
                                ),
                                modifier = Modifier
                                    .clip(RoundedCornerShape(20.dp))
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "跳过",
                                        fontSize = 14.sp,
                                        color = Color.Black,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "»",
                                        fontSize = 16.sp,
                                        color = Color.Black
                                    )
                                }
                            }
                        } else {
                            Box(
                                modifier = Modifier
                                    .background(
                                        Color.Black.copy(alpha = 0.5f),
                                        RoundedCornerShape(12.dp)
                                    )
                                    .padding(horizontal = 12.dp, vertical = 6.dp)
                            ) {
                                Text(
                                    text = "${skipTime - currentProgress}秒后可跳过",
                                    color = Color.White,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 关闭确认对话框
    if (showCloseDialog) {
        AlertDialog(
            onDismissRequest = { showCloseDialog = false },
            title = {
                Text("确认关闭广告？")
            },
            text = {
                Text("关闭广告将无法获得 ${rewardCoins} 金币奖励")
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showCloseDialog = false
                        exoPlayer?.pause()
                        onAdClosed()
                    }
                ) {
                    Text("确认关闭", color = Color.Red)
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showCloseDialog = false }
                ) {
                    Text("继续观看")
                }
            }
        )
    }
}
