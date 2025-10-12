package com.game.needleinsert.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.game.needleinsert.viewmodel.SettingsViewModel

/**
 * 金币获取记录详情页面
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CoinRecordsScreen(
    onBack: () -> Unit,
    viewModel: SettingsViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberLazyListState()
    
    // 页面加载时获取数据
    LaunchedEffect(Unit) {
        viewModel.loadUserInfo()
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
                    "金币获取记录", 
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
        
        // 统计信息卡片
        uiState.userInfo?.let { user ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.95f)
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    horizontalArrangement = Arrangement.SpaceAround
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "${user.coins}",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFFFB800)
                        )
                        Text(
                            text = "当前金币",
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                    }
                    
                    Divider(
                        modifier = Modifier
                            .width(1.dp)
                            .height(40.dp),
                        color = Color.LightGray
                    )
                    
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "${uiState.coinRecords.size}",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF4CAF50)
                        )
                        Text(
                            text = "获取记录",
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                    }
                    
                    Divider(
                        modifier = Modifier
                            .width(1.dp)
                            .height(40.dp),
                        color = Color.LightGray
                    )
                    
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        val totalEarned = uiState.coinRecords
                            .filter { it.amount > 0 }
                            .sumOf { it.amount }
                        Text(
                            text = "$totalEarned",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF2196F3)
                        )
                        Text(
                            text = "累计获得",
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                    }
                }
            }
        }
        
        // 记录列表
        if (uiState.isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    color = Color.White,
                    strokeWidth = 3.dp
                )
            }
        } else if (uiState.coinRecords.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "💰",
                        fontSize = 48.sp
                    )
                    Text(
                        text = "暂无金币获取记录",
                        color = Color.White.copy(alpha = 0.7f),
                        fontSize = 16.sp
                    )
                }
            }
        } else {
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(uiState.coinRecords) { record ->
                    CoinRecordCard(record = record)
                }
                
                // 底部间距
                item {
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}

@Composable
fun CoinRecordCard(record: SettingsViewModel.CoinRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.95f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 左侧：描述和时间
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = record.description,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF2d3748)
                )
                Text(
                    text = record.createdAt,
                    fontSize = 12.sp,
                    color = Color.Gray
                )
            }
            
            // 右侧：金币数量
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (record.amount > 0) 
                        Color(0xFF4CAF50).copy(alpha = 0.1f)
                    else 
                        Color(0xFFF44336).copy(alpha = 0.1f)
                ),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = if (record.amount > 0) "+${record.amount}" else "${record.amount}",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (record.amount > 0) Color(0xFF4CAF50) else Color(0xFFF44336),
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }
    }
}

