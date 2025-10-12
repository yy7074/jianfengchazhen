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
import com.game.needleinsert.ui.SettingsScreen
import com.game.needleinsert.ui.LeaderboardScreen
import com.game.needleinsert.ui.WithdrawScreen
import com.game.needleinsert.ui.UserProfileScreen
import com.game.needleinsert.ui.LoginScreen
import com.game.needleinsert.ui.CoinRecordsScreen
import com.game.needleinsert.ui.theme.NeedleInsertTheme
import com.game.needleinsert.ui.theme.GameColors
import com.game.needleinsert.ui.components.AnimatedBackground
import com.game.needleinsert.ui.components.PulsingButton
import com.game.needleinsert.ui.FullScreenAdActivity
import com.game.needleinsert.model.AdConfig
import androidx.activity.result.contract.ActivityResultContracts
import android.app.Activity
import android.content.Intent
import androidx.compose.ui.platform.LocalContext
import com.game.needleinsert.utils.UserManager
import com.game.needleinsert.utils.AppTimeLimitManager
import com.game.needleinsert.utils.VersionManager
import com.game.needleinsert.utils.ApkInstaller
import com.game.needleinsert.viewmodel.UserViewModel
import com.game.needleinsert.model.User
import kotlinx.coroutines.launch
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.border
import androidx.compose.ui.draw.clip
import androidx.lifecycle.lifecycleScope
import com.game.needleinsert.ui.TimeLimitDialog
import com.game.needleinsert.ui.components.UpdateDialog
import com.game.needleinsert.config.AppConfig
import com.game.needleinsert.model.AppVersionInfo
import android.net.Uri
import android.util.Log
import androidx.compose.runtime.rememberCoroutineScope

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // 初始化用户管理器和时间限制管理器
        UserManager.init(this)
        AppTimeLimitManager.init(this)
        
        setContent {
            NeedleInsertTheme {
                MainNavigation()
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        // 每次应用恢复时检查时间限制
        // 时间限制检查已移至MainNavigation中的LaunchedEffect
    }
}

