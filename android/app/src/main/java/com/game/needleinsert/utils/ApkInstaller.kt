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
                Log.d(TAG, "开始下载APK: $downloadUrl")
                
                val url = URL(downloadUrl)
                val connection = url.openConnection() as HttpURLConnection
                connection.connect()
                
                val fileLength = connection.contentLength
                
                // 创建下载目录
                val downloadDir = File(context.getExternalFilesDir(null), "downloads")
                if (!downloadDir.exists()) {
                    downloadDir.mkdirs()
                }
                
                val apkFile = File(downloadDir, fileName)
                
                // 如果文件已存在，删除旧文件
                if (apkFile.exists()) {
                    apkFile.delete()
                }
                
                val input = connection.inputStream
                val output = FileOutputStream(apkFile)
                
                val buffer = ByteArray(4096)
                var total = 0
                var count: Int
                
                while (input.read(buffer).also { count = it } != -1) {
                    total += count
                    output.write(buffer, 0, count)
                    
                    // 更新进度
                    if (fileLength > 0) {
                        val progress = (total * 100 / fileLength)
                        onProgress(progress)
                    }
                }
                
                output.flush()
                output.close()
                input.close()
                
                Log.d(TAG, "APK下载完成: ${apkFile.absolutePath}")
                apkFile
                
            } catch (e: Exception) {
                Log.e(TAG, "下载APK失败", e)
                null
            }
        }
    }
    
    /**
     * 安装APK文件
     */
    fun installApk(context: Context, apkFile: File): Boolean {
        return try {
            val intent = Intent(Intent.ACTION_VIEW)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            
            val apkUri = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                // Android 7.0及以上使用FileProvider
                intent.flags = intent.flags or Intent.FLAG_GRANT_READ_URI_PERMISSION
                FileProvider.getUriForFile(
                    context,
                    "${context.packageName}.fileprovider",
                    apkFile
                )
            } else {
                Uri.fromFile(apkFile)
            }
            
            intent.setDataAndType(apkUri, "application/vnd.android.package-archive")
            
            context.startActivity(intent)
            Log.d(TAG, "启动APK安装: ${apkFile.absolutePath}")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "安装APK失败", e)
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
