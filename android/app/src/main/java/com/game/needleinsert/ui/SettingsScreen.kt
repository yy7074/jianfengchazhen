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
import com.game.needleinsert.utils.VersionManager
import com.game.needleinsert.utils.ApkInstaller
import com.game.needleinsert.ui.components.UpdateDialog
import com.game.needleinsert.viewmodel.SettingsViewModel
import java.text.SimpleDateFormat
import java.util.*
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope
import android.util.Log

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
        // 游戏统计和提现历史已移除
        // viewModel.loadUserStats()
        // viewModel.loadWithdrawHistory()
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
            
            // 游戏统计卡片已移除
            /*
            item {
                GameStatsCard(
                    gameStats = uiState.gameStats,
                    isLoading = uiState.isLoading
                )
            }
            */
            
            // 金币获取记录卡片
            item {
                CoinRecordsCard(
                    coinRecords = uiState.coinRecords,
                    isLoading = uiState.isLoading
                )
            }
            
            // 提现历史卡片已移除
            /*
            item {
                WithdrawHistoryCard(
                    withdrawHistory = uiState.withdrawHistory,
                    isLoading = uiState.isLoading
                )
            }
            */
            
            // 版本信息
            item {
                VersionInfoCard()
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
                // 等级信息已隐藏
                // InfoRow("等级", "Lv.${userInfo.level}")
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
fun CoinRecordsCard(
    coinRecords: List<SettingsViewModel.CoinRecord>,
    isLoading: Boolean
) {
    SettingsCard(
        title = "金币获取记录",
        icon = Icons.Default.Star
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.primary
            )
        } else if (coinRecords.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                coinRecords.take(5).forEach { record ->
                    CoinRecordItem(record)
                }
                if (coinRecords.size > 5) {
                    Text(
//                        "还有${coinRecords.size - 5}条记录",
                        "",
                        color = Color.Gray,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
            }
        } else {
            Text("暂无金币获取记录", color = Color.Gray)
        }
    }
}

@Composable
fun CoinRecordItem(record: SettingsViewModel.CoinRecord) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = record.description,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = record.createdAt,
                fontSize = 12.sp,
                color = Color.Gray
            )
        }
        Text(
            text = "+${record.amount}",
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            color = if (record.amount > 0) Color(0xFF4CAF50) else Color(0xFFF44336)
        )
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

@Composable
fun VersionInfoCard() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    // 版本更新状态
    var showUpdateDialog by remember { mutableStateOf(false) }
    var updateVersionInfo by remember { mutableStateOf<com.game.needleinsert.model.AppVersionInfo?>(null) }
    var isForceUpdate by remember { mutableStateOf(false) }
    var isCheckingUpdate by remember { mutableStateOf(false) }
    var updateMessage by remember { mutableStateOf("") }
    var isDownloading by remember { mutableStateOf(false) }
    var downloadProgress by remember { mutableStateOf(0) }
    var pendingApkFile by remember { mutableStateOf<java.io.File?>(null) }
    
    // 获取当前版本信息
    val (currentVersionName, currentVersionCode) = VersionManager.getCurrentVersionInfo(context)
    
    // 监听窗口焦点变化，处理从设置页面返回后的安装
    DisposableEffect(Unit) {
        val callback = object : android.view.ViewTreeObserver.OnWindowFocusChangeListener {
            override fun onWindowFocusChanged(hasFocus: Boolean) {
                if (hasFocus && pendingApkFile != null) {
                    Log.d("InstallPermission", "窗口获得焦点，检查安装权限")
                    if (ApkInstaller.canInstallUnknownApps(context)) {
                        Log.d("InstallPermission", "权限已授予，立即安装APK")
                        val apkFile = pendingApkFile!!
                        pendingApkFile = null  // 先清空，避免重复安装
                        
                        val success = ApkInstaller.installApk(context, apkFile)
                        if (success) {
                            showUpdateDialog = false
                            updateMessage = "安装包已启动，请按提示完成安装"
                        } else {
                            updateMessage = "启动安装失败，请重试"
                        }
                    } else {
                        Log.d("InstallPermission", "权限未授予，继续等待")
                    }
                }
            }
        }
        
        // 获取根视图并添加监听器
        val view = (context as? android.app.Activity)?.window?.decorView
        view?.viewTreeObserver?.addOnWindowFocusChangeListener(callback)
        
        onDispose {
            view?.viewTreeObserver?.removeOnWindowFocusChangeListener(callback)
        }
    }
    
    SettingsCard(
        title = "版本信息",
        icon = Icons.Default.Info
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            // 当前版本信息
            InfoRow("应用名称", "见缝插针")
            InfoRow("当前版本", "v$currentVersionName")
            InfoRow("版本号", currentVersionCode.toString())
            InfoRow("系统版本", "Android ${Build.VERSION.RELEASE}")
            InfoRow("设备型号", "${Build.MANUFACTURER} ${Build.MODEL}")
            
            // 更新状态显示
            if (updateMessage.isNotEmpty()) {
                Text(
                    text = updateMessage,
                    fontSize = 12.sp,
                    color = if (updateMessage.contains("最新")) Color.Green else Color.Blue,
                    modifier = Modifier.padding(vertical = 4.dp)
                )
            }
            
            // 检查更新按钮
            SettingsButton(
                text = if (isCheckingUpdate) "检查中..." else "检查更新",
                icon = Icons.Default.Refresh,
                onClick = {
                    if (!isCheckingUpdate) {
                        isCheckingUpdate = true
                        updateMessage = ""
                        
                        coroutineScope.launch {
                            try {
                                Log.d("VersionCheck", "手动检查版本更新...")
                                val versionCheckResult = VersionManager.checkVersionUpdate(context)
                                
                                versionCheckResult?.let { result ->
                                    if (result.hasUpdate && result.latestVersion != null) {
                                        Log.d("VersionCheck", "发现新版本: ${result.latestVersion.versionName}")
                                        updateVersionInfo = result.latestVersion
                                        isForceUpdate = result.isForceUpdate
                                        showUpdateDialog = true
                                        updateMessage = "发现新版本 v${result.latestVersion.versionName}"
                                    } else {
                                        Log.d("VersionCheck", "当前已是最新版本")
                                        updateMessage = "当前已是最新版本"
                                    }
                                } ?: run {
                                    updateMessage = "检查更新失败，请稍后重试"
                                }
                            } catch (e: Exception) {
                                Log.e("VersionCheck", "版本检查失败", e)
                                updateMessage = "检查更新失败: ${e.message}"
                            } finally {
                                isCheckingUpdate = false
                            }
                        }
                    }
                }
            )
        }
    }
    
    // 显示版本更新对话框
    if (showUpdateDialog && updateVersionInfo != null) {
        UpdateDialog(
            versionInfo = updateVersionInfo!!,
            isForceUpdate = isForceUpdate,
            isDownloading = isDownloading,
            downloadProgress = downloadProgress,
            onDownload = {
                coroutineScope.launch {
                    try {
                        isDownloading = true
                        downloadProgress = 0
                        val fileName = updateVersionInfo!!.fileName ?: "update_${updateVersionInfo!!.versionName}.apk"
                        val downloadUrl = if (updateVersionInfo!!.downloadUrl.startsWith("http")) {
                            Log.d("UpdateDownload", "使用完整URL: ${updateVersionInfo!!.downloadUrl}")
                            updateVersionInfo!!.downloadUrl
                        } else {
                            val baseUrl = com.game.needleinsert.config.AppConfig.Network.BASE_URL
                            val path = updateVersionInfo!!.downloadUrl
                            val fullUrl = if (baseUrl.endsWith("/") || path.startsWith("/")) {
                                baseUrl + path
                            } else {
                                "$baseUrl/$path"
                            }
                            Log.d("UpdateDownload", "构造完整URL: baseUrl=$baseUrl, path=$path, fullUrl=$fullUrl")
                            fullUrl
                        }
                        
                        Log.d("UpdateDownload", "开始下载APK: $downloadUrl")
                        
                        val apkFile = ApkInstaller.downloadApk(
                            context = context,
                            downloadUrl = downloadUrl,
                            fileName = fileName,
                            onProgress = { progress ->
                                downloadProgress = progress
                                Log.d("UpdateDownload", "下载进度: $progress%")
                            }
                        )
                        
                        isDownloading = false
                        
                        if (apkFile != null) {
                            Log.d("UpdateDownload", "下载完成，开始安装")
                            
                            // 检查安装权限
                            if (ApkInstaller.canInstallUnknownApps(context)) {
                                Log.d("UpdateDownload", "已有安装权限，直接安装")
                                val success = ApkInstaller.installApk(context, apkFile)
                                if (success) {
                                    showUpdateDialog = false
                                    updateMessage = "安装包已启动，请按提示完成安装"
                                } else {
                                    updateMessage = "启动安装失败，请重试"
                                }
                            } else {
                                Log.w("UpdateDownload", "需要安装未知来源应用权限")
                                // 保存APK文件路径到SharedPreferences，权限授权后恢复安装
                                ApkInstaller.savePendingApkPath(context, apkFile)
                                pendingApkFile = apkFile
                                updateMessage = "正在请求安装权限，请授权后返回APP..."

                                // 请求权限
                                ApkInstaller.requestInstallPermission(context)
                                
                                // 延迟检查，给用户时间授权
                                coroutineScope.launch {
                                    kotlinx.coroutines.delay(500) // 等待500ms
                                    var retryCount = 0
                                    while (retryCount < 30 && pendingApkFile != null) {  // 最多等30秒
                                        kotlinx.coroutines.delay(1000)
                                        if (ApkInstaller.canInstallUnknownApps(context)) {
                                            Log.d("InstallPermission", "检测到权限已授予，立即安装")
                                            val apk = pendingApkFile
                                            pendingApkFile = null
                                            if (apk != null) {
                                                val success = ApkInstaller.installApk(context, apk)
                                                if (success) {
                                                    ApkInstaller.clearPendingApkPath(context)
                                                    showUpdateDialog = false
                                                    updateMessage = "安装包已启动，请按提示完成安装"
                                                } else {
                                                    updateMessage = "启动安装失败"
                                                }
                                            }
                                            break
                                        }
                                        retryCount++
                                    }
                                }
                            }
                        } else {
                            Log.e("UpdateDownload", "下载失败")
                            updateMessage = "下载失败，请稍后重试"
                        }
                        
                    } catch (e: Exception) {
                        Log.e("UpdateDownload", "下载或安装失败", e)
                        isDownloading = false
                        
                        // 显示用户友好的错误提示
                        updateMessage = when {
                            e.message?.contains("MalformedURLException") == true -> "下载链接格式错误，请稍后重试"
                            e.message?.contains("UnknownHostException") == true -> "网络连接失败，请检查网络连接"
                            e.message?.contains("SocketTimeoutException") == true -> "下载超时，请重试"
                            e.message?.contains("FileNotFoundException") == true -> "文件不存在，请联系管理员"
                            else -> "下载失败: ${e.message}"
                        }
                    }
                }
            },
            onCancel = {
                if (!isForceUpdate) {
                    showUpdateDialog = false
                }
            },
            onDismiss = {
                if (!isForceUpdate) {
                    showUpdateDialog = false
                }
            }
        )
    }
}
