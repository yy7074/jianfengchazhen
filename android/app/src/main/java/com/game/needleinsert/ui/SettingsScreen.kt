package com.game.needleinsert.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.os.Build
import android.provider.Settings
import androidx.lifecycle.viewmodel.compose.viewModel
import com.game.needleinsert.utils.UserManager
import com.game.needleinsert.viewmodel.SettingsViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onBack: () -> Unit,
    viewModel: SettingsViewModel = viewModel()
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadUserInfo()
        viewModel.loadUserStats()
        viewModel.loadWithdrawHistory()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF1e3c72),
                        Color(0xFF2a5298)
                    )
                )
            )
    ) {
        // 顶部导航栏
        TopAppBar(
            title = { 
                Text(
                    "个人设置", 
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                ) 
            },
            navigationIcon = {
                IconButton(onClick = onBack) {
                    Icon(
                        Icons.Default.ArrowBack, 
                        contentDescription = "返回",
                        tint = Color.White
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.Transparent
            )
        )
        
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 用户信息卡片
            item {
                UserInfoCard(
                    userInfo = uiState.userInfo,
                    isLoading = uiState.isLoading
                )
            }
            
            // 设备信息卡片
            item {
                DeviceInfoCard()
            }
            
            // 游戏统计卡片
            item {
                GameStatsCard(
                    gameStats = uiState.gameStats,
                    isLoading = uiState.isLoading
                )
            }
            
            // 提现历史卡片
            item {
                WithdrawHistoryCard(
                    withdrawHistory = uiState.withdrawHistory,
                    isLoading = uiState.isLoading
                )
            }
            
            // 其他设置
            item {
                OtherSettingsCard(
                    onClearCache = { viewModel.clearCache() },
                    onLogout = { 
                        viewModel.logout()
                        onBack()
                    }
                )
            }
        }
    }
}

@Composable
fun UserInfoCard(
    userInfo: com.game.needleinsert.model.User?,
    isLoading: Boolean
) {
    SettingsCard(
        title = "用户信息",
        icon = Icons.Default.Person
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.primary
            )
        } else if (userInfo != null) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                InfoRow("用户ID", userInfo.id)
                InfoRow("昵称", userInfo.nickname)
                InfoRow("等级", "Lv.${userInfo.level}")
                InfoRow("金币余额", "${userInfo.coins} 枚")
            }
        } else {
            Text("未登录", color = Color.Gray)
        }
    }
}

@Composable
fun DeviceInfoCard() {
    val context = LocalContext.current
    val deviceId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID) ?: "unknown"
    val deviceName = "${Build.MANUFACTURER} ${Build.MODEL}"
    val androidVersion = "Android ${Build.VERSION.RELEASE}"
    val appVersion = try {
        val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
        packageInfo.versionName ?: "未知"
    } catch (e: Exception) {
        "未知"
    }
    
    SettingsCard(
        title = "设备信息",
        icon = Icons.Default.Phone
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            InfoRow("设备ID", deviceId.take(8) + "***")
            InfoRow("设备型号", deviceName)
            InfoRow("系统版本", androidVersion)
            InfoRow("应用版本", appVersion)
        }
    }
}

@Composable
fun GameStatsCard(
    gameStats: SettingsViewModel.GameStats?,
    isLoading: Boolean
) {
    SettingsCard(
        title = "游戏统计",
        icon = Icons.Default.Star
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.primary
            )
        } else if (gameStats != null) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                InfoRow("游戏次数", "${gameStats.gameCount} 次")
                InfoRow("最高分", "${gameStats.bestScore} 分")
                InfoRow("平均分", "${gameStats.averageScore} 分")
                InfoRow("总观看广告", "${gameStats.adsWatched} 次")
                InfoRow("总获得金币", "${gameStats.totalCoins} 枚")
            }
        } else {
            Text("暂无数据", color = Color.Gray)
        }
    }
}

@Composable
fun WithdrawHistoryCard(
    withdrawHistory: List<SettingsViewModel.WithdrawRecord>,
    isLoading: Boolean
) {
    SettingsCard(
        title = "提现记录",
        icon = Icons.Default.List
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.primary
            )
        } else if (withdrawHistory.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                withdrawHistory.take(3).forEach { record ->
                    WithdrawRecordItem(record)
                }
                if (withdrawHistory.size > 3) {
                    Text(
                        "还有 ${withdrawHistory.size - 3} 条记录...",
                        color = Color.Gray,
                        fontSize = 12.sp
                    )
                }
            }
        } else {
            Text("暂无提现记录", color = Color.Gray)
        }
    }
}

@Composable
fun WithdrawRecordItem(record: SettingsViewModel.WithdrawRecord) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                "¥${record.amount}",
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp
            )
            Text(
                record.requestTime,
                color = Color.Gray,
                fontSize = 12.sp
            )
        }
        
        StatusBadge(record.status)
    }
}

@Composable
fun StatusBadge(status: String) {
    val (color, text) = when (status) {
        "PENDING" -> Color(0xFFFFA726) to "待处理"
        "COMPLETED" -> Color(0xFF66BB6A) to "已完成"
        "REJECTED" -> Color(0xFFEF5350) to "已拒绝"
        else -> Color.Gray to "未知"
    }
    
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            color = color,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun OtherSettingsCard(
    onClearCache: () -> Unit,
    onLogout: () -> Unit
) {
    SettingsCard(
        title = "其他设置",
        icon = Icons.Default.Settings
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            SettingsButton(
                text = "清除缓存",
                icon = Icons.Default.Delete,
                onClick = onClearCache
            )
            
            SettingsButton(
                text = "退出登录",
                icon = Icons.Default.ExitToApp,
                onClick = onLogout,
                isDestructive = true
            )
        }
    }
}

@Composable
fun SettingsCard(
    title: String,
    icon: ImageVector,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.95f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 16.dp)
            ) {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = Color(0xFF2a5298),
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    title,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF2a5298)
                )
            }
            
            content()
        }
    }
}

@Composable
fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            label,
            color = Color.Gray,
            fontSize = 14.sp
        )
        Text(
            value,
            fontWeight = FontWeight.Medium,
            fontSize = 14.sp
        )
    }
}

@Composable
fun SettingsButton(
    text: String,
    icon: ImageVector,
    onClick: () -> Unit,
    isDestructive: Boolean = false
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = if (isDestructive) Color.Red else Color(0xFF2a5298)
        ),
        border = ButtonDefaults.outlinedButtonBorder.copy(
            width = 1.dp
        )
    ) {
        Icon(
            icon,
            contentDescription = null,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(text)
    }
}