@Composable
fun MainNavigation() {
    val context = LocalContext.current
    // 添加登录状态管理
    val userViewModel: UserViewModel = viewModel()
    val userState by userViewModel.uiState.collectAsState()
    var currentScreen by remember { mutableStateOf("login") }
    
    // 时间限制状态管理
    var showTimeLimitDialog by remember { mutableStateOf(false) }
    
    // 版本更新状态管理
    var showUpdateDialog by remember { mutableStateOf(false) }
    var updateVersionInfo by remember { mutableStateOf<AppVersionInfo?>(null) }
    var isForceUpdate by remember { mutableStateOf(false) }
    var downloadProgress by remember { mutableStateOf(0) }
    var isDownloading by remember { mutableStateOf(false) }
    var pendingApkFile by remember { mutableStateOf<java.io.File?>(null) }
    
    val coroutineScope = rememberCoroutineScope()
    
    // 检查时间限制 - 持续监控
    LaunchedEffect(Unit) {
        // 初始化时间限制管理器（不清除数据，保持持久化）
        AppTimeLimitManager.init(context)
        
        // 首次启动时输出详细信息
        Log.d("TimeLimitCheck", "=== 时间限制检查开始 ===")
        Log.d("TimeLimitCheck", AppTimeLimitManager.getInstallTimeInfo())
        Log.d("TimeLimitCheck", "时间限制启用: ${AppTimeLimitManager.isTimeLimitEnabled()}")
        Log.d("TimeLimitCheck", "开始持续监控...")
        
        // 持续检查时间限制
        while (true) {
            val isExceeded = AppTimeLimitManager.isTimeLimitExceeded()
            val remainingTime = AppTimeLimitManager.getRemainingTimeSeconds()
            
            // 只在剩余时间较少时输出日志
            if (remainingTime <= 10) {
                Log.d("TimeLimitCheck", "剩余时间: ${remainingTime}秒")
            }
            
            if (isExceeded) {
                Log.d("TimeLimitCheck", "时间已到期，显示限制弹窗")
                showTimeLimitDialog = true
                break // 显示弹窗后停止检查
            }
            
            // 每秒检查一次
            kotlinx.coroutines.delay(1000)
        }
    }
    
    // 检查版本更新
    LaunchedEffect(Unit) {
        try {
            Log.d("VersionCheck", "开始检查版本更新...")
            val versionCheckResult = VersionManager.checkVersionUpdate(context)
            
            versionCheckResult?.let { result ->
                if (result.hasUpdate && result.latestVersion != null) {
                    Log.d("VersionCheck", "发现新版本: ${result.latestVersion.versionName}")
                    updateVersionInfo = result.latestVersion
                    isForceUpdate = result.isForceUpdate
                    showUpdateDialog = true
                } else {
                    Log.d("VersionCheck", "当前已是最新版本")
                }
            }
        } catch (e: Exception) {
            Log.e("VersionCheck", "版本检查失败", e)
        }
    }
    
    // 监听权限状态变化，处理权限授权后的安装
    LaunchedEffect(pendingApkFile) {
        pendingApkFile?.let { apkFile ->
            // 定期检查权限状态，直到获得权限或用户取消
            while (pendingApkFile != null) {
                if (ApkInstaller.canInstallUnknownApps(context)) {
                    Log.d("InstallPermission", "权限已授予，继续安装APK")
                    val success = ApkInstaller.installApk(context, apkFile)
                    if (success) {
                        showUpdateDialog = false
                    }
                    pendingApkFile = null
                    break
                }
                // 每秒检查一次权限状态
                kotlinx.coroutines.delay(1000)
            }
        }
    }
    
    // 启动时自动登录
    LaunchedEffect(Unit) {
        UserManager.init(context)
        val currentUser = UserManager.getCurrentUser()
        if (currentUser != null && currentUser.id.isNotBlank()) {
            // 如果本地有有效的用户信息，加载到ViewModel并跳转主页
            userViewModel.loadUserInfo()
            currentScreen = "menu"
        } else {
            // 清除无效的本地数据并自动尝试注册/登录
            if (currentUser != null && currentUser.id.isBlank()) {
                UserManager.logout() // 清除无效数据
            }
            userViewModel.autoLogin(context)
        }
    }
    
    // 监听用户登录状态变化
    LaunchedEffect(userState.user) {
        if (userState.user != null) {
            currentScreen = "menu"
        }
    }
    
    // 显示时间限制弹窗
    if (showTimeLimitDialog) {
        TimeLimitDialog(
            onContactDeveloper = {
                // 打开联系开发者的方式（邮件）
                val intent = Intent(Intent.ACTION_VIEW).apply {
                    data = Uri.parse("mailto:${AppConfig.TimeLimits.DEVELOPER_EMAIL}?subject=应用授权咨询&body=您好，我希望获取应用的完整版本授权。")
                }
                try {
                    context.startActivity(intent)
                } catch (e: Exception) {
                    // 如果没有邮件应用，尝试其他方式
                    val fallbackIntent = Intent(Intent.ACTION_SEND).apply {
                        type = "text/plain"
                        putExtra(Intent.EXTRA_EMAIL, arrayOf(AppConfig.TimeLimits.DEVELOPER_EMAIL))
                        putExtra(Intent.EXTRA_SUBJECT, "应用授权咨询")
                        putExtra(Intent.EXTRA_TEXT, "您好，我希望获取应用的完整版本授权。")
                    }
                    try {
                        context.startActivity(Intent.createChooser(fallbackIntent, "选择邮件应用"))
                    } catch (e2: Exception) {
                        // 最后的备选方案：可以显示一个Toast或对话框显示联系方式
                    }
                }
            },
            onExit = {
                // 退出应用
                (context as? ComponentActivity)?.finish()
            }
        )
        return // 如果显示时间限制弹窗，不显示其他内容
    }
    
    // 显示版本更新弹窗
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
                            val baseUrl = AppConfig.Network.BASE_URL
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
                                val success = ApkInstaller.installApk(context, apkFile)
                                if (success) {
                                    showUpdateDialog = false
                                }
                            } else {
                                Log.w("UpdateDownload", "需要安装未知来源应用权限")
                                // 保存APK文件引用，等待权限授权后继续安装
                                pendingApkFile = apkFile
                                ApkInstaller.requestInstallPermission(context)
                            }
                        } else {
                            Log.e("UpdateDownload", "下载失败")
                        }
                        
                    } catch (e: Exception) {
                        Log.e("UpdateDownload", "下载或安装失败", e)
                        isDownloading = false
                        
                        // 显示用户友好的错误提示
                        val errorMessage = when {
                            e.message?.contains("MalformedURLException") == true -> "下载链接格式错误"
                            e.message?.contains("UnknownHostException") == true -> "网络连接失败，请检查网络"
                            e.message?.contains("SocketTimeoutException") == true -> "下载超时，请重试"
                            e.message?.contains("FileNotFoundException") == true -> "文件不存在"
                            else -> "下载失败: ${e.message}"
                        }
                        
                        // 这里可以显示Toast或者更新UI状态
                        Log.e("UpdateDownload", "用户提示: $errorMessage")
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
        
        // 如果是强制更新，不显示其他内容
        if (isForceUpdate) {
            return
        }
    }
    
    when (currentScreen) {
        "login" -> LoginScreen(
            onLoginSuccess = { currentScreen = "menu" }
        )
        "menu" -> MainMenuScreen(
            onStartGame = { currentScreen = "game" },
            onSettings = { currentScreen = "settings" },
            onLeaderboard = { currentScreen = "leaderboard" },
            onWithdraw = { currentScreen = "withdraw" },
            onProfile = { currentScreen = "profile" }
        )
        "game" -> GameScreen(
            onBackPressed = { currentScreen = "menu" }
        )
        "settings" -> SettingsScreen(
            onBack = { currentScreen = "menu" },
            onNavigateToCoinRecords = { currentScreen = "coinRecords" }
        )
        "coinRecords" -> CoinRecordsScreen(
            onBack = { currentScreen = "settings" }
        )
        // 排行榜功能已移除
        /*
        "leaderboard" -> LeaderboardScreen(
            onBack = { currentScreen = "menu" }
        )
        */
        "withdraw" -> WithdrawScreen(
            onBack = { currentScreen = "menu" }
        )
        "profile" -> UserProfileScreen(
            onBack = { currentScreen = "menu" },
            onLogout = { currentScreen = "login" }
        )
    }
}

