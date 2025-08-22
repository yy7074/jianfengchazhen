package com.game.needleinsert.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.game.needleinsert.network.RetrofitClient
import com.game.needleinsert.utils.UserManager
import com.game.needleinsert.model.LeaderboardResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class LeaderboardViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(LeaderboardUiState())
    val uiState: StateFlow<LeaderboardUiState> = _uiState.asStateFlow()
    
    private val apiService = RetrofitClient.getApiService()
    
    data class LeaderboardUiState(
        val isLoading: Boolean = false,
        val leaderboardData: List<PlayerData> = emptyList(),
        val timeRange: String = "all",
        val error: String? = null
    )
    
    data class PlayerData(
        val id: String,
        val nickname: String,
        val bestScore: Int,
        val level: Int,
        val gameCount: Int,
        val coins: Int,
        val isCurrentUser: Boolean = false
    )
    
    fun loadLeaderboard(period: String = "all") {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true, error = null)
                
                val response = apiService.getLeaderboard("Bearer dummy_token", period)
                
                if (response.isSuccessful && response.body()?.code == 200) {
                    val leaderboardResponse = response.body()?.data
                    if (leaderboardResponse != null) {
                        val currentUser = UserManager.getCurrentUser()
                        val players = leaderboardResponse.leaderboard.map { player ->
                            PlayerData(
                                id = player.userId.toString(),
                                nickname = player.nickname,
                                bestScore = player.bestScore,
                                level = player.level,
                                gameCount = player.gameCount,
                                coins = player.coins,
                                isCurrentUser = currentUser != null && player.userId.toString() == currentUser.id
                            )
                        }
                        
                        _uiState.value = _uiState.value.copy(
                            leaderboardData = players,
                            isLoading = false
                        )
                    } else {
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            error = "数据格式错误"
                        )
                    }
                } else {
                    // 后备数据
                    val fallbackData = generateFallbackData()
                    _uiState.value = _uiState.value.copy(
                        leaderboardData = fallbackData,
                        isLoading = false,
                        error = "使用离线数据"
                    )
                }
            } catch (e: Exception) {
                Log.e("LeaderboardViewModel", "加载排行榜失败", e)
                val fallbackData = generateFallbackData()
                _uiState.value = _uiState.value.copy(
                    leaderboardData = fallbackData,
                    isLoading = false,
                    error = "网络连接失败，显示离线数据"
                )
            }
        }
    }
    
    fun changeTimeRange(timeRange: String) {
        _uiState.value = _uiState.value.copy(timeRange = timeRange)
        loadLeaderboard(timeRange)
    }
    
    private fun generateFallbackData(): List<PlayerData> {
        val currentUser = UserManager.getCurrentUser()
        return listOf(
            PlayerData(
                id = "demo1",
                nickname = "游戏高手",
                bestScore = 2580,
                level = 15,
                gameCount = 128,
                coins = 5200
            ),
            PlayerData(
                id = "demo2", 
                nickname = "针法大师",
                bestScore = 2340,
                level = 12,
                gameCount = 95,
                coins = 4100
            ),
            PlayerData(
                id = "demo3",
                nickname = "插针王者",
                bestScore = 2100,
                level = 10,
                gameCount = 76,
                coins = 3800
            ),
            PlayerData(
                id = currentUser?.id ?: "demo_user",
                nickname = currentUser?.nickname ?: "我的游戏",
                bestScore = 850,
                level = currentUser?.level ?: 3,
                gameCount = 25,
                coins = currentUser?.coins ?: 560,
                isCurrentUser = true
            ),
            PlayerData(
                id = "demo4",
                nickname = "新手玩家",
                bestScore = 680,
                level = 2,
                gameCount = 18,
                coins = 340
            )
        ).sortedByDescending { it.bestScore }
    }
}
