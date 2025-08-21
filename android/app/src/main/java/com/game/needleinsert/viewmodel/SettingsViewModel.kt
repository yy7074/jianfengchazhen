package com.game.needleinsert.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.game.needleinsert.model.User
import com.game.needleinsert.network.RetrofitClient
import com.game.needleinsert.utils.UserManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class SettingsViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()
    
    private val apiService = RetrofitClient.getApiService()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
    
    data class SettingsUiState(
        val isLoading: Boolean = false,
        val userInfo: User? = null,
        val gameStats: GameStats? = null,
        val withdrawHistory: List<WithdrawRecord> = emptyList(),
        val error: String? = null
    )
    
    data class GameStats(
        val gameCount: Int = 0,
        val bestScore: Int = 0,
        val averageScore: Int = 0,
        val adsWatched: Int = 0,
        val totalCoins: Int = 0
    )
    
    data class WithdrawRecord(
        val id: Int,
        val amount: String,
        val status: String,
        val requestTime: String,
        val alipayAccount: String
    )
    
    fun loadUserInfo() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                val currentUser = UserManager.getCurrentUser()
                if (currentUser != null) {
                    _uiState.value = _uiState.value.copy(
                        userInfo = currentUser,
                        isLoading = false
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "用户未登录"
                    )
                }
            } catch (e: Exception) {
                Log.e("SettingsViewModel", "加载用户信息失败", e)
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "加载用户信息失败: ${e.message}"
                )
            }
        }
    }
    
    fun loadUserStats() {
        viewModelScope.launch {
            try {
                val currentUser = UserManager.getCurrentUser()
                if (currentUser == null) {
                    Log.w("SettingsViewModel", "用户未登录，无法加载统计数据")
                    return@launch
                }
                
                // 获取用户统计数据
                val response = apiService.getUserStats(currentUser.id)
                
                if (response.isSuccessful && response.body()?.code == 200) {
                    val statsData = response.body()?.data as? Map<String, Any>
                    if (statsData != null) {
                        val gameStats = GameStats(
                            gameCount = (statsData["game_count"] as? Number)?.toInt() ?: 0,
                            bestScore = (statsData["best_score"] as? Number)?.toInt() ?: 0,
                            averageScore = (statsData["average_score"] as? Number)?.toInt() ?: 0,
                            adsWatched = (statsData["ads_watched"] as? Number)?.toInt() ?: 0,
                            totalCoins = (statsData["total_coins"] as? Number)?.toInt() ?: 0
                        )
                        
                        _uiState.value = _uiState.value.copy(gameStats = gameStats)
                    }
                } else {
                    Log.w("SettingsViewModel", "获取用户统计失败: ${response.body()?.message}")
                    // 使用本地数据作为后备
                    val gameStats = GameStats(
                        gameCount = 0,
                        bestScore = 0,
                        averageScore = 0,
                        adsWatched = 0,
                        totalCoins = currentUser.coins
                    )
                    _uiState.value = _uiState.value.copy(gameStats = gameStats)
                }
            } catch (e: Exception) {
                Log.e("SettingsViewModel", "加载用户统计失败", e)
                // 使用本地数据作为后备
                val currentUser = UserManager.getCurrentUser()
                if (currentUser != null) {
                    val gameStats = GameStats(
                        gameCount = 0,
                        bestScore = 0,
                        averageScore = 0,
                        adsWatched = 0,
                        totalCoins = currentUser.coins
                    )
                    _uiState.value = _uiState.value.copy(gameStats = gameStats)
                }
            }
        }
    }
    
    fun loadWithdrawHistory() {
        viewModelScope.launch {
            try {
                val currentUser = UserManager.getCurrentUser()
                if (currentUser == null) {
                    Log.w("SettingsViewModel", "用户未登录，无法加载提现历史")
                    return@launch
                }
                
                // 获取提现历史
                val response = apiService.getWithdrawHistory(currentUser.id)
                
                if (response.isSuccessful && response.body()?.code == 200) {
                    val historyData = response.body()?.data as? List<Map<String, Any>>
                    if (historyData != null) {
                        val withdrawHistory = historyData.map { record ->
                            WithdrawRecord(
                                id = (record["id"] as? Number)?.toInt() ?: 0,
                                amount = (record["amount"] as? Number)?.toString() ?: "0",
                                status = record["status"] as? String ?: "UNKNOWN",
                                requestTime = formatDateTime(record["request_time"] as? String),
                                alipayAccount = record["alipay_account"] as? String ?: ""
                            )
                        }
                        
                        _uiState.value = _uiState.value.copy(withdrawHistory = withdrawHistory)
                    }
                } else {
                    Log.w("SettingsViewModel", "获取提现历史失败: ${response.body()?.message}")
                }
            } catch (e: Exception) {
                Log.e("SettingsViewModel", "加载提现历史失败", e)
            }
        }
    }
    
    private fun formatDateTime(dateTimeStr: String?): String {
        return try {
            if (dateTimeStr == null) return "未知时间"
            // 尝试解析ISO格式的日期时间
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val date = inputFormat.parse(dateTimeStr)
            date?.let { dateFormat.format(it) } ?: dateTimeStr
        } catch (e: Exception) {
            dateTimeStr ?: "未知时间"
        }
    }
    
    fun clearCache() {
        viewModelScope.launch {
            try {
                // 这里可以添加清除缓存的逻辑
                // 比如清除图片缓存、临时文件等
                Log.d("SettingsViewModel", "清除缓存完成")
            } catch (e: Exception) {
                Log.e("SettingsViewModel", "清除缓存失败", e)
            }
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            try {
                UserManager.logout()
                _uiState.value = SettingsUiState() // 重置状态
                Log.d("SettingsViewModel", "用户已退出登录")
            } catch (e: Exception) {
                Log.e("SettingsViewModel", "退出登录失败", e)
            }
        }
    }
}