@Composable
fun MainMenuScreen(
    onStartGame: () -> Unit,
    onSettings: () -> Unit,
    onLeaderboard: () -> Unit,
    onWithdraw: () -> Unit,
    onProfile: () -> Unit
) {
    val context = LocalContext.current
    val userViewModel: UserViewModel = viewModel()
    val userState by userViewModel.uiState.collectAsState()
    
    // 加载用户信息
    LaunchedEffect(Unit) {
        userViewModel.loadUserInfo()
    }
    
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
                modifier = Modifier.padding(bottom = 20.dp)
            )
            
            // 用户信息区域
            UserInfoCard(
                user = userState.user,
                isLoading = userState.isLoading,
                onProfileClick = onProfile,
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(30.dp))
            
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
            
            // 排行榜功能已移除
            /*
            AnimatedMenuButton(
                text = "🏆 排行榜",
                onClick = onLeaderboard,
                backgroundColor = GameColors.AccentOrange
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            */
            
            AnimatedMenuButton(
                text = "💰 提现",
                onClick = onWithdraw,
                backgroundColor = GameColors.AccentPink
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            AnimatedMenuButton(
                text = "⚙️ 设置",
                onClick = onSettings,
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
                            text = "🎯 点击屏幕从下方发射彩色数字针\n💫 针按顺序发射，每个都有独特颜色\n📊 中心显示剩余针数，底部显示发射队列\n🎪 多种关卡类型：普通、高速、反向、变速等\n🎮 游戏中观看广告获得金币奖励！\n✨ 精美的视觉效果和流畅动画",
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

@Composable
fun UserInfoCard(
    user: User?,
    isLoading: Boolean,
    onProfileClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(80.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(20.dp),
        onClick = onProfileClick
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            when {
                isLoading -> {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = GameColors.Primary,
                            strokeWidth = 2.dp
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "正在登录...",
                            fontSize = 16.sp,
                            color = GameColors.TextPrimary
                        )
                    }
                }
                user != null -> {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // 用户信息
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // 头像
                            Box(
                                modifier = Modifier
                                    .size(40.dp)
                                    .clip(CircleShape)
                                    .background(GameColors.Primary.copy(alpha = 0.2f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "🎮",
                                    fontSize = 20.sp
                                )
                            }
                            
                            Spacer(modifier = Modifier.width(12.dp))
                            
                            Column {
                                Text(
                                    text = user.nickname,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = GameColors.Primary
                                )
                                // 等级信息已隐藏
                                /*
                                Text(
                                    text = "等级 ${user.level}",
                                    fontSize = 12.sp,
                                    color = GameColors.TextSecondary
                                )
                                */
                            }
                        }
                        
                        // 金币显示
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "💰",
                                fontSize = 16.sp
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "${user.coins}",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = GameColors.AccentOrange
                            )
                            
                            Spacer(modifier = Modifier.width(8.dp))
                            
                            Text(
                                text = "👆",
                                fontSize = 12.sp,
                                color = GameColors.TextSecondary
                            )
                        }
                    }
                }
                else -> {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = "🎮",
                            fontSize = 20.sp
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "点击登录游戏",
                            fontSize = 16.sp,
                            color = GameColors.Primary,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "👆",
                            fontSize = 12.sp,
                            color = GameColors.TextSecondary
                        )
                    }
                }
            }
        }
    }
}

 