package com.game.needleinsert

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.animation.core.*
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.PressInteraction
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.draw.scale
import com.game.needleinsert.ui.GameScreen
import com.game.needleinsert.ui.theme.NeedleInsertTheme
import com.game.needleinsert.ui.theme.GameColors
import com.game.needleinsert.ui.components.AnimatedBackground
import com.game.needleinsert.ui.components.PulsingButton

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            NeedleInsertTheme {
                MainNavigation()
            }
        }
    }
}

@Composable
fun MainNavigation() {
    var currentScreen by remember { mutableStateOf("menu") }
    
    when (currentScreen) {
        "menu" -> MainMenuScreen(
            onStartGame = { currentScreen = "game" }
        )
        "game" -> GameScreen(
            onBackPressed = { currentScreen = "menu" }
        )
    }
}

@Composable
fun MainMenuScreen(
    onStartGame: () -> Unit
) {
    // 标题动画
    val infiniteTransition = rememberInfiniteTransition(label = "title_animation")
    
    val titleScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "title_scale"
    )
    
    val titleGlow by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "title_glow"
    )
    
    AnimatedBackground(
        modifier = Modifier.fillMaxSize(),
        particleCount = 80
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // 游戏标题 - 带发光效果
            Box(
                modifier = Modifier
                    .graphicsLayer {
                        scaleX = titleScale
                        scaleY = titleScale
                    }
            ) {
                // 发光背景
                Text(
                    text = "见缝插针",
                    fontSize = 48.sp,
                    fontWeight = FontWeight.Bold,
                    color = GameColors.ElectricBlue.copy(alpha = titleGlow * 0.3f),
                    textAlign = TextAlign.Center,
                    modifier = Modifier.graphicsLayer {
                        scaleX = 1.1f
                        scaleY = 1.1f
                    }
                )
                
                // 主标题
                Text(
                    text = "见缝插针",
                    fontSize = 48.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
                    textAlign = TextAlign.Center
                )
            }
            
            Text(
                text = "🎯 NEEDLE INSERT 🎯",
                fontSize = 16.sp,
                color = GameColors.GoldYellow.copy(alpha = 0.9f),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 60.dp)
            )
            
            // 主菜单按钮 - 使用动画按钮
            PulsingButton(
                onClick = onStartGame,
                backgroundColor = GameColors.EmeraldGreen,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "🚀 开始游戏",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            AnimatedMenuButton(
                text = "🏆 排行榜",
                onClick = { /* TODO: 实现排行榜 */ },
                backgroundColor = GameColors.AccentOrange
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            AnimatedMenuButton(
                text = "🎬 观看广告",
                onClick = { /* TODO: 实现广告中心 */ },
                backgroundColor = GameColors.AccentPink
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            AnimatedMenuButton(
                text = "⚙️ 设置",
                onClick = { /* TODO: 实现设置 */ },
                backgroundColor = GameColors.DeepPurple
            )
            
            Spacer(modifier = Modifier.height(40.dp))
            
            // 游戏说明 - 带渐变背景
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Transparent
                ),
                shape = RoundedCornerShape(20.dp)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            Brush.linearGradient(
                                colors = listOf(
                                    GameColors.MidnightBlue.copy(alpha = 0.6f),
                                    GameColors.DeepPurple.copy(alpha = 0.4f)
                                )
                            ),
                            RoundedCornerShape(20.dp)
                        )
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "🎮",
                                fontSize = 24.sp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "游戏规则",
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold,
                                color = GameColors.GoldYellow,
                                modifier = Modifier.padding(bottom = 4.dp)
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Text(
                            text = "🎯 点击屏幕从下方发射彩色数字针\n💫 针按顺序发射，每个都有独特颜色\n📊 中心显示剩余针数，底部显示发射队列\n🎪 多种关卡类型：普通、高速、反向、变速等\n🎬 观看广告获得金币奖励！\n✨ 精美的视觉效果和流畅动画",
                            fontSize = 14.sp,
                            color = Color.White.copy(alpha = 0.9f),
                            lineHeight = 22.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun AnimatedMenuButton(
    text: String,
    onClick: () -> Unit,
    backgroundColor: Color,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }
    var isPressed by remember { mutableStateOf(false) }
    
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "button_scale"
    )
    
    Button(
        onClick = {
            isPressed = true
            onClick()
        },
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp)
            .scale(scale),
        colors = ButtonDefaults.buttonColors(
            containerColor = backgroundColor
        ),
        shape = RoundedCornerShape(16.dp),
        interactionSource = interactionSource
    ) {
        
        Text(
            text = text,
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium,
            color = Color.White
        )
    }
}

 