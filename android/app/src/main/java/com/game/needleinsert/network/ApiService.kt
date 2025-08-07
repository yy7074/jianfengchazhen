package com.game.needleinsert.network

import com.game.needleinsert.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // 用户相关接口
    @POST("api/user/register")
    suspend fun registerUser(@Body request: UserRegister): Response<BaseResponse<User>>
    
    @POST("api/user/login")
    suspend fun loginUser(@Body request: UserLogin): Response<BaseResponse<User>>
    
    @GET("api/user/profile")
    suspend fun getUserProfile(@Header("Authorization") token: String): Response<BaseResponse<User>>
    
    // 广告相关接口
    @GET("api/ad/random")
    suspend fun getRandomAd(@Header("Authorization") token: String): Response<BaseResponse<AdConfig>>
    
    @POST("api/ad/watch")
    suspend fun submitAdWatch(
        @Header("Authorization") token: String,
        @Body request: AdWatchRequest
    ): Response<BaseResponse<AdReward>>
    
    // 游戏相关接口
    @POST("api/game/result")
    suspend fun submitGameResult(
        @Header("Authorization") token: String,
        @Body request: GameResultSubmit
    ): Response<BaseResponse<String>>
    
    @GET("api/game/leaderboard")
    suspend fun getLeaderboard(@Header("Authorization") token: String): Response<BaseResponse<List<User>>>
} 