package com.game.needleinsert.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.platform.LocalContext
import android.content.Context
import android.util.Log
import com.game.needleinsert.utils.ConfigManager
import com.game.needleinsert.viewmodel.WithdrawViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WithdrawScreen(
    onBack: () -> Unit,
    viewModel: WithdrawViewModel = viewModel()
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    
    // 应用配置状态（与后端保持一致）
    var minWithdrawAmount by remember { mutableStateOf(10.0) }
    var maxWithdrawAmount by remember { mutableStateOf(500.0) }
    var coinToRmbRate by remember { mutableStateOf(33000) }
    var dailyWithdrawLimit by remember { mutableStateOf(1) }
    
    LaunchedEffect(Unit) {
        viewModel.loadUserInfo(context)
        viewModel.loadWithdrawHistory()
        
        // 强制刷新配置以确保获取最新值
        try {
            Log.d("WithdrawScreen", "开始强制刷新配置...")
            // 先清除缓存，确保获取最新配置
            ConfigManager.clearCache(context)
            ConfigManager.refreshConfig(context)?.let { config ->
                Log.d("WithdrawScreen", "配置刷新成功: minWithdraw=${config.minWithdrawAmount}, maxWithdraw=${config.maxWithdrawAmount}, dailyLimit=${config.dailyWithdrawLimit}")
                minWithdrawAmount = config.minWithdrawAmount
                maxWithdrawAmount = config.maxWithdrawAmount
                coinToRmbRate = config.coinToRmbRate
                dailyWithdrawLimit = config.dailyWithdrawLimit
            } ?: run {
                Log.w("WithdrawScreen", "配置刷新失败，使用默认配置获取")
                minWithdrawAmount = ConfigManager.getMinWithdrawAmount(context)
                maxWithdrawAmount = ConfigManager.getMaxWithdrawAmount(context)
                coinToRmbRate = ConfigManager.getCoinToRmbRate(context)
                dailyWithdrawLimit = ConfigManager.getDailyWithdrawLimit(context)
            }
            Log.d("WithdrawScreen", "最终配置: minWithdraw=$minWithdrawAmount, maxWithdraw=$maxWithdrawAmount, coinRate=$coinToRmbRate, dailyLimit=$dailyWithdrawLimit")
        } catch (e: Exception) {
            Log.e("WithdrawScreen", "配置加载异常，使用默认值", e)
            // 使用默认值
        }
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
                    "金币提现", 
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
            // 余额信息卡片
            item {
                BalanceCard(
                    currentCoins = uiState.currentCoins,
                    withdrawableAmount = uiState.withdrawableAmount,
                    exchangeRateText = uiState.exchangeRateText
                )
            }
            
            // 提现申请卡片
            item {
                WithdrawRequestCard(
                    selectedAmount = uiState.selectedAmount,
                    onAmountSelect = { viewModel.selectWithdrawAmount(it) },
                    alipayAccount = uiState.alipayAccount,
                    onAlipayAccountChange = { viewModel.updateAlipayAccount(it) },
                    realName = uiState.realName,
                    onRealNameChange = { viewModel.updateRealName(it) },
                    onSubmit = { viewModel.submitWithdrawRequest(context) },
                    isLoading = uiState.isSubmitting,
                    canSubmit = uiState.canSubmit,
                    withdrawableAmount = uiState.withdrawableAmount,
                    minWithdrawAmount = minWithdrawAmount,
                    maxWithdrawAmount = maxWithdrawAmount
                )
            }
            
            // 提现规则说明
            item {
                WithdrawRulesCard(
                    minWithdrawAmount = minWithdrawAmount,
                    maxWithdrawAmount = maxWithdrawAmount,
                    dailyWithdrawLimit = dailyWithdrawLimit
                )
            }
            
            // 提现历史
            item {
                WithdrawHistoryCard(
                    history = uiState.withdrawHistory,
                    isLoading = uiState.isLoading,
                    onRefresh = { viewModel.loadWithdrawHistory() }
                )
            }
        }
        
        // 错误信息显示
        if (uiState.error != null) {
            AlertDialog(
                onDismissRequest = { viewModel.clearError() },
                title = { Text("提示") },
                text = { Text(uiState.error!!) },
                confirmButton = {
                    TextButton(onClick = { viewModel.clearError() }) {
                        Text("确定")
                    }
                }
            )
        }
        
        // 成功信息显示
        if (uiState.message != null) {
            AlertDialog(
                onDismissRequest = { viewModel.clearMessage() },
                title = { Text("提示") },
                text = { Text(uiState.message!!) },
                confirmButton = {
                    TextButton(onClick = { viewModel.clearMessage() }) {
                        Text("确定")
                    }
                }
            )
        }
    }
}

@Composable
fun BalanceCard(
    currentCoins: Int,
    withdrawableAmount: Double,
    exchangeRateText: String = "33000金币 ≈ ¥1.00"
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
                    Icons.Default.AccountBox,
                    contentDescription = null,
                    tint = Color(0xFF2a5298),
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    "我的余额",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF2a5298)
                )
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        "当前金币",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                    Text(
                        "$currentCoins 枚",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2a5298)
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        "可提现金额",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                    Text(
                        "¥${String.format("%.2f", withdrawableAmount)}",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF10b981)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                "兑换比例：$exchangeRateText",
                fontSize = 12.sp,
                color = Color.Gray
            )
        }
    }
}

