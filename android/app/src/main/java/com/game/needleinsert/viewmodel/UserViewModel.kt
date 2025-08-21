package com.game.needleinsert.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.game.needleinsert.model.User
import com.game.needleinsert.utils.UserManager
import com.game.needleinsert.network.RetrofitClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import android.util.Log

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val errorMessage: String = ""
)

class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    companion object {
        private const val TAG = "UserViewModel"
    }

    /**
     * 加载用户信息
     */
    fun loadUserInfo() {
        val currentUser = UserManager.getCurrentUser()
        _uiState.value = _uiState.value.copy(
            user = currentUser,
            errorMessage = ""
        )
    }

    /**
     * 自动登录（注册或登录）
     */
    suspend fun autoLogin(context: Context) {
        _uiState.value = _uiState.value.copy(
            isLoading = true,
            errorMessage = ""
        )
        
        try {
            // 确保UserManager已初始化
            UserManager.init(context)
            
            Log.d(TAG, "开始自动登录...")
            val user = UserManager.autoRegisterOrLogin(context)
            
            if (user != null) {
                Log.d(TAG, "登录成功: ${user.nickname}")
                _uiState.value = _uiState.value.copy(
                    user = user,
                    isLoading = false,
                    errorMessage = ""
                )
                
                // 登录成功后尝试获取最新的用户统计信息
                loadUserStats(user.id)
            } else {
                Log.e(TAG, "登录失败")
                _uiState.value = _uiState.value.copy(
                    user = null,
                    isLoading = false,
                    errorMessage = "登录失败，请检查网络连接后重试"
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "登录异常", e)
            _uiState.value = _uiState.value.copy(
                user = null,
                isLoading = false,
                errorMessage = "登录异常：${e.message}"
            )
        }
    }

    /**
     * 获取用户统计信息
     */
    private suspend fun loadUserStats(userId: String) {
        try {
            Log.d(TAG, "获取用户统计信息: $userId")
            val response = RetrofitClient.getApiService().getUserStats(userId)
            
            if (response.isSuccessful && response.body()?.code == 200) {
                val statsData = response.body()?.data as? Map<String, Any>
                statsData?.let { stats ->
                    val currentUser = _uiState.value.user
                    if (currentUser != null) {
                        // 更新用户信息（包含最新统计）
                        val updatedUser = currentUser.copy(
                            coins = (stats["current_coins"] as? Number)?.toInt() ?: currentUser.coins,
                            bestScore = (stats["best_score"] as? Number)?.toInt() ?: currentUser.bestScore,
                            level = (stats["level"] as? Number)?.toInt() ?: currentUser.level,
                            gameCount = (stats["game_count"] as? Number)?.toInt() ?: currentUser.gameCount,
                            totalCoins = (stats["total_coins"] as? Number)?.toFloat() ?: currentUser.totalCoins
                        )
                        
                        _uiState.value = _uiState.value.copy(user = updatedUser)
                        Log.d(TAG, "用户统计更新成功: 金币${updatedUser.coins}, 最高分${updatedUser.bestScore}")
                    }
                }
            } else {
                Log.w(TAG, "获取用户统计失败: ${response.body()?.message}")
            }
        } catch (e: Exception) {
            Log.e(TAG, "获取用户统计异常", e)
            // 不显示错误信息，因为这不是关键操作
        }
    }

    /**
     * 登出
     */
    fun logout() {
        UserManager.logout()
        _uiState.value = _uiState.value.copy(
            user = null,
            errorMessage = ""
        )
        Log.d(TAG, "用户已登出")
    }

    /**
     * 更新用户金币（从其他地方调用，比如游戏结束或看广告后）
     */
    fun updateUserCoins(newCoins: Int) {
        val currentUser = _uiState.value.user
        if (currentUser != null) {
            val updatedUser = currentUser.copy(coins = newCoins)
            UserManager.updateCoins(newCoins)
            _uiState.value = _uiState.value.copy(user = updatedUser)
            Log.d(TAG, "用户金币更新: $newCoins")
        }
    }

    /**
     * 更新用户等级
     */
    fun updateUserLevel(newLevel: Int) {
        val currentUser = _uiState.value.user
        if (currentUser != null) {
            val updatedUser = currentUser.copy(level = newLevel)
            UserManager.updateLevel(newLevel)
            _uiState.value = _uiState.value.copy(user = updatedUser)
            Log.d(TAG, "用户等级更新: $newLevel")
        }
    }

    /**
     * 清除错误信息
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = "")
    }

    /**
     * 检查是否已登录
     */
    fun isLoggedIn(): Boolean {
        return _uiState.value.user != null
    }

    /**
     * 获取当前用户
     */
    fun getCurrentUser(): User? {
        return _uiState.value.user
    }
}