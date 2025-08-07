package com.game.needleinsert.network

import android.util.Log
import com.game.needleinsert.model.BaseResponse
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    
    // 后端服务器地址 - 请根据实际情况修改
    private const val BASE_URL = "http://your-backend-server.com/"
    
    private var apiService: ApiService? = null
    
    fun getApiService(): ApiService {
        if (apiService == null) {
            apiService = createRetrofit().create(ApiService::class.java)
        }
        return apiService!!
    }
    
    private fun createRetrofit(): Retrofit {
        // 创建日志拦截器
        val loggingInterceptor = HttpLoggingInterceptor { message ->
            Log.d("NetworkAPI", message)
        }.apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        // 创建OkHttp客户端
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
        
        // 创建Retrofit实例
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    // 设置授权头
    fun createAuthHeader(token: String): String {
        return "Bearer $token"
    }
    
    // 检查网络响应
    fun <T> isSuccessful(response: retrofit2.Response<BaseResponse<T>>): Boolean {
        return response.isSuccessful && response.body()?.code == 200
    }
    
    // 获取响应数据
    fun <T> getResponseData(response: retrofit2.Response<BaseResponse<T>>): T? {
        return if (isSuccessful(response)) {
            response.body()?.data
        } else {
            Log.e("RetrofitClient", "API请求失败: ${response.body()?.message}")
            null
        }
    }
} 