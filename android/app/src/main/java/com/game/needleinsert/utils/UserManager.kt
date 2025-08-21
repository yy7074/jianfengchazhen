package com.game.needleinsert.utils

import android.content.Context
import android.content.SharedPreferences
import android.provider.Settings
import android.util.Log
import android.os.Build
import com.game.needleinsert.model.User
import com.game.needleinsert.model.UserRegister
import com.game.needleinsert.model.UserLogin
import com.game.needleinsert.network.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.random.Random

/**
 * 用户管理器
 * 负责用户注册、登录和本地用户信息管理
 */
object UserManager {
    private const val TAG = "UserManager"
    private const val PREFS_NAME = "user_prefs"
    private const val KEY_USER_ID = "user_id"
    private const val KEY_DEVICE_ID = "device_id"
    private const val KEY_NICKNAME = "nickname"
    private const val KEY_COINS = "coins"
    private const val KEY_LEVEL = "level"
    private const val KEY_IS_REGISTERED = "is_registered"
    
    private var currentUser: User? = null
    private lateinit var sharedPrefs: SharedPreferences
    
    /**
     * 初始化用户管理器
     */
    fun init(context: Context) {
        sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        loadUserFromPrefs()
    }
    
    /**
     * 获取当前用户
     */
    fun getCurrentUser(): User? = currentUser
    
    /**
     * 获取设备ID（固定唯一，不包含随机数）
     */
    private fun getDeviceId(context: Context): String {
        val savedDeviceId = sharedPrefs.getString(KEY_DEVICE_ID, null)
        if (savedDeviceId != null) {
            return savedDeviceId
        }
        
        // 使用Android ID生成固定的设备ID
        val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        val deviceId = if (androidId.isNullOrEmpty()) {
            "device_${System.currentTimeMillis()}"
        } else {
            "device_${androidId}"
        }
        
        // 保存设备ID
        sharedPrefs.edit().putString(KEY_DEVICE_ID, deviceId).apply()
        Log.d(TAG, "生成设备ID: $deviceId")
        return deviceId
    }
    
    /**
     * 自动注册或登录用户
     */
    suspend fun autoRegisterOrLogin(context: Context): User? {
        return withContext(Dispatchers.IO) {
            try {
                val deviceId = getDeviceId(context)
                val isRegistered = sharedPrefs.getBoolean(KEY_IS_REGISTERED, false)
                
                if (isRegistered) {
                    // 尝试登录
                    Log.d(TAG, "尝试登录用户: $deviceId")
                    loginUser(deviceId)
                } else {
                    // 注册新用户
                    Log.d(TAG, "注册新用户: $deviceId")
                    registerUser(context, deviceId)
                }
            } catch (e: Exception) {
                Log.e(TAG, "自动注册或登录失败", e)
                null
            }
        }
    }
    
    /**
     * 注册用户
     */
    private suspend fun registerUser(context: Context, deviceId: String): User? {
        return try {
            val nickname = "玩家${Random.nextInt(1000, 9999)}"
            val deviceName = getDeviceName()
            val registerRequest = UserRegister(
                deviceId = deviceId,
                deviceName = deviceName,
                nickname = nickname
            )
            
            val response = RetrofitClient.getApiService().registerUser(registerRequest)
            
            if (response.isSuccessful && response.body()?.code == 200) {
                val userData = response.body()?.data
                Log.d(TAG, "注册响应原始数据: $userData")
                Log.d(TAG, "数据类型: ${userData?.javaClass?.simpleName}")
                
                // 直接使用Gson解析的User对象
                val user = userData ?: User(
                    id = "0",
                    deviceId = deviceId,
                    nickname = nickname,
                    coins = 100,
                    level = 1
                )
                
                // 保存用户信息
                saveUserToPrefs(user)
                sharedPrefs.edit().putBoolean(KEY_IS_REGISTERED, true).apply()
                currentUser = user
                
                Log.d(TAG, "用户注册成功: $nickname, 初始金币: ${user.coins}")
                user
            } else {
                Log.e(TAG, "注册失败: ${response.body()?.message}")
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "注册请求失败", e)
            null
        }
    }
    