@Composable
fun WithdrawRequestCard(
    selectedAmount: Double?,
    onAmountSelect: (Double) -> Unit,
    alipayAccount: String,
    onAlipayAccountChange: (String) -> Unit,
    realName: String,
    onRealNameChange: (String) -> Unit,
    onSubmit: () -> Unit,
    isLoading: Boolean,
    canSubmit: Boolean,
    withdrawableAmount: Double,
    minWithdrawAmount: Double,
    maxWithdrawAmount: Double
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
                    Icons.Default.Send,
                    contentDescription = null,
                    tint = Color(0xFF2a5298),
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    "申请提现",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF2a5298)
                )
            }
            
            // 提现金额选择
            Text(
                "选择提现金额",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = Color.Gray,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            // 固定提现金额选项：0.5元、15元、30元
            val withdrawOptions: List<Double> = listOf(0.5, 15.0, 30.0)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                withdrawOptions.forEach { amount ->
                    val isSelected = selectedAmount == amount
                    val isEnabled = amount <= withdrawableAmount
                    
                    OutlinedButton(
                        onClick = { onAmountSelect(amount) },
                        enabled = isEnabled,
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (isSelected) Color(0xFF2a5298) else Color.Transparent,
                            contentColor = if (isSelected) Color.White else Color(0xFF2a5298),
                            disabledContentColor = Color.Gray
                        ),
                        border = androidx.compose.foundation.BorderStroke(
                            1.dp, 
                            if (isSelected) Color(0xFF2a5298) 
                            else if (isEnabled) Color(0xFF2a5298) 
                            else Color.Gray
                        ),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            if (amount == amount.toInt().toDouble()) {
                                "¥${amount.toInt()}"
                            } else {
                                "¥$amount"
                            }
                        )
                    }
                }
            }
            
            
            // 自定义金额输入已隐藏
            // 用户只能从固定的 0.5、15、30 元三个金额中选择
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 支付宝账号
            OutlinedTextField(
                value = alipayAccount,
                onValueChange = onAlipayAccountChange,
                label = { Text("支付宝账号") },
                placeholder = { Text("请输入支付宝账号/手机号") },
                leadingIcon = {
                    Icon(Icons.Default.Phone, contentDescription = null)
                },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // 真实姓名
            OutlinedTextField(
                value = realName,
                onValueChange = onRealNameChange,
                label = { Text("真实姓名") },
                placeholder = { Text("请输入支付宝实名认证姓名") },
                leadingIcon = {
                    Icon(Icons.Default.Person, contentDescription = null)
                },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            
            Spacer(modifier = Modifier.height(20.dp))
            
            // 提交按钮
            Button(
                onClick = onSubmit,
                enabled = canSubmit && !isLoading,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF2a5298)
                )
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                }
                Text(
                    if (isLoading) "提交中..." else "提交申请",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
fun WithdrawRulesCard(
    minWithdrawAmount: Double,
    maxWithdrawAmount: Double,
    dailyWithdrawLimit: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFF8F9FA)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 12.dp)
            ) {
                Icon(
                    Icons.Default.Info,
                    contentDescription = null,
                    tint = Color(0xFF2a5298),
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "提现规则",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF2a5298)
                )
            }
            
            val rules = listOf(
                "提现金额：¥${String.format("%.1f", minWithdrawAmount)}起，最高¥${String.format("%.0f", maxWithdrawAmount)}",
                if (dailyWithdrawLimit == 1) "每天只能提现一次" else "每天最多可提现${dailyWithdrawLimit}次",
                "工作日1-3个工作日到账"
            )
            
            rules.forEach { rule ->
                Row(
                    modifier = Modifier.padding(vertical = 2.dp)
                ) {
                    Text(
                        "• ",
                        fontSize = 14.sp,
                        color = Color(0xFF2a5298)
                    )
                    Text(
                        rule,
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
fun WithdrawHistoryCard(
    history: List<WithdrawViewModel.WithdrawRecord>,
    isLoading: Boolean,
    onRefresh: () -> Unit
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
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.List,
                        contentDescription = null,
                        tint = Color(0xFF2a5298),
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        "提现历史",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2a5298)
                    )
                }
                
                IconButton(onClick = onRefresh) {
                    Icon(
                        Icons.Default.Refresh,
                        contentDescription = "刷新",
                        tint = Color(0xFF2a5298)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (isLoading) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = Color(0xFF2a5298))
                }
            } else if (history.isEmpty()) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        "📋",
                        fontSize = 32.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "暂无提现记录",
                        fontSize = 16.sp,
                        color = Color.Gray
                    )
                }
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    history.forEach { record ->
                        WithdrawHistoryItem(record = record)
                    }
                }
            }
        }
    }
}

@Composable
fun WithdrawHistoryItem(record: WithdrawViewModel.WithdrawRecord) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFF8F9FA)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
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
            
            WithdrawStatusBadge(status = record.status)
        }
    }
}

@Composable
fun WithdrawStatusBadge(status: String) {
    val (color, text) = when (status.lowercase()) {
        "pending" -> Color(0xFFFFA726) to "审核中"
        "approved" -> Color(0xFF66BB6A) to "已打款"
        "completed" -> Color(0xFF66BB6A) to "已打款"
        "rejected" -> Color(0xFFEF5350) to "已拒绝"
        else -> Color.Gray to "未知($status)"
    }
    
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            color = color,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium
        )
    }
}
