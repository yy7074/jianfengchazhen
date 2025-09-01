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
import com.game.needleinsert.viewmodel.WithdrawViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WithdrawScreen(
    onBack: () -> Unit,
    viewModel: WithdrawViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadUserInfo()
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
                    onSubmit = { viewModel.submitWithdrawRequest() },
                    isLoading = uiState.isSubmitting,
                    canSubmit = uiState.canSubmit,
                    withdrawableAmount = uiState.withdrawableAmount
                )
            }
            
            // 提现规则说明
            item {
                WithdrawRulesCard()
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
        
        // 提示信息
        if (uiState.message != null) {
            LaunchedEffect(uiState.message) {
                // 这里可以显示 SnackBar 或 Toast
            }
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
    withdrawableAmount: Double
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
            
            val withdrawOptions = listOf(0.5, 15.0, 30.0)
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
                        Text("¥$amount")
                    }
                }
            }
            
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
fun WithdrawRulesCard() {
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
                "提现金额：¥0.5、¥15、¥30三个固定选项",
                "每天只能提现一次",
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
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            color = color,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium
        )
    }
}
