package com.game.needleinsert.ui

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.animation.core.*
import androidx.compose.ui.graphics.graphicsLayer
import com.game.needleinsert.model.*
import com.game.needleinsert.viewmodel.GameViewModel
import com.game.needleinsert.ui.theme.GameColors
import com.game.needleinsert.ui.components.AnimatedBackground
import com.game.needleinsert.ui.FullScreenAdActivity
import androidx.activity.result.contract.ActivityResultContracts
import android.app.Activity
import android.content.Intent
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.delay
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun GameScreen(
    modifier: Modifier = Modifier,
    onBackPressed: () -> Unit = {},
    viewModel: GameViewModel = viewModel()
) {
    val configuration = LocalConfiguration.current
    val screenWidth = configuration.screenWidthDp.toFloat()
    val screenHeight = configuration.screenHeightDp.toFloat()
    
    // 初始化游戏
    LaunchedEffect(Unit) {
        viewModel.initGame(screenWidth, screenHeight)
        // 重置广告状态，防止从全屏广告返回时状态异常
        viewModel.resetAdState()
    }
    
    AnimatedBackground(
        modifier = modifier.fillMaxSize(),
        particleCount = 30
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // 游戏区域
            Canvas(
                modifier = Modifier
                    .fillMaxSize()
                    .clickable {
                        if (viewModel.gameData.state == GameState.PLAYING) {
                            viewModel.insertNeedle()
                        }
                    }
            ) {
                drawGameContent(
                    viewModel = viewModel,
                    canvasSize = size
                )
            }
            
            // 顶部信息栏
            GameInfoBar(
                gameData = viewModel.gameData,
                onPauseClick = { viewModel.togglePause() },
                onBackClick = onBackPressed,
                modifier = Modifier.align(Alignment.TopCenter)
            )
        
        // 游戏结束对话框
        if (viewModel.gameData.state == GameState.GAME_OVER) {
            GameOverDialog(
                score = viewModel.gameData.score,
                level = viewModel.gameData.level,
                onRestartClick = { viewModel.restartGame() },
                onExitClick = onBackPressed
            )
        }
        
        // 暂停对话框
        if (viewModel.gameData.state == GameState.PAUSED) {
            PauseDialog(
                onResumeClick = { viewModel.togglePause() },
                onRestartClick = { viewModel.restartGame() },
                onExitClick = onBackPressed
            )
        }
        
        // 底部针队列显示
        if (viewModel.gameData.state == GameState.PLAYING) {
            NeedleQueueDisplay(
                needleQueue = viewModel.gameData.needleQueue,
                currentIndex = viewModel.gameData.needlesInserted,
                viewModel = viewModel,
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 30.dp)
            )
        }
        
        // 广告机会提示
        if (viewModel.gameData.canShowAd && viewModel.gameData.adState == AdState.NONE) {
            AdOpportunityDialog(
                onWatchClick = { viewModel.requestWatchAd() },
                onDismissClick = { viewModel.cancelAdWatch() }
            )
        }
        
        // 广告播放界面 - 全屏广告确认对话框
        if (viewModel.gameData.adState == AdState.READY) {
            val context = LocalContext.current
            
            AlertDialog(
                onDismissRequest = { viewModel.cancelAdWatch() },
                title = {
                    Text(
                        text = "🎬 开始观看广告",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                },
                text = {
                    viewModel.currentAd?.let { ad ->
                        Column {
                            Text(
                                text = "即将全屏播放广告视频",
                                fontSize = 16.sp
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "💰 观看完整可获得 ${ad.rewardCoins} 金币",
                                fontSize = 14.sp,
                                color = Color(0xFFFFD700),
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            viewModel.currentAd?.let { ad ->
                                // 启动全屏广告Activity
                                FullScreenAdActivity.startForResult(context as Activity, ad, 1002)
                                // 标记为正在播放状态并关闭对话框
                                viewModel.startPlayingAd()
                            }
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF4CAF50)
                        )
                    ) {
                        Text("开始观看")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { viewModel.cancelAdWatch() }) {
                        Text("取消")
                    }
                }
            )
        }
        
        // 广告奖励提示
        viewModel.adReward?.let { reward ->
            AdRewardDialog(
                reward = reward,
                onDismiss = { viewModel.dismissAdReward() }
            )
        }
        }
    }
}