    /**
     * 登录用户
     */
    private suspend fun loginUser(deviceId: String): User? {
        return try {
            val loginRequest = UserLogin(deviceId = deviceId)
            val response = RetrofitClient.getApiService().loginUser(loginRequest)
            
            if (response.isSuccessful && response.body()?.code == 200) {
                val userData = response.body()?.data
                Log.d(TAG, "登录响应数据: $userData")
                
                // 直接使用Gson解析的User对象
                val user = userData ?: User(
                    id = "0",
                    deviceId = deviceId,
                    nickname = "用户",
                    coins = 0,
                    level = 1
                )
                
                // 更新本地用户信息
                saveUserToPrefs(user)
                currentUser = user
                
                Log.d(TAG, "用户登录成功: ${user.nickname}, 金币: ${user.coins}")
                user
            } else {
                Log.e(TAG, "登录失败: ${response.body()?.message}")
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "登录请求失败", e)
            null
        }
    }
    
    /**
     * 更新用户金币
     */
    fun updateCoins(coins: Int) {
        currentUser?.let { user ->
            val updatedUser = user.copy(coins = coins)
            currentUser = updatedUser
            saveUserToPrefs(updatedUser)
        }
    }
    
    /**
     * 更新用户等级
     */
    fun updateLevel(level: Int) {
        currentUser?.let { user ->
            val updatedUser = user.copy(level = level)
            currentUser = updatedUser
            saveUserToPrefs(updatedUser)
        }
    }
    
    /**
     * 保存用户信息到SharedPreferences
     */
    private fun saveUserToPrefs(user: User) {
        sharedPrefs.edit().apply {
            putString(KEY_USER_ID, user.id)
            putString(KEY_DEVICE_ID, user.deviceId)
            putString(KEY_NICKNAME, user.nickname)
            putString(KEY_COINS, user.coins.toString())
            putInt(KEY_LEVEL, user.level)
            apply()
        }
    }
    
    /**
     * 从SharedPreferences加载用户信息
     */
    private fun loadUserFromPrefs() {
        val userId = sharedPrefs.getString(KEY_USER_ID, null)
        val deviceId = sharedPrefs.getString(KEY_DEVICE_ID, null)
        val nickname = sharedPrefs.getString(KEY_NICKNAME, null)
        val coinsStr = sharedPrefs.getString(KEY_COINS, null)
        val level = sharedPrefs.getInt(KEY_LEVEL, 1)
        
        if (userId != null && deviceId != null && nickname != null && coinsStr != null) {
            currentUser = User(
                id = userId,
                deviceId = deviceId,
                nickname = nickname,
                coins = coinsStr.toIntOrNull() ?: 0,
                level = level
            )
            Log.d(TAG, "加载本地用户信息: $nickname")
        }
    }
    
    /**
     * 获取设备名称（手机型号）
     */
    private fun getDeviceName(): String {
        return try {
            val manufacturer = Build.MANUFACTURER
            val model = Build.MODEL
            if (model.startsWith(manufacturer)) {
                model.replaceFirstChar { it.uppercase() }
            } else {
                "${manufacturer.replaceFirstChar { it.uppercase() }} $model"
            }
        } catch (e: Exception) {
            Log.w(TAG, "获取设备名称失败", e)
            "Unknown Device"
        }
    }
    
    /**
     * 更新用户信息
     */
    fun updateUserInfo(user: User) {
        currentUser = user
        saveUserToPrefs(user)
        Log.d(TAG, "用户信息已更新: ${user.nickname}")
    }

    /**
     * 清除用户数据（登出）
     */
    fun logout() {
        currentUser = null
        sharedPrefs.edit().clear().apply()
        Log.d(TAG, "用户已登出")
    }
}
