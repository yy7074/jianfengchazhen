package com.game.needleinsert.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.game.needleinsert.network.RetrofitClient
import com.game.needleinsert.utils.UserManager
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
    
    fun loadLeaderboard() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true, error = null)
                
                val response = apiService.getLeaderboard("Bearer dummy_token")
                
                if (response.isSuccessful && response.body()?.code == 200) {
                    val leaderboardData = response.body()?.data as? List<Map<String, Any>>
                    if (leaderboardData != null) {
                        val currentUser = UserManager.getCurrentUser()
                        val players = leaderboardData.mapIndexed { index, playerMap ->
                            val playerId = (playerMap["id"] as? Number)?.toString() ?: "0"
                            PlayerData(
                                id = playerId,
                                nickname = playerMap["nickname"] as? String ?: "匿名玩家",
                                bestScore = (playerMap["best_score"] as? Number)?.toInt() ?: 0,
                                level = (playerMap["level"] as? Number)?.toInt() ?: 1,
                                gameCount = (playerMap["game_count"] as? Number)?.toInt() ?: 0,
                                coins = (playerMap["coins"] as? Number)?.toInt() ?: 0,
                                isCurrentUser = currentUser != null && playerId == currentUser.id
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
        // 这里可以根据时间范围重新加载数据
        // 暂时使用相同的数据
        loadLeaderboard()
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
