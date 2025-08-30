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
import java.text.SimpleDateFormat
import java.util.*

class WithdrawViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(WithdrawUiState())
    val uiState: StateFlow<WithdrawUiState> = _uiState.asStateFlow()
    
    private val apiService = RetrofitClient.getApiService()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
    
    data class WithdrawUiState(
        val isLoading: Boolean = false,
        val isSubmitting: Boolean = false,
        val currentCoins: Int = 0,
        val withdrawableAmount: Double = 0.0,
        val selectedAmount: Double? = null,
        val alipayAccount: String = "",
        val realName: String = "",
        val withdrawHistory: List<WithdrawRecord> = emptyList(),
        val message: String? = null,
        val error: String? = null
    ) {
        val canSubmit: Boolean
            get() = selectedAmount != null &&
                    selectedAmount!! <= withdrawableAmount &&
                    alipayAccount.isNotBlank() && 
                    realName.isNotBlank()
    }
    
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
                val currentUser = UserManager.getCurrentUser()
                if (currentUser != null) {
                    val withdrawableAmount = currentUser.coins / 33000.0 // 33000金币 = 1元
                    _uiState.value = _uiState.value.copy(
                        currentCoins = currentUser.coins,
                        withdrawableAmount = withdrawableAmount
                    )
                }
            } catch (e: Exception) {
                Log.e("WithdrawViewModel", "加载用户信息失败", e)
            }
        }
    }
    
    fun loadWithdrawHistory() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                val currentUser = UserManager.getCurrentUser()
                if (currentUser == null) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "用户未登录"
                    )
                    return@launch
                }
                
                val response = apiService.getWithdrawHistory(currentUser.id)
                
                if (response.isSuccessful && response.body()?.code == 200) {
                    val historyData = response.body()?.data as? List<Map<String, Any>>
                    if (historyData != null) {
                        val history = historyData.map { record ->
                            WithdrawRecord(
                                id = (record["id"] as? Number)?.toInt() ?: 0,
                                amount = String.format("%.2f", (record["amount"] as? Number)?.toDouble() ?: 0.0),
                                status = record["status"] as? String ?: "UNKNOWN",
                                requestTime = formatDateTime(record["request_time"] as? String),
                                alipayAccount = record["alipay_account"] as? String ?: ""
                            )
                        }
                        
                        _uiState.value = _uiState.value.copy(
                            withdrawHistory = history,
                            isLoading = false
                        )
                    }
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "获取提现历史失败"
                    )
                }
            } catch (e: Exception) {
                Log.e("WithdrawViewModel", "加载提现历史失败", e)
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "网络连接失败"
                )
            }
        }
    }
    
    fun selectWithdrawAmount(amount: Double) {
        _uiState.value = _uiState.value.copy(selectedAmount = amount)
    }
    
    fun updateAlipayAccount(account: String) {
        _uiState.value = _uiState.value.copy(alipayAccount = account)
    }
    
    fun updateRealName(name: String) {
        _uiState.value = _uiState.value.copy(realName = name)
    }
    
    fun submitWithdrawRequest() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isSubmitting = true, message = null, error = null)
                
                val currentUser = UserManager.getCurrentUser()
                if (currentUser == null) {
                    _uiState.value = _uiState.value.copy(
                        isSubmitting = false,
                        error = "用户未登录"
                    )
                    return@launch
                }
                
                val amount = _uiState.value.selectedAmount
                if (amount == null) {
                    _uiState.value = _uiState.value.copy(
                        isSubmitting = false,
                        error = "请选择提现金额"
                    )
                    return@launch
                }
                
                // 验证金额是否为有效选项
                val validAmounts = listOf(0.5, 15.0, 30.0)
                if (amount !in validAmounts) {
                    _uiState.value = _uiState.value.copy(
                        isSubmitting = false,
                        error = "无效的提现金额"
                    )
                    return@launch
                }
                
                if (amount > _uiState.value.withdrawableAmount) {
                    _uiState.value = _uiState.value.copy(
                        isSubmitting = false,
                        error = "提现金额超过可用余额"
                    )
                    return@launch
                }
                
                // 构建提现请求
                val requestBody = mapOf(
                    "amount" to amount,
                    "alipay_account" to _uiState.value.alipayAccount,
                    "real_name" to _uiState.value.realName
                )
                
                // 调用提现申请API
                val response = apiService.submitWithdrawRequest(currentUser.id, requestBody)
                
                if (!response.isSuccessful || response.body()?.code != 200) {
                    _uiState.value = _uiState.value.copy(
                        isSubmitting = false,
                        error = response.body()?.message ?: "提交失败，请重试"
                    )
                    return@launch
                }
                
                _uiState.value = _uiState.value.copy(
                    isSubmitting = false,
                    message = "提现申请提交成功，请等待审核",
                    selectedAmount = null,
                    alipayAccount = "",
                    realName = ""
                )
                
                // 重新加载用户信息和提现历史
                loadUserInfo()
                loadWithdrawHistory()
                
            } catch (e: Exception) {
                Log.e("WithdrawViewModel", "提交提现申请失败", e)
                _uiState.value = _uiState.value.copy(
                    isSubmitting = false,
                    error = "提交失败，请重试"
                )
            }
        }
    }
    
    private fun formatDateTime(dateTimeStr: String?): String {
        return try {
            if (dateTimeStr == null) return "未知时间"
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val date = inputFormat.parse(dateTimeStr)
            date?.let { dateFormat.format(it) } ?: dateTimeStr
        } catch (e: Exception) {
            dateTimeStr ?: "未知时间"
        }
    }
}
