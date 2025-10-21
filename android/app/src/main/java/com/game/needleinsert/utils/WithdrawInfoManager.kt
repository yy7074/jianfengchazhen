package com.game.needleinsert.utils

import android.content.Context
import android.content.SharedPreferences
import android.util.Log

/**
 * 提现信息管理器 - 本地保存提现信息，避免重复输入
 */
object WithdrawInfoManager {
    private const val TAG = "WithdrawInfoManager"
    private const val PREFS_NAME = "withdraw_info_prefs"
    private const val KEY_ALIPAY_ACCOUNT = "alipay_account"
    private const val KEY_REAL_NAME = "real_name"
    
    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }
    
    /**
     * 保存提现信息
     */
    fun saveWithdrawInfo(context: Context, alipayAccount: String, realName: String) {
        Log.d(TAG, "保存提现信息: alipay=$alipayAccount, name=$realName")
        getPrefs(context).edit().apply {
            putString(KEY_ALIPAY_ACCOUNT, alipayAccount)
            putString(KEY_REAL_NAME, realName)
            apply()
        }
        Log.d(TAG, "提现信息保存成功")
    }
    
    /**
     * 获取保存的支付宝账号
     */
    fun getSavedAlipayAccount(context: Context): String {
        val account = getPrefs(context).getString(KEY_ALIPAY_ACCOUNT, "") ?: ""
        Log.d(TAG, "读取保存的支付宝账号: $account")
        return account
    }
    
    /**
     * 获取保存的真实姓名
     */
    fun getSavedRealName(context: Context): String {
        val name = getPrefs(context).getString(KEY_REAL_NAME, "") ?: ""
        Log.d(TAG, "读取保存的真实姓名: $name")
        return name
    }
    
    /**
     * 清除保存的提现信息
     */
    fun clearWithdrawInfo(context: Context) {
        getPrefs(context).edit().clear().apply()
    }
    
    /**
     * 检查是否有保存的提现信息
     */
    fun hasSavedInfo(context: Context): Boolean {
        val alipay = getSavedAlipayAccount(context)
        val name = getSavedRealName(context)
        return alipay.isNotBlank() && name.isNotBlank()
    }
}

