package com.game.needleinsert.ui

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
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
import com.game.needleinsert.model.GameState
import com.game.needleinsert.model.Needle
import com.game.needleinsert.viewmodel.GameViewModel
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
    }
    
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(
                Brush.radialGradient(
                    colors = listOf(
                        Color(0xFF1a1a2e),
                        Color(0xFF16213e),
                        Color(0xFF0f0f23)
                    )
                )
            )
    ) {
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
        
        // 底部提示
        if (viewModel.gameData.state == GameState.PLAYING) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 50.dp)
            ) {
                Text(
                    text = if (viewModel.isNeedleLaunching) "针正在发射..." else "点击屏幕发射针",
                    color = Color.White.copy(alpha = 0.8f),
                    fontSize = 16.sp
                )
                
                if (!viewModel.isNeedleLaunching) {
                    Text(
                        text = "💡 针从下方射向圆盘",
                        color = Color.White.copy(alpha = 0.6f),
                        fontSize = 14.sp,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
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
    
    // 绘制圆盘
    drawCircle(
        color = Color(0xFF2d4059),
        radius = viewModel.diskRadius,
        center = Offset(centerX, centerY),
        style = Stroke(width = 8.dp.toPx())
    )
    
    drawCircle(
        color = Color(0xFF1a1a2e),
        radius = viewModel.diskRadius - 20,
        center = Offset(centerX, centerY)
    )
    
    // 绘制中心圆
    drawCircle(
        color = Color(0xFFea5455),
        radius = 15f,
        center = Offset(centerX, centerY)
    )
    
    // 绘制已插入的针
    viewModel.insertedNeedles.forEach { needle ->
        drawNeedle(
            needle = needle,
            centerX = centerX,
            centerY = centerY,
            color = Color(0xFFf39c12),
            isInserted = true
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
            color = if (viewModel.isNeedleLaunching) Color(0xFFf39c12) else Color(0xFF00d4aa),
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
            radius = 20f,
            center = Offset(endX, endY)
        )
        drawCircle(
            color = color.copy(alpha = 0.5f),
            radius = 12f,
            center = Offset(endX, endY)
        )
    }
    
    // 绘制针身
    drawLine(
        color = color,
        start = Offset(startX, startY),
        end = Offset(endX, endY),
        strokeWidth = if (isInserted) 6.dp.toPx() else 8.dp.toPx(),
        cap = StrokeCap.Round
    )
    
    // 绘制针尖
    drawCircle(
        color = if (isInserted) color else Color.White,
        radius = if (isInserted) 4f else 8f,
        center = Offset(endX, endY)
    )
    
    // 如果是准备发射的针，绘制箭头指示
    if (!isInserted) {
        val arrowSize = 6f
        val arrowX1 = endX - cos(needle.angle + 0.5f) * arrowSize
        val arrowY1 = endY - sin(needle.angle + 0.5f) * arrowSize
        val arrowX2 = endX - cos(needle.angle - 0.5f) * arrowSize
        val arrowY2 = endY - sin(needle.angle - 0.5f) * arrowSize
        
        drawLine(
            color = Color.White,
            start = Offset(endX, endY),
            end = Offset(arrowX1, arrowY1),
            strokeWidth = 3.dp.toPx(),
            cap = StrokeCap.Round
        )
        drawLine(
            color = Color.White,
            start = Offset(endX, endY),
            end = Offset(arrowX2, arrowY2),
            strokeWidth = 3.dp.toPx(),
            cap = StrokeCap.Round
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
            containerColor = Color.Black.copy(alpha = 0.5f)
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