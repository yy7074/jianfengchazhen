package com.game.needleinsert.ui.components

import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import com.game.needleinsert.model.AdConfig
import kotlinx.coroutines.delay

@Composable
fun WebpageAdPlayer(
    adConfig: AdConfig,
    onAdStarted: () -> Unit = {},
    onAdCompleted: (Boolean) -> Unit,
    onAdClosed: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var showWebView by remember { mutableStateOf(false) }
    var countdown by remember { mutableStateOf(adConfig.duration) }
    var canSkip by remember { mutableStateOf(false) }
    var webViewStarted by remember { mutableStateOf(false) }
    
    // 倒计时逻辑
    LaunchedEffect(countdown, webViewStarted) {
        if (webViewStarted && countdown > 0) {
            delay(1000)
            countdown--
            if (countdown <= adConfig.duration - adConfig.skipTime) {
                canSkip = true
            }
        } else if (webViewStarted && countdown <= 0) {
            // 倒计时结束，自动完成
            onAdCompleted(true)
        }
    }
    
    // 自动显示WebView
    LaunchedEffect(Unit) {
        showWebView = true
        webViewStarted = true
        onAdStarted() // 通知广告开始
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Color.Black)
    ) {
        // 直接显示WebView
        if (showWebView) {
            AndroidView(
                factory = { context ->
                    WebView(context).apply {
                        webViewClient = WebViewClient()
                        settings.javaScriptEnabled = true
                        settings.domStorageEnabled = true
                        settings.allowFileAccess = false
                        settings.allowContentAccess = false
                        loadUrl(adConfig.webpageUrl)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }
        
        // 顶部控制栏（悬浮在WebView上方）
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .background(
                    Color.Black.copy(alpha = 0.7f),
                    shape = RoundedCornerShape(8.dp)
                )
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 左侧：广告信息
            Column {
                Text(
                    text = "📱 ${adConfig.title}",
                    color = Color.White,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "💰 观看获得 ${adConfig.getDisplayRewardCoins()} 金币",
                    color = Color(0xFFFFD700),
                    fontSize = 12.sp
                )
            }
            
            // 右侧：倒计时和按钮
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // 倒计时显示
                if (webViewStarted) {
                    Text(
                        text = if (countdown > 0) "${countdown}s" else "完成",
                        color = if (countdown > 0) Color.White else Color(0xFF4CAF50),
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                // 跳过/关闭按钮
                if (canSkip || countdown <= 0) {
                    Button(
                        onClick = {
                            if (countdown <= 0) {
                                onAdCompleted(true)
                            } else {
                                onAdCompleted(false) // 跳过
                            }
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (countdown <= 0) Color(0xFF4CAF50) else Color(0xFFFF5722)
                        ),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.height(32.dp)
                    ) {
                        Text(
                            text = if (countdown <= 0) "关闭" else "跳过",
                            color = Color.White,
                            fontSize = 12.sp
                        )
                    }
                }
            }
        }
    }
}
