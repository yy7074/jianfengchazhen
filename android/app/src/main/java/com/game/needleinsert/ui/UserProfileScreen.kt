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
import com.game.needleinsert.model.User
import com.game.needleinsert.utils.UserManager
import com.game.needleinsert.viewmodel.UserViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UserProfileScreen(
    onBack: () -> Unit,
    onLogout: () -> Unit,
    onLogin: () -> Unit = {},
    viewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadUserInfo()
    }

    AnimatedBackground(
        modifier = Modifier.fillMaxSize()
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 标题栏
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                PulsingButton(
                    onClick = onBack,
                    backgroundColor = GameColors.DeepPurple.copy(alpha = 0.7f),
                    modifier = Modifier.padding(8.dp)
                ) {
                    Text(
                        text = "← 返回",
                        color = Color.White,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                Text(
                    text = "👤 用户信息",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                
                Spacer(modifier = Modifier.width(80.dp)) // 平衡布局
            }
            
            Spacer(modifier = Modifier.height(40.dp))
            
            // 用户信息卡片
            when {
                uiState.isLoading -> {
                    LoadingCard()
                }
                uiState.user != null -> {
                    UserInfoCard(
                        user = uiState.user!!,
                        onLogin = {
                            scope.launch {
                                viewModel.autoLogin(context)
                            }
                        },
                        onLogout = {
                            viewModel.logout()
                        }
                    )
                }
                else -> {
                    LoginCard(
                        onLogin = {
                            scope.launch {
                                viewModel.autoLogin(context)
                            }
                        }
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            // 错误信息
            if (uiState.errorMessage.isNotEmpty()) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(15.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.Red.copy(alpha = 0.1f))
                ) {
                    Text(
                        text = uiState.errorMessage,
                        modifier = Modifier.padding(16.dp),
                        color = Color.Red,
                        fontSize = 14.sp,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
    }
}

@Composable
private fun LoadingCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.95f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(30.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            CircularProgressIndicator(
                color = GameColors.Primary,
                strokeWidth = 3.dp
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            Text(
                text = "正在加载用户信息...",
                fontSize = 16.sp,
                color = GameColors.TextPrimary
            )
        }
    }
}

@Composable
private fun LoginCard(onLogin: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.95f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(30.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "🎮",
                fontSize = 48.sp
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            Text(
                text = "欢迎来到见缝插针",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = GameColors.Primary
            )
            
            Spacer(modifier = Modifier.height(10.dp))
            
            Text(
                text = "点击下方按钮开始游戏\n系统将自动为您创建游戏账户",
                fontSize = 14.sp,
                color = GameColors.TextSecondary,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(30.dp))
            
            PulsingButton(
                onClick = onLogin,
                backgroundColor = GameColors.Primary,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "🚀 开始游戏",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
private fun UserInfoCard(
    user: User,
    onLogin: () -> Unit,
    onLogout: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.95f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(30.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 头像
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.radialGradient(
                            colors = listOf(
                                GameColors.Primary.copy(alpha = 0.8f),
                                GameColors.AccentPink.copy(alpha = 0.6f)
                            )
                        )
                    )
                    .border(3.dp, Color.White, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "🎮",
                    fontSize = 32.sp
                )
            }
            
            Spacer(modifier = Modifier.height(20.dp))
            
            // 用户名
            Text(
                text = user.nickname,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = GameColors.Primary
            )
            
            Spacer(modifier = Modifier.height(5.dp))
            
            Text(
                text = "等级 ${user.level}",
                fontSize = 14.sp,
                color = GameColors.TextSecondary
            )
            
            Spacer(modifier = Modifier.height(30.dp))
            
            // 统计信息网格
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(15.dp)
            ) {
                // 第一行：金币和最高分
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    StatCard(
                        icon = "💰",
                        title = "金币",
                        value = "${user.coins}",
                        color = GameColors.AccentOrange,
                        modifier = Modifier.weight(1f)
                    )
                    
                    Spacer(modifier = Modifier.width(10.dp))
                    
                    StatCard(
                        icon = "🏆",
                        title = "最高分",
                        value = "${user.bestScore}",
                        color = GameColors.AccentPink,
                        modifier = Modifier.weight(1f)
                    )
                }
                
                // 第二行：等级和设备信息
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    StatCard(
                        icon = "⭐",
                        title = "等级",
                        value = "${user.level}",
                        color = GameColors.Primary,
                        modifier = Modifier.weight(1f)
                    )
                    
                    Spacer(modifier = Modifier.width(10.dp))
                    
                    StatCard(
                        icon = "📱",
                        title = "设备",
                        value = "ID: ${user.deviceId.takeLast(6)}",
                        color = GameColors.TextSecondary,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(30.dp))
            
            // 操作按钮
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(15.dp)
            ) {
                PulsingButton(
                    onClick = onLogin,
                    backgroundColor = GameColors.Primary,
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "🔄 刷新",
                        color = Color.White,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                PulsingButton(
                    onClick = onLogout,
                    backgroundColor = GameColors.TextSecondary,
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "🚪 登出",
                        color = Color.White,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
private fun StatCard(
    icon: String,
    title: String,
    value: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        shape = RoundedCornerShape(15.dp),
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        ),
        modifier = modifier.border(1.dp, color.copy(alpha = 0.3f), RoundedCornerShape(15.dp))
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = icon,
                fontSize = 24.sp
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = value,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = color
            )
            
            Text(
                text = title,
                fontSize = 12.sp,
                color = GameColors.TextSecondary
            )
        }
    }
}