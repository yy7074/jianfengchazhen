package com.game.needleinsert.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import com.game.needleinsert.ui.theme.GameColors
import kotlin.math.*
import kotlin.random.Random

@Composable
fun ScorePopup(
    score: Int,
    modifier: Modifier = Modifier,
    onAnimationEnd: () -> Unit = {}
) {
    val animationState = remember { MutableTransitionState(false) }
    
    LaunchedEffect(score) {
        animationState.targetState = true
    }
    
    val transition = updateTransition(animationState, label = "score_popup")
    
    val scale by transition.animateFloat(
        transitionSpec = {
            spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        },
        label = "scale"
    ) { isVisible ->
        if (isVisible) 1.2f else 0f
    }
    
    val alpha by transition.animateFloat(
        transitionSpec = { tween(1000) },
        label = "alpha"
    ) { isVisible ->
        if (isVisible) 1f else 0f
    }
    
    val offsetY by transition.animateFloat(
        transitionSpec = { tween(1000) },
        label = "offset"
    ) { isVisible ->
        if (isVisible) -100f else 0f
    }
    
    LaunchedEffect(transition.currentState) {
        if (transition.currentState && animationState.targetState) {
            onAnimationEnd()
        }
    }
    
    Canvas(
        modifier = modifier
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                this.alpha = alpha
                translationY = offsetY
            }
    ) {
        val centerX = size.width / 2
        val centerY = size.height / 2
        
        // 绘制发光背景
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    GameColors.GoldYellow.copy(alpha = 0.6f),
                    GameColors.SunsetOrange.copy(alpha = 0.3f),
                    Color.Transparent
                ),
                center = Offset(centerX, centerY),
                radius = 60f
            ),
            radius = 60f,
            center = Offset(centerX, centerY)
        )
        
        // 绘制分数文字
        drawContext.canvas.nativeCanvas.apply {
            drawText(
                "+$score",
                centerX,
                centerY + 10f,
                android.graphics.Paint().apply {
                    color = android.graphics.Color.WHITE
                    textSize = 32f
                    textAlign = android.graphics.Paint.Align.CENTER
                    setShadowLayer(4f, 0f, 0f, android.graphics.Color.parseColor("#FFD700"))
                }
            )
        }
    }
}

@Composable
fun LevelTransition(
    level: Int,
    levelType: String,
    modifier: Modifier = Modifier,
    onAnimationEnd: () -> Unit = {}
) {
    val animationState = remember(level) { MutableTransitionState(false) }
    
    LaunchedEffect(level) {
        animationState.targetState = true
    }
    
    val transition = updateTransition(animationState, label = "level_transition")
    
    val scale by transition.animateFloat(
        transitionSpec = {
            keyframes {
                durationMillis = 2000
                0f at 0
                1.5f at 300 with FastOutSlowInEasing
                1f at 600 with FastOutSlowInEasing
                1f at 2000
            }
        },
        label = "scale"
    ) { isVisible ->
        if (isVisible) 1f else 0f
    }
    
    val alpha by transition.animateFloat(
        transitionSpec = { tween(2000) },
        label = "alpha"
    ) { isVisible ->
        if (isVisible) 1f else 0f
    }
    
    val rotation by transition.animateFloat(
        transitionSpec = { tween(2000, easing = LinearEasing) },
        label = "rotation"
    ) { isVisible ->
        if (isVisible) 360f else 0f
    }
    
    LaunchedEffect(transition.currentState) {
        if (transition.currentState && animationState.targetState) {
            onAnimationEnd()
        }
    }
    
    Canvas(
        modifier = modifier
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                this.alpha = alpha
                rotationZ = rotation
            }
    ) {
        val centerX = size.width / 2
        val centerY = size.height / 2
        
        // 绘制彩虹光环
        val ringColors = listOf(
            GameColors.HotPink,
            GameColors.AccentOrange,
            GameColors.GoldYellow,
            GameColors.NeonGreen,
            GameColors.ElectricBlue,
            GameColors.RoyalPurple
        )
        
        ringColors.forEachIndexed { index, color ->
            val radius = 80f + index * 15f
            drawCircle(
                color = color.copy(alpha = 0.6f),
                radius = radius,
                center = Offset(centerX, centerY),
                style = Stroke(width = 8f)
            )
        }
        
        // 绘制中心文字背景
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    GameColors.MidnightBlue.copy(alpha = 0.9f),
                    GameColors.DeepPurple.copy(alpha = 0.7f)
                ),
                center = Offset(centerX, centerY),
                radius = 70f
            ),
            radius = 70f,
            center = Offset(centerX, centerY)
        )
        
        // 绘制关卡文字
        drawContext.canvas.nativeCanvas.apply {
            drawText(
                "第 $level 关",
                centerX,
                centerY - 10f,
                android.graphics.Paint().apply {
                    color = android.graphics.Color.WHITE
                    textSize = 28f
                    textAlign = android.graphics.Paint.Align.CENTER
                    isFakeBoldText = true
                }
            )
            
            drawText(
                levelType,
                centerX,
                centerY + 20f,
                android.graphics.Paint().apply {
                    color = android.graphics.Color.parseColor("#FFD700")
                    textSize = 16f
                    textAlign = android.graphics.Paint.Align.CENTER
                }
            )
        }
    }
}

@Composable
fun SuccessEffect(
    modifier: Modifier = Modifier,
    onAnimationEnd: () -> Unit = {}
) {
    val infiniteTransition = rememberInfiniteTransition(label = "success_effect")
    
    val sparkleRotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "sparkle_rotation"
    )
    
    val sparkleScale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "sparkle_scale"
    )
    
    Canvas(
        modifier = modifier
            .graphicsLayer {
                rotationZ = sparkleRotation
                scaleX = sparkleScale
                scaleY = sparkleScale
            }
    ) {
        val centerX = size.width / 2
        val centerY = size.height / 2
        
        // 绘制星星点点效果
        val starCount = 12
        repeat(starCount) { index ->
            val angle = (360f / starCount) * index + sparkleRotation
            val radius = 100f
            val x = centerX + radius * cos(angle * PI.toFloat() / 180f)
            val y = centerY + radius * sin(angle * PI.toFloat() / 180f)
            
            val starColor = when (index % 4) {
                0 -> GameColors.GoldYellow
                1 -> GameColors.ElectricBlue
                2 -> GameColors.HotPink
                else -> GameColors.NeonGreen
            }
            
            // 绘制星星
            drawStar(
                center = Offset(x, y),
                color = starColor,
                size = 8f + 4f * sin((sparkleRotation + index * 30f) * PI.toFloat() / 180f)
            )
        }
    }
}

private fun DrawScope.drawStar(
    center: Offset,
    color: Color,
    size: Float
) {
    val path = Path().apply {
        val outerRadius = size
        val innerRadius = size * 0.4f
        
        repeat(5) { i ->
            val outerAngle = (i * 72f - 90f) * PI.toFloat() / 180f
            val innerAngle = ((i + 0.5f) * 72f - 90f) * PI.toFloat() / 180f
            
            val outerX = center.x + outerRadius * cos(outerAngle)
            val outerY = center.y + outerRadius * sin(outerAngle)
            val innerX = center.x + innerRadius * cos(innerAngle)
            val innerY = center.y + innerRadius * sin(innerAngle)
            
            if (i == 0) {
                moveTo(outerX, outerY)
            } else {
                lineTo(outerX, outerY)
            }
            lineTo(innerX, innerY)
        }
        close()
    }
    
    drawPath(
        path = path,
        color = color
    )
} 