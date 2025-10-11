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
                val (currentVersionName, currentVersionCode) = getCurrentVersionInfo(context)
                
                val request = VersionCheckRequest(
                    platform = "android",
                    currentVersionCode = currentVersionCode
                )
                
                Log.d(TAG, "开始版本检查...")
                Log.d(TAG, "当前版本: $currentVersionName (代码: $currentVersionCode)")
                Log.d(TAG, "请求数据: platform=${request.platform}, currentVersionCode=${request.currentVersionCode}")
                
                val apiService = RetrofitClient.getApiService()
                Log.d(TAG, "获取API服务成功")
                
                val response = apiService.checkVersionUpdate(request)
                Log.d(TAG, "网络请求完成, 状态码: ${response.code()}")
                Log.d(TAG, "响应消息: ${response.message()}")
                
                if (response.isSuccessful) {
                    val baseResponse = response.body()
                    Log.d(TAG, "响应体: $baseResponse")
                    
                    if (baseResponse?.code == 200) {
                        val versionCheckResponse = baseResponse.data
                        Log.d(TAG, "版本检查成功!")
                        Log.d(TAG, "有更新: ${versionCheckResponse?.hasUpdate}")
                        Log.d(TAG, "强制更新: ${versionCheckResponse?.isForceUpdate}")
                        
                        versionCheckResponse?.latestVersion?.let { version ->
                            Log.d(TAG, "最新版本: ${version.versionName} (代码: ${version.versionCode})")
                            Log.d(TAG, "下载链接: ${version.downloadUrl}")
                            Log.d(TAG, "文件大小: ${version.fileSize} bytes")
                        }
                        
                        return@withContext versionCheckResponse
                    } else {
                        Log.e(TAG, "API返回错误: code=${baseResponse?.code}, message=${baseResponse?.message}")
                    }
                } else {
                    Log.e(TAG, "HTTP请求失败: ${response.code()} - ${response.message()}")
                    val errorBody = response.errorBody()?.string()
                    Log.e(TAG, "错误响应体: $errorBody")
                }
                
                null
            } catch (e: Exception) {
                Log.e(TAG, "版本检查异常: ${e.javaClass.simpleName} - ${e.message}", e)
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
