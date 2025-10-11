package com.game.needleinsert.utils

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.util.Log
import androidx.core.content.FileProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL

/**
 * APK下载和安装管理器
 */
object ApkInstaller {
    private const val TAG = "ApkInstaller"
    
    /**
     * 下载APK文件
     */
    suspend fun downloadApk(
        context: Context,
        downloadUrl: String,
        fileName: String,
        onProgress: (Int) -> Unit = {}
    ): File? {
        return withContext(Dispatchers.IO) {
            try {
                Log.d(TAG, "开始下载APK...")
                Log.d(TAG, "下载链接: $downloadUrl")
                Log.d(TAG, "文件名: $fileName")
                
                val url = URL(downloadUrl)
                val connection = url.openConnection() as HttpURLConnection
                connection.connectTimeout = 30000 // 30秒连接超时
                connection.readTimeout = 60000 // 60秒读取超时
                connection.connect()
                
                val responseCode = connection.responseCode
                Log.d(TAG, "HTTP响应码: $responseCode")
                
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    Log.e(TAG, "下载失败: HTTP $responseCode")
                    return@withContext null
                }
                
                val fileLength = connection.contentLength
                Log.d(TAG, "文件大小: $fileLength bytes")
                
                // 创建下载目录
                val downloadDir = File(context.getExternalFilesDir(null), "downloads")
                if (!downloadDir.exists()) {
                    val created = downloadDir.mkdirs()
                    Log.d(TAG, "创建下载目录: $created")
                }
                
                val apkFile = File(downloadDir, fileName)
                Log.d(TAG, "保存路径: ${apkFile.absolutePath}")
                
                // 如果文件已存在，删除旧文件
                if (apkFile.exists()) {
                    val deleted = apkFile.delete()
                    Log.d(TAG, "删除旧文件: $deleted")
                }
                
                val input = connection.inputStream
                val output = FileOutputStream(apkFile)
                
                val buffer = ByteArray(4096)
                var total = 0
                var count: Int
                var lastProgress = 0
                
                while (input.read(buffer).also { count = it } != -1) {
                    total += count
                    output.write(buffer, 0, count)
                    
                    // 更新进度
                    if (fileLength > 0) {
                        val progress = (total * 100 / fileLength)
                        if (progress != lastProgress) {
                            onProgress(progress)
                            lastProgress = progress
                            if (progress % 10 == 0) { // 每10%记录一次日志
                                Log.d(TAG, "下载进度: $progress%")
                            }
                        }
                    }
                }
                
                output.flush()
                output.close()
                input.close()
                
                Log.d(TAG, "APK下载完成!")
                Log.d(TAG, "文件路径: ${apkFile.absolutePath}")
                Log.d(TAG, "文件大小: ${apkFile.length()} bytes")
                Log.d(TAG, "文件存在: ${apkFile.exists()}")
                
                apkFile
                
            } catch (e: Exception) {
                Log.e(TAG, "下载APK异常: ${e.javaClass.simpleName} - ${e.message}", e)
                null
            }
        }
    }
    
    /**
     * 安装APK文件
     */
    fun installApk(context: Context, apkFile: File): Boolean {
        return try {
            Log.d(TAG, "开始安装APK...")
            Log.d(TAG, "APK文件: ${apkFile.absolutePath}")
            Log.d(TAG, "文件存在: ${apkFile.exists()}")
            Log.d(TAG, "文件大小: ${apkFile.length()} bytes")
            Log.d(TAG, "Android版本: ${Build.VERSION.SDK_INT}")
            
            if (!apkFile.exists()) {
                Log.e(TAG, "APK文件不存在")
                return false
            }
            
            val intent = Intent(Intent.ACTION_VIEW)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            
            val apkUri = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                // Android 7.0及以上使用FileProvider
                Log.d(TAG, "使用FileProvider (Android 7.0+)")
                intent.flags = intent.flags or Intent.FLAG_GRANT_READ_URI_PERMISSION
                
                val authority = "${context.packageName}.fileprovider"
                Log.d(TAG, "FileProvider authority: $authority")
                
                FileProvider.getUriForFile(context, authority, apkFile)
            } else {
                Log.d(TAG, "使用直接文件URI (Android < 7.0)")
                Uri.fromFile(apkFile)
            }
            
            Log.d(TAG, "APK URI: $apkUri")
            
            intent.setDataAndType(apkUri, "application/vnd.android.package-archive")
            
            // 检查是否有应用可以处理安装Intent
            val packageManager = context.packageManager
            val activities = packageManager.queryIntentActivities(intent, 0)
            Log.d(TAG, "可处理安装的应用数量: ${activities.size}")
            
            if (activities.isEmpty()) {
                Log.e(TAG, "没有应用可以处理APK安装")
                return false
            }
            
            context.startActivity(intent)
            Log.d(TAG, "成功启动APK安装界面")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "安装APK异常: ${e.javaClass.simpleName} - ${e.message}", e)
            false
        }
    }
    
    /**
     * 检查是否可以安装未知来源应用
     */
    fun canInstallUnknownApps(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.packageManager.canRequestPackageInstalls()
        } else {
            true
        }
    }
    
    /**
     * 请求安装未知来源应用权限
     */
    fun requestInstallPermission(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val intent = Intent(android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES)
            intent.data = Uri.parse("package:${context.packageName}")
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            context.startActivity(intent)
        }
    }
    
    /**
     * 清理下载的APK文件
     */
    fun cleanupDownloadedApks(context: Context) {
        try {
            val downloadDir = File(context.getExternalFilesDir(null), "downloads")
            if (downloadDir.exists()) {
                downloadDir.listFiles()?.forEach { file ->
                    if (file.name.endsWith(".apk")) {
                        file.delete()
                        Log.d(TAG, "清理APK文件: ${file.name}")
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "清理APK文件失败", e)
        }
    }
}
