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
import com.game.needleinsert.ui.GameScreen
import com.game.needleinsert.ui.theme.NeedleInsertTheme

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
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF1a1a2e),
                        Color(0xFF16213e),
                        Color(0xFF0f0f23)
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // 游戏标题
            Text(
                text = "见缝插针",
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                textAlign = TextAlign.Center
            )
            
            Text(
                text = "NEEDLE INSERT",
                fontSize = 16.sp,
                color = Color.White.copy(alpha = 0.7f),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 60.dp)
            )
            
            // 主菜单按钮
            MenuButton(
                text = "开始游戏",
                onClick = onStartGame,
                backgroundColor = Color(0xFF00d4aa)
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            MenuButton(
                text = "排行榜",
                onClick = { /* TODO: 实现排行榜 */ },
                backgroundColor = Color(0xFF2d4059)
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            MenuButton(
                text = "观看广告",
                onClick = { /* TODO: 实现广告中心 */ },
                backgroundColor = Color(0xFF4CAF50)
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            MenuButton(
                text = "设置",
                onClick = { /* TODO: 实现设置 */ },
                backgroundColor = Color(0xFF2d4059)
            )
            
            Spacer(modifier = Modifier.height(40.dp))
            
            // 游戏说明
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Black.copy(alpha = 0.3f)
                ),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp)
                ) {
                    Text(
                        text = "游戏规则",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )
                    
                    Text(
                        text = "• 点击屏幕从下方发射彩色数字针\n• 针按顺序发射，每个都有独特颜色\n• 中心显示剩余针数，底部显示发射队列\n• 多种关卡类型：普通、高速、反向、变速等\n• 🎬 观看广告获得金币奖励！\n• 精美的视觉效果和流畅动画",
                        fontSize = 14.sp,
                        color = Color.White.copy(alpha = 0.8f),
                        lineHeight = 20.sp
                    )
                }
            }
        }
    }
}

@Composable
fun MenuButton(
    text: String,
    onClick: () -> Unit,
    backgroundColor: Color,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = backgroundColor
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Text(
            text = text,
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium,
            color = Color.White
        )
    }
} 