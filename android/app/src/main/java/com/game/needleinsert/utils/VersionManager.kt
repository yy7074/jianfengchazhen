package com.game.needleinsert.utils

import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import com.game.needleinsert.model.VersionCheckRequest
import com.game.needleinsert.model.VersionCheckResponse
import com.game.needleinsert.network.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * 版本管理器
 * 负责检查应用版本更新
 */
object VersionManager {
    private const val TAG = "VersionManager"
    
    /**
     * 获取当前应用版本信息
     */
    fun getCurrentVersionInfo(context: Context): Pair<String, Int> {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            val versionName = packageInfo.versionName ?: "1.0.0"
            val versionCode = packageInfo.longVersionCode.toInt()
            Pair(versionName, versionCode)
        } catch (e: PackageManager.NameNotFoundException) {
            Log.e(TAG, "获取版本信息失败", e)
            Pair("1.0.0", 1)
        }
    }
    
    /**
     * 检查版本更新
     */
    suspend fun checkVersionUpdate(context: Context): VersionCheckResponse? {
        return withContext(Dispatchers.IO) {
            try {
                val (_, currentVersionCode) = getCurrentVersionInfo(context)
                
                val request = VersionCheckRequest(
                    platform = "android",
                    currentVersionCode = currentVersionCode
                )
                
                Log.d(TAG, "检查版本更新: 当前版本号 = $currentVersionCode")
                
                val response = RetrofitClient.getApiService().checkVersionUpdate(request)
                
                if (response.isSuccessful) {
                    val baseResponse = response.body()
                    if (baseResponse?.code == 200) {
                        val versionCheckResponse = baseResponse.data
                        Log.d(TAG, "版本检查结果: hasUpdate=${versionCheckResponse?.hasUpdate}, isForceUpdate=${versionCheckResponse?.isForceUpdate}")
                        return@withContext versionCheckResponse
                    } else {
                        Log.e(TAG, "版本检查失败: ${baseResponse?.message}")
                    }
                } else {
                    Log.e(TAG, "版本检查请求失败: ${response.code()}")
                }
                
                null
            } catch (e: Exception) {
                Log.e(TAG, "检查版本更新异常", e)
                null
            }
        }
    }
    
    /**
     * 格式化文件大小
     */
    fun formatFileSize(bytes: Long?): String {
        if (bytes == null || bytes <= 0) return "未知大小"
        
        val units = arrayOf("B", "KB", "MB", "GB")
        var size = bytes.toDouble()
        var unitIndex = 0
        
        while (size >= 1024 && unitIndex < units.size - 1) {
            size /= 1024
            unitIndex++
        }
        
        return String.format("%.1f %s", size, units[unitIndex])
    }
    
    /**
     * 解析更新内容为列表
     */
    fun parseUpdateContent(content: String?): List<String> {
        if (content.isNullOrBlank()) return emptyList()
        
        return content.split("\n")
            .map { it.trim() }
            .filter { it.isNotEmpty() }
    }
}
