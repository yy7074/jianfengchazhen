package com.game.needleinsert.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import com.game.needleinsert.ui.theme.GameColors
import kotlin.math.*
import kotlin.random.Random

@Composable
fun AnimatedBackground(
    modifier: Modifier = Modifier,
    particleCount: Int = 50,
    content: @Composable () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "background_animation")
    
    // 背景渐变动画
    val gradientOffset by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(8000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "gradient_offset"
    )
    
    // 粒子动画
    val particleAnimation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(20000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "particle_animation"
    )
    
    val density = LocalDensity.current
    
    Box(modifier = modifier) {
        // 动画背景
        Canvas(
            modifier = Modifier.fillMaxSize()
        ) {
            drawAnimatedBackground(size, gradientOffset, particleAnimation, particleCount)
        }
        
        // 内容层
        content()
    }
}

private fun DrawScope.drawAnimatedBackground(
    canvasSize: androidx.compose.ui.geometry.Size,
    gradientOffset: Float,
    particleAnimation: Float,
    particleCount: Int
) {
    // 绘制渐变背景
    val gradient = Brush.radialGradient(
        colors = listOf(
            GameColors.MidnightBlue.copy(alpha = 0.9f),
            GameColors.DeepPurple.copy(alpha = 0.7f),
            GameColors.RoyalPurple.copy(alpha = 0.5f),
            GameColors.ElectricBlue.copy(alpha = 0.3f)
        ),
        center = Offset(
            canvasSize.width * (0.3f + 0.4f * sin(gradientOffset * PI.toFloat())),
            canvasSize.height * (0.3f + 0.4f * cos(gradientOffset * PI.toFloat()))
        ),
        radius = canvasSize.maxDimension * (0.8f + 0.3f * sin(gradientOffset * 2 * PI.toFloat()))
    )
    
    drawRect(gradient)
    
    // 绘制星空粒子效果
    drawStarField(canvasSize, particleAnimation, particleCount)
    
    // 绘制浮动光点
    drawFloatingLights(canvasSize, particleAnimation)
}

private fun DrawScope.drawStarField(
    canvasSize: androidx.compose.ui.geometry.Size,
    animation: Float,
    particleCount: Int
) {
    val random = Random(42) // 固定种子确保一致性
    
    repeat(particleCount) { index ->
        val baseX = random.nextFloat() * canvasSize.width
        val baseY = random.nextFloat() * canvasSize.height
        val twinkleSpeed = 1f + random.nextFloat() * 2f
        val size = 1f + random.nextFloat() * 3f
        
        // 星星闪烁效果
        val twinkle = sin((animation + index * 30f) * twinkleSpeed * PI.toFloat() / 180f)
        val alpha = 0.3f + 0.7f * (twinkle * 0.5f + 0.5f)
        
        val color = when (index % 5) {
            0 -> GameColors.GoldYellow
            1 -> GameColors.ElectricBlue
            2 -> GameColors.NeonGreen
            3 -> GameColors.HotPink
            else -> Color.White
        }.copy(alpha = alpha)
        
        drawCircle(
            color = color,
            radius = size,
            center = Offset(baseX, baseY)
        )
    }
}

private fun DrawScope.drawFloatingLights(
    canvasSize: androidx.compose.ui.geometry.Size,
    animation: Float
) {
    val lightCount = 8
    repeat(lightCount) { index ->
        val angle = (animation + index * 45f) * PI.toFloat() / 180f
        val radiusX = canvasSize.width * 0.3f
        val radiusY = canvasSize.height * 0.25f
        
        val x = canvasSize.width * 0.5f + radiusX * cos(angle)
        val y = canvasSize.height * 0.5f + radiusY * sin(angle * 1.5f)
        
        val lightSize = 8f + 5f * sin(angle * 3f)
        val alpha = 0.4f + 0.3f * sin(angle * 2f)
        
        val lightColor = when (index % 4) {
            0 -> GameColors.AccentOrange
            1 -> GameColors.AccentPink
            2 -> GameColors.SecondaryTeal
            else -> GameColors.GoldYellow
        }.copy(alpha = alpha)
        
        // 光晕效果
        val haloGradient = Brush.radialGradient(
            colors = listOf(
                lightColor.copy(alpha = alpha),
                lightColor.copy(alpha = alpha * 0.5f),
                Color.Transparent
            ),
            center = Offset(x, y),
            radius = lightSize * 3f
        )
        
        drawCircle(
            brush = haloGradient,
            radius = lightSize * 3f,
            center = Offset(x, y)
        )
        
        // 核心光点
        drawCircle(
            color = lightColor,
            radius = lightSize,
            center = Offset(x, y)
        )
    }
}

@Composable
fun PulsingButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    backgroundColor: Color = GameColors.PrimaryBlue,
    content: @Composable () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "button_animation")
    
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "button_scale"
    )
    
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "button_glow"
    )
    
    Box(
        modifier = modifier
    ) {
        // 发光背景
        Box(
            modifier = Modifier
                .matchParentSize()
                .background(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            backgroundColor.copy(alpha = glowAlpha),
                            backgroundColor.copy(alpha = glowAlpha * 0.5f),
                            Color.Transparent
                        )
                    ),
                    shape = CircleShape
                )
        )
        
        // 按钮内容
        androidx.compose.material3.Button(
            onClick = onClick,
            enabled = enabled,
            modifier = Modifier
                .graphicsLayer {
                    scaleX = scale
                    scaleY = scale
                },
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(
                containerColor = backgroundColor
            )
        ) {
            content()
        }
    }
} 