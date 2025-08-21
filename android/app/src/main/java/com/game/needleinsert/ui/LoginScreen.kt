package com.game.needleinsert.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.game.needleinsert.ui.theme.GameColors
import com.game.needleinsert.ui.components.AnimatedBackground
import com.game.needleinsert.ui.components.PulsingButton
import com.game.needleinsert.viewmodel.UserViewModel
import kotlinx.coroutines.launch

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    viewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val uiState by viewModel.uiState.collectAsState()

    // 监听登录状态变化
    LaunchedEffect(uiState.user) {
        if (uiState.user != null) {
            onLoginSuccess()
        }
    }

    AnimatedBackground(
        modifier = Modifier.fillMaxSize()
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                
                // 游戏Logo区域
                GameLogoSection()
                
                Spacer(modifier = Modifier.height(60.dp))
                
                // 登录卡片
                LoginCard(
                    isLoading = uiState.isLoading,
                    errorMessage = uiState.errorMessage,
                    onLogin = {
                        scope.launch {
                            viewModel.autoLogin(context)
                        }
                    },
                    onClearError = { viewModel.clearError() }
                )
                
                Spacer(modifier = Modifier.height(40.dp))
                
                // 底部说明文字
                InfoSection()
            }
        }
    }
}

@Composable
private fun GameLogoSection() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 游戏图标
        Box(
            modifier = Modifier
                .size(120.dp)
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        colors = listOf(
                            GameColors.Primary.copy(alpha = 0.8f),
                            GameColors.AccentPink.copy(alpha = 0.6f),
                            GameColors.ElectricBlue.copy(alpha = 0.4f)
                        )
                    )
                )
                .border(4.dp, Color.White.copy(alpha = 0.3f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "🎯",
                fontSize = 48.sp
            )
        }
        
        Spacer(modifier = Modifier.height(20.dp))
        
        // 游戏标题
        Text(
            text = "见缝插针",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            textAlign = TextAlign.Center
        )
        
        Text(
            text = "NEEDLE INSERT GAME",
            fontSize = 14.sp,
            fontWeight = FontWeight.Medium,
            color = GameColors.GoldYellow.copy(alpha = 0.8f),
            textAlign = TextAlign.Center,
            letterSpacing = 2.sp
        )
    }
}

@Composable
private fun LoginCard(
    isLoading: Boolean,
    errorMessage: String,
    onLogin: () -> Unit,
    onClearError: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.95f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 欢迎文字
            Text(
                text = "欢迎来到游戏世界",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = GameColors.Primary,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "系统将自动为您创建游戏账户\n开始您的挑战之旅！",
                fontSize = 14.sp,
                color = GameColors.TextSecondary,
                textAlign = TextAlign.Center,
                lineHeight = 20.sp
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // 登录按钮或加载状态
            if (isLoading) {
                LoadingSection()
            } else {
                LoginButton(onLogin = onLogin)
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            // 错误信息
            if (errorMessage.isNotEmpty()) {
                ErrorSection(
                    errorMessage = errorMessage,
                    onRetry = onLogin,
                    onClearError = onClearError
                )
            }
        }
    }
}

@Composable
private fun LoadingSection() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator(
            modifier = Modifier.size(40.dp),
            color = GameColors.Primary,
            strokeWidth = 4.dp
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "正在为您创建账户...",
            fontSize = 16.sp,
            color = GameColors.TextPrimary,
            fontWeight = FontWeight.Medium
        )
        
        Text(
            text = "请稍候片刻",
            fontSize = 12.sp,
            color = GameColors.TextSecondary
        )
    }
}

@Composable
private fun LoginButton(onLogin: () -> Unit) {
    PulsingButton(
        onClick = onLogin,
        backgroundColor = GameColors.Primary,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "🚀",
                fontSize = 20.sp
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            Text(
                text = "开始游戏",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
        }
    }
}

@Composable
private fun ErrorSection(
    errorMessage: String,
    onRetry: () -> Unit,
    onClearError: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Red.copy(alpha = 0.1f)
        ),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = Brush.linearGradient(
                colors = listOf(
                    Color.Red.copy(alpha = 0.3f),
                    Color.Red.copy(alpha = 0.2f)
                )
            )
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 错误图标
            Text(
                text = "⚠️",
                fontSize = 24.sp
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "连接失败",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Red.copy(alpha = 0.8f)
            )
            
            Text(
                text = errorMessage,
                fontSize = 12.sp,
                color = Color.Red.copy(alpha = 0.7f),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = 4.dp)
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // 操作按钮
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // 重试按钮
                OutlinedButton(
                    onClick = {
                        onClearError()
                        onRetry()
                    },
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = GameColors.Primary
                    ),
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "🔄 重试",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                // 关闭按钮
                TextButton(
                    onClick = onClearError,
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "关闭",
                        fontSize = 14.sp,
                        color = GameColors.TextSecondary
                    )
                }
            }
        }
    }
}

@Composable
private fun InfoSection() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Black.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "🎮 游戏特色",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = GameColors.GoldYellow
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            val features = listOf(
                "💰 观看广告获得金币奖励",
                "🏆 挑战最高分记录",
                "💸 金币可提现到支付宝",
                "🎯 精准操作，简单易上手"
            )
            
            features.forEach { feature ->
                Text(
                    text = feature,
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.8f),
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }
}