private fun DrawScope.drawGameContent(
    viewModel: GameViewModel,
    canvasSize: androidx.compose.ui.geometry.Size
) {
    val centerX = canvasSize.width / 2
    val centerY = canvasSize.height / 2
    
    // 更新ViewModel中的中心坐标
    viewModel.centerX = centerX
    viewModel.centerY = centerY
    
    // 绘制圆盘 - 使用渐变和发光效果
    val diskGradient = Brush.radialGradient(
        colors = listOf(
            GameColors.ElectricBlue.copy(alpha = 0.8f),
            GameColors.RoyalPurple.copy(alpha = 0.6f),
            GameColors.MidnightBlue.copy(alpha = 0.9f)
        ),
        center = Offset(centerX, centerY),
        radius = viewModel.diskRadius
    )
    
    // 外层发光圈
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(
                GameColors.ElectricBlue.copy(alpha = 0.3f),
                Color.Transparent
            ),
            center = Offset(centerX, centerY),
            radius = viewModel.diskRadius + 20f
        ),
        radius = viewModel.diskRadius + 20f,
        center = Offset(centerX, centerY)
    )
    
    // 主圆盘
    drawCircle(
        brush = diskGradient,
        radius = viewModel.diskRadius - 15,
        center = Offset(centerX, centerY)
    )
    
    // 圆盘边框
    drawCircle(
        color = GameColors.ElectricBlue,
        radius = viewModel.diskRadius,
        center = Offset(centerX, centerY),
        style = Stroke(width = 6.dp.toPx())
    )
    
    // 绘制中心圆 - 豪华金色渐变
    val centerGradient = Brush.radialGradient(
        colors = listOf(
            GameColors.GoldYellow,
            GameColors.SunsetOrange,
            GameColors.AccentOrange.copy(alpha = 0.8f)
        ),
        center = Offset(centerX, centerY),
        radius = 50f
    )
    
    // 中心圆外层光晕
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(
                GameColors.GoldYellow.copy(alpha = 0.4f),
                GameColors.SunsetOrange.copy(alpha = 0.2f),
                Color.Transparent
            ),
            center = Offset(centerX, centerY),
            radius = 70f
        ),
        radius = 70f,
        center = Offset(centerX, centerY)
    )
    
    // 主中心圆
    drawCircle(
        brush = centerGradient,
        radius = 50f,
        center = Offset(centerX, centerY)
    )
    
    // 中心圆边框 - 双层边框效果
    drawCircle(
        color = Color.White,
        radius = 50f,
        center = Offset(centerX, centerY),
        style = Stroke(width = 4.dp.toPx())
    )
    
    drawCircle(
        color = GameColors.GoldYellow,
        radius = 46f,
        center = Offset(centerX, centerY),
        style = Stroke(width = 2.dp.toPx())
    )
    
    // 绘制已插入的针
    viewModel.insertedNeedles.forEach { needle ->
        drawNeedle(
            needle = needle,
            centerX = centerX,
            centerY = centerY,
            color = needle.color,
            isInserted = true
        )
    }
    
    // 在中心圆上绘制剩余针数 - 调整字体大小
    val remainingNeedles = viewModel.gameData.needlesRequired - viewModel.gameData.needlesInserted
    drawContext.canvas.nativeCanvas.apply {
        drawText(
            remainingNeedles.toString(),
            centerX,
            centerY + 15f, // 文字垂直居中偏移
            android.graphics.Paint().apply {
                color = android.graphics.Color.WHITE
                textSize = 56f // 增大字体
                textAlign = android.graphics.Paint.Align.CENTER
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            }
        )
    }
    
    // 绘制发射轨迹线
    viewModel.currentNeedle?.let { needle ->
        if (!viewModel.isNeedleLaunching) {
            // 绘制瞄准线
            val aimLineStartRadius = needle.radius + 20f
            val aimLineEndRadius = viewModel.diskRadius + 10f
            val aimStartX = centerX + cos(needle.angle) * aimLineStartRadius
            val aimStartY = centerY + sin(needle.angle) * aimLineStartRadius
            val aimEndX = centerX + cos(needle.angle) * aimLineEndRadius
            val aimEndY = centerY + sin(needle.angle) * aimLineEndRadius
            
            // 绘制虚线瞄准线
            val dashLength = 10f
            val gapLength = 8f
            var currentDistance = 0f
            val totalDistance = aimLineStartRadius - aimLineEndRadius
            
            while (currentDistance < totalDistance) {
                val progress1 = currentDistance / totalDistance
                val progress2 = minOf((currentDistance + dashLength) / totalDistance, 1f)
                
                val dash1X = centerX + cos(needle.angle) * (aimLineStartRadius - currentDistance)
                val dash1Y = centerY + sin(needle.angle) * (aimLineStartRadius - currentDistance)
                val dash2X = centerX + cos(needle.angle) * (aimLineStartRadius - currentDistance - dashLength)
                val dash2Y = centerY + sin(needle.angle) * (aimLineStartRadius - currentDistance - dashLength)
                
                drawLine(
                    color = Color(0xFF00d4aa).copy(alpha = 0.6f),
                    start = Offset(dash1X, dash1Y),
                    end = Offset(dash2X, dash2Y),
                    strokeWidth = 2.dp.toPx(),
                    cap = StrokeCap.Round
                )
                
                currentDistance += dashLength + gapLength
            }
        }
    }
    
    // 绘制当前准备插入的针
    viewModel.currentNeedle?.let { needle ->
        drawNeedle(
            needle = needle,
            centerX = centerX,
            centerY = centerY,
            color = if (viewModel.isNeedleLaunching) needle.color.copy(alpha = 0.8f) else needle.color,
            isInserted = false
        )
    }
}

private fun DrawScope.drawNeedle(
    needle: Needle,
    centerX: Float,
    centerY: Float,
    color: Color,
    isInserted: Boolean
) {
    val needleLength = 80f
    val startX = centerX + cos(needle.angle) * (needle.radius - needleLength)
    val startY = centerY + sin(needle.angle) * (needle.radius - needleLength)
    val endX = centerX + cos(needle.angle) * needle.radius
    val endY = centerY + sin(needle.angle) * needle.radius
    
    // 如果是准备发射的针，添加发光效果
    if (!isInserted) {
        // 绘制发光光晕
        drawCircle(
            color = color.copy(alpha = 0.3f),
            radius = 25f,
            center = Offset(endX, endY)
        )
        drawCircle(
            color = color.copy(alpha = 0.6f),
            radius = 15f,
            center = Offset(endX, endY)
        )
    }
    
    // 绘制针身
    drawLine(
        color = color,
        start = Offset(startX, startY),
        end = Offset(endX, endY),
        strokeWidth = if (isInserted) 8.dp.toPx() else 10.dp.toPx(),
        cap = StrokeCap.Round
    )
    
    // 绘制针头圆圈
    drawCircle(
        color = color,
        radius = if (isInserted) 12f else 16f,
        center = Offset(endX, endY)
    )
    
    // 绘制针头边框
    drawCircle(
        color = Color.White,
        radius = if (isInserted) 12f else 16f,
        center = Offset(endX, endY),
        style = Stroke(width = 2.dp.toPx())
    )
    
    // 在针头上绘制数字
    drawContext.canvas.nativeCanvas.apply {
        drawText(
            needle.number.toString(),
            endX,
            endY + if (isInserted) 6f else 8f, // 文字垂直居中偏移
            android.graphics.Paint().apply {
                this.color = android.graphics.Color.WHITE
                textSize = if (isInserted) 20f else 24f
                textAlign = android.graphics.Paint.Align.CENTER
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            }
        )
    }
}

@Composable
fun GameInfoBar(
    gameData: com.game.needleinsert.model.GameData,
    onPauseClick: () -> Unit,
    onBackClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Transparent
        ),
        shape = RoundedCornerShape(20.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(
                            GameColors.DeepPurple.copy(alpha = 0.8f),
                            GameColors.RoyalPurple.copy(alpha = 0.6f),
                            GameColors.ElectricBlue.copy(alpha = 0.4f)
                        )
                    ),
                    RoundedCornerShape(20.dp)
                )
        ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 返回按钮
            IconButton(onClick = onBackClick) {
                Text(
                    text = "←",
                    color = Color.White,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // 游戏信息
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "第 ${gameData.level} 关",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "分数: ${gameData.score}",
                    color = Color.White.copy(alpha = 0.8f),
                    fontSize = 14.sp
                )
                
                // 显示金币数量
                Text(
                    text = "💰 ${gameData.coins}",
                    color = Color(0xFFFFD700),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
                
                // 关卡类型指示
                val levelTypeIcon = when (gameData.currentLevelType) {
                    LevelType.SPEED -> "⚡"
                    LevelType.REVERSE -> "🔄"
                    LevelType.RANDOM -> "🎲"
                    LevelType.OBSTACLE -> "⚠️"
                    LevelType.LARGE -> "📏"
                    LevelType.PRECISION -> "🎯"
                    else -> ""
                }
                
                if (levelTypeIcon.isNotEmpty()) {
                    Text(
                        text = levelTypeIcon,
                        color = Color.White,
                        fontSize = 16.sp,
                        modifier = Modifier.padding(top = 2.dp)
                    )
                }
            }
            
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "${gameData.needlesInserted}/${gameData.needlesRequired}",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "针数",
                    color = Color.White.copy(alpha = 0.8f),
                    fontSize = 14.sp
                )
            }
            
            // 暂停按钮
            IconButton(onClick = onPauseClick) {
                Text(
                    text = if (gameData.state == GameState.PAUSED) "▶" else "⏸",
                    color = Color.White,
                    fontSize = 20.sp
                )
            }
        }
        }
    }
}

@Composable
fun GameOverDialog(
    score: Int,
    level: Int,
    onRestartClick: () -> Unit,
    onExitClick: () -> Unit
) {
    AlertDialog(
        onDismissRequest = { },
        title = {
            Text(
                text = "游戏结束",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFea5455)
            )
        },
        text = {
            Column {
                Text(
                    text = "最终分数: $score",
                    fontSize = 18.sp
                )
                Text(
                    text = "通过关卡: $level",
                    fontSize = 18.sp
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onRestartClick,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF00d4aa)
                )
            ) {
                Text("重新开始")
            }
        },
        dismissButton = {
            TextButton(onClick = onExitClick) {
                Text("退出")
            }
        }
    )
}

@Composable
fun PauseDialog(
    onResumeClick: () -> Unit,
    onRestartClick: () -> Unit,
    onExitClick: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onResumeClick,
        title = {
            Text(
                text = "游戏暂停",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Text("选择一个操作")
        },
        confirmButton = {
            Button(onClick = onResumeClick) {
                Text("继续游戏")
            }
        },
        dismissButton = {
            Column {
                TextButton(onClick = onRestartClick) {
                    Text("重新开始")
                }
                TextButton(onClick = onExitClick) {
                    Text("退出游戏")
                }
            }
        }
    )
}

@Composable
fun NeedleQueueDisplay(
    needleQueue: List<Int>,
    currentIndex: Int,
    viewModel: GameViewModel,
    modifier: Modifier = Modifier
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = modifier
    ) {
        // 操作提示
        Text(
            text = if (viewModel.isNeedleLaunching) "针正在发射..." else "点击屏幕发射针",
            color = Color.White.copy(alpha = 0.8f),
            fontSize = 16.sp
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // 针队列
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth(),
            contentPadding = PaddingValues(horizontal = 20.dp)
        ) {
            items(needleQueue.size) { index ->
                val needleNumber = needleQueue[index]
                val isCompleted = index < currentIndex
                val isCurrent = index == currentIndex
                val needleColor = getNeedleDisplayColor(needleNumber)
                
                NeedleQueueItem(
                    number = needleNumber,
                    color = needleColor,
                    isCompleted = isCompleted,
                    isCurrent = isCurrent,
                    isLaunching = isCurrent && viewModel.isNeedleLaunching
                )
            }
        }
        
        // 关卡类型提示
        val levelDescription = when (viewModel.gameData.currentLevelType) {
            LevelType.NORMAL -> "普通关卡"
            LevelType.SPEED -> "⚡ 高速旋转"
            LevelType.REVERSE -> "🔄 反向旋转"
            LevelType.RANDOM -> "🎲 变速挑战"
            LevelType.OBSTACLE -> "⚠️ 有障碍物"
            LevelType.LARGE -> "📏 大量针"
            LevelType.PRECISION -> "🎯 精确插入"
        }
        
        Text(
            text = levelDescription,
            color = Color.White.copy(alpha = 0.6f),
            fontSize = 12.sp,
            modifier = Modifier.padding(top = 8.dp)
        )
    }
}

@Composable
fun NeedleQueueItem(
    number: Int,
    color: Color,
    isCompleted: Boolean,
    isCurrent: Boolean,
    isLaunching: Boolean
) {
    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .size(40.dp)
            .background(
                color = when {
                    isCompleted -> Color.Gray.copy(alpha = 0.5f)
                    isCurrent && isLaunching -> color.copy(alpha = 0.8f)
                    isCurrent -> color
                    else -> color.copy(alpha = 0.7f)
                },
                shape = CircleShape
            )
            .border(
                width = if (isCurrent) 2.dp else 1.dp,
                color = if (isCurrent) Color.White else Color.White.copy(alpha = 0.5f),
                shape = CircleShape
            )
    ) {
        Text(
            text = number.toString(),
            color = if (isCompleted) Color.Gray else Color.White,
            fontSize = 16.sp,
            fontWeight = if (isCurrent) FontWeight.Bold else FontWeight.Normal
        )
    }
}

// 获取显示用的针颜色（与ViewModel中的逻辑一致）
private fun getNeedleDisplayColor(number: Int): Color {
    val colors = listOf(
        Color(0xFF2196F3), // 蓝色
        Color(0xFFF44336), // 红色
        Color(0xFFFFEB3B), // 黄色
        Color(0xFF9C27B0), // 紫色
        Color(0xFF00BCD4), // 青色
        Color(0xFF4CAF50), // 绿色
        Color(0xFFFF9800), // 橙色
        Color(0xFFE91E63), // 粉色
        Color(0xFF795548), // 棕色
        Color(0xFF607D8B)  // 蓝灰色
    )
    return colors[(number - 1) % colors.size]
}

@Composable
fun AdOpportunityDialog(
    onWatchClick: () -> Unit,
    onDismissClick: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismissClick,
        title = {
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "🎬",
                    fontSize = 32.sp
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "观看广告获得奖励",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        },
        text = {
            Column {
                Text(
                    text = "观看15秒广告视频可获得金币奖励！",
                    fontSize = 16.sp
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "💰 奖励：50-150金币",
                    fontSize = 14.sp,
                    color = Color(0xFFFFD700),
                    fontWeight = FontWeight.Bold
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onWatchClick,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50)
                )
            ) {
                Text("观看广告")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismissClick) {
                Text("稍后再看")
            }
        }
    )
}

@Composable
fun AdPlayerDialog(
    ad: AdConfig,
    adState: AdState,
    onStartPlay: () -> Unit,
    onComplete: () -> Unit,
    onCancel: () -> Unit
) {
    var progress by remember { mutableStateOf(0) }
    var canSkip by remember { mutableStateOf(false) }
    
    LaunchedEffect(adState) {
        if (adState == AdState.PLAYING) {
            // 模拟广告播放进度
            for (i in 1..30) {
                delay(1000)
                progress = i
                if (i >= 15) canSkip = true
                if (i >= 30) {
                    onComplete()
                    break
                }
            }
        }
    }
    
    AlertDialog(
        onDismissRequest = { },
        title = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = ad.title,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                
                if (adState == AdState.PLAYING && canSkip) {
                    TextButton(onClick = onComplete) {
                        Text("跳过", color = Color.Gray)
                    }
                }
            }
        },
        text = {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                when (adState) {
                    AdState.READY -> {
                        Text("准备播放广告...")
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = onStartPlay) {
                            Text("开始播放")
                        }
                    }
                    AdState.PLAYING -> {
                        // 模拟视频播放界面
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(200.dp)
                                .background(Color.Black),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "🎬",
                                    fontSize = 48.sp,
                                    color = Color.White
                                )
                                Text(
                                    text = "广告播放中...",
                                    color = Color.White,
                                    fontSize = 16.sp
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                LinearProgressIndicator(
                                    progress = progress / 30f,
                                    modifier = Modifier.fillMaxWidth(0.8f)
                                )
                                Text(
                                    text = "${progress}/30秒",
                                    color = Color.White,
                                    fontSize = 14.sp
                                )
                                if (!canSkip) {
                                    Text(
                                        text = "15秒后可跳过",
                                        color = Color.Gray,
                                        fontSize = 12.sp
                                    )
                                }
                            }
                        }
                    }
                    else -> {
                        Text("加载中...")
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "💰 奖励：${ad.rewardCoins} 金币",
                    fontSize = 14.sp,
                    color = Color(0xFFFFD700),
                    fontWeight = FontWeight.Bold
                )
            }
        },
        confirmButton = {
            if (adState == AdState.READY) {
                TextButton(onClick = onCancel) {
                    Text("取消")
                }
            }
        },
        dismissButton = { }
    )
}

@Composable
fun AdRewardDialog(
    reward: AdReward,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "🎉",
                    fontSize = 48.sp
                )
                Text(
                    text = "恭喜获得奖励！",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF4CAF50)
                )
            }
        },
        text = {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = reward.message ?: "观看完成",
                    fontSize = 16.sp,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "💰 +${reward.coins}",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFFD700)
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onDismiss,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50)
                )
            ) {
                Text("太棒了！")
            }
        },
        dismissButton = { }
    )
} 