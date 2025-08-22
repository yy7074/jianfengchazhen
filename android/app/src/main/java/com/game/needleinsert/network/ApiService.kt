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
    
    @GET("api/user/{user_id}/stats")
    suspend fun getUserStats(@Path("user_id") userId: String): Response<BaseResponse<Map<String, Any>>>
    
    @GET("api/user/{user_id}/withdraws")
    suspend fun getWithdrawHistory(@Path("user_id") userId: String): Response<BaseResponse<List<Map<String, Any>>>>
    
    @POST("api/user/{user_id}/withdraw")
    suspend fun submitWithdrawRequest(
        @Path("user_id") userId: String,
        @Body request: Map<String, Any>
    ): Response<BaseResponse<Map<String, Any>>>
    
    // 广告相关接口
    @GET("api/ad/available/{user_id}")
    suspend fun getAvailableAds(
        @Header("Authorization") token: String,
        @Path("user_id") userId: String
    ): Response<BaseResponse<Map<String, Any>>>
    
    @GET("api/ad/random")
    suspend fun getRandomAd(@Header("Authorization") token: String): Response<BaseResponse<AdConfig>>
    
    @POST("api/ad/watch/{user_id}")
    suspend fun submitAdWatch(
        @Path("user_id") userId: String,
        @Body request: AdWatchRequest
    ): Response<BaseResponse<AdReward>>
    
    @GET("api/ad/stats")
    suspend fun getAdStats(@Header("Authorization") token: String): Response<BaseResponse<Map<String, Any>>>
    
    @FormUrlEncoded
    @POST("api/ad/click")
    suspend fun recordAdClick(
        @Header("Authorization") token: String,
        @Field("ad_id") adId: String,
        @Field("user_id") userId: String
    ): Response<BaseResponse<String>>
    
    // 游戏相关接口
    @POST("api/game/result")
    suspend fun submitGameResult(
        @Header("Authorization") token: String,
        @Body request: GameResultSubmit
    ): Response<BaseResponse<String>>
    
    @GET("api/game/leaderboard")
    suspend fun getLeaderboard(
        @Header("Authorization") token: String,
        @Query("period") period: String = "all",
        @Query("limit") limit: Int = 50
    ): Response<BaseResponse<LeaderboardResponse>>
} 