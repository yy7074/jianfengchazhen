-- MySQL dump 10.13  Distrib 9.2.0, for macos15.2 (arm64)
--
-- Host: localhost    Database: game_db
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ad_configs`
--

DROP TABLE IF EXISTS `ad_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ad_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '广告名称',
  `ad_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'video',
  `video_url` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '视频文件URL（视频广告用）',
  `webpage_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duration` int NOT NULL COMMENT '视频时长（秒）',
  `reward_coins` decimal(8,2) DEFAULT NULL COMMENT '观看奖励金币',
  `daily_limit` int DEFAULT NULL COMMENT '每日观看限制',
  `min_watch_duration` int DEFAULT NULL COMMENT '最少观看时长（秒）',
  `weight` int DEFAULT NULL COMMENT '权重（用于随机选择）',
  `status` enum('ACTIVE','DISABLED') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '状态',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `created_time` datetime DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ad_configs`
--

LOCK TABLES `ad_configs` WRITE;
/*!40000 ALTER TABLE `ad_configs` DISABLE KEYS */;
INSERT INTO `ad_configs` (`id`, `name`, `ad_type`, `video_url`, `webpage_url`, `image_url`, `duration`, `reward_coins`, `daily_limit`, `min_watch_duration`, `weight`, `status`, `start_time`, `end_time`, `created_time`, `updated_time`) VALUES (5,'淘宝购物广告','webpage',NULL,'https://www.taobao.com',NULL,10,5.00,100,5,10,'ACTIVE',NULL,NULL,'2025-08-21 13:41:11','2025-09-16 10:09:51'),(6,'京东商城广告','webpage',NULL,'https://www.jd.com',NULL,15,8.00,100,8,10,'ACTIVE',NULL,NULL,'2025-08-21 13:41:11','2025-09-16 10:07:45'),(8,'奔驰官网','video','https://moneyyy.oss-cn-qingdao.aliyuncs.com/%E4%B8%8B%E8%BD%BD.mp4','https://www.mercedes-benz.com.cn/',NULL,30,10.00,10,15,11,'ACTIVE',NULL,NULL,'2025-08-23 11:28:31','2025-09-16 14:00:57'),(9,'汽车广告视频','video','https://moneyyy.oss-cn-qingdao.aliyuncs.com/%E4%B8%8B%E8%BD%BD.mp4',NULL,NULL,30,15.00,20,10,10,'ACTIVE',NULL,NULL,'2025-09-16 10:08:47','2025-09-16 14:00:03'),(10,'字节跳动视频广告','video','https://moneyyy.oss-cn-qingdao.aliyuncs.com/%E4%B8%8B%E8%BD%BD.mp4',NULL,NULL,25,12.00,15,8,15,'ACTIVE',NULL,NULL,'2025-09-16 10:14:38','2025-09-16 14:00:14');
/*!40000 ALTER TABLE `ad_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ad_watch_records`
--

DROP TABLE IF EXISTS `ad_watch_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ad_watch_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `ad_id` int NOT NULL,
  `watch_duration` int NOT NULL COMMENT '实际观看时长（毫秒）',
  `reward_coins` decimal(8,2) DEFAULT NULL COMMENT '获得金币',
  `is_completed` tinyint(1) DEFAULT NULL COMMENT '是否完整观看',
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  `device_info` text COLLATE utf8mb4_unicode_ci COMMENT '设备信息',
  `watch_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_ad_id` (`ad_id`),
  KEY `idx_watch_time` (`watch_time`),
  CONSTRAINT `fk_ad_watch_ad` FOREIGN KEY (`ad_id`) REFERENCES `ad_configs` (`id`),
  CONSTRAINT `fk_ad_watch_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ad_watch_records`
--

LOCK TABLES `ad_watch_records` WRITE;
/*!40000 ALTER TABLE `ad_watch_records` DISABLE KEYS */;
INSERT INTO `ad_watch_records` (`id`, `user_id`, `ad_id`, `watch_duration`, `reward_coins`, `is_completed`, `ip_address`, `device_info`, `watch_time`) VALUES (1,9,5,10727,5.00,1,'112.229.162.152','Android','2025-08-21 18:38:02'),(2,9,5,10747,5.00,1,'112.229.162.152','Android','2025-08-21 18:54:17'),(3,9,5,10688,5.00,1,'112.229.162.152','Android','2025-08-21 18:54:56'),(5,9,6,15606,8.00,1,'112.229.162.152','Android','2025-08-22 18:08:47'),(6,9,5,10539,5.00,1,'60.255.166.105','Android','2025-08-23 10:14:25'),(9,9,6,15424,8.00,1,'60.255.166.105','Android','2025-08-23 10:17:09'),(10,9,6,15303,8.00,1,'60.255.166.105','Android','2025-08-23 10:20:06'),(11,9,5,10216,5.00,1,'60.255.166.105','Android','2025-08-23 10:20:45'),(12,9,6,15283,8.00,1,'60.255.166.105','Android','2025-08-23 10:23:44'),(13,9,6,15311,8.00,1,'60.255.166.105','Android','2025-08-23 10:24:16'),(16,9,6,15292,8.00,1,'60.255.166.105','Android','2025-08-23 10:29:14'),(17,9,6,15307,8.00,1,'60.255.166.105','Android','2025-08-23 10:29:55'),(19,9,5,10238,5.00,1,'60.255.166.105','Android','2025-08-23 11:29:33'),(21,9,6,15348,8.00,1,'183.220.102.51','Android','2025-08-23 11:30:20'),(36,9,5,10,5.00,1,'119.162.121.211','Android','2025-08-30 09:32:20'),(38,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 09:38:01'),(40,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 09:48:38'),(41,9,5,10,5.00,1,'119.162.121.211','Android','2025-08-30 09:53:02'),(42,9,5,13,5.00,1,'119.162.121.211','Android','2025-08-30 09:53:03'),(43,9,5,12,5.00,1,'119.162.121.211','Android','2025-08-30 09:53:03'),(44,9,5,10,5.00,1,'119.162.121.211','Android','2025-08-30 09:53:41'),(47,9,5,10,5.00,1,'119.162.121.211','Android','2025-08-30 10:15:55'),(48,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 10:17:14'),(49,9,5,15,5.00,1,'172.105.197.232','Test','2025-08-30 10:18:46'),(51,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 10:26:41'),(53,9,5,10,5.00,1,'119.162.121.211','Android','2025-08-30 10:46:42'),(54,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 10:47:24'),(55,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 10:47:58'),(56,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 11:36:03'),(57,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-30 11:36:41'),(58,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-31 09:13:04'),(59,9,6,15,8.00,1,'119.162.121.211','Android','2025-08-31 09:13:46'),(61,9,6,15,8.00,1,'117.175.136.109','Android','2025-08-31 12:37:29'),(62,9,6,15,8.00,1,'117.175.136.109','Android','2025-08-31 12:38:03'),(63,9,6,15,8.00,1,'117.175.136.109','Android','2025-08-31 12:38:52'),(64,9,6,15,8.00,1,'117.175.136.109','Android','2025-08-31 12:39:23'),(65,9,5,15,5.00,1,'172.105.197.232','Test','2025-09-01 23:14:28'),(66,9,5,10,5.00,1,'119.162.121.211','Android','2025-09-01 23:54:07'),(67,9,6,15,8.00,1,'119.162.121.211','Android','2025-09-01 23:57:27'),(68,9,5,10,5.00,1,'119.162.121.211','Android','2025-09-01 23:59:06'),(69,9,5,10,5.00,1,'119.162.121.211','Android','2025-09-02 01:05:33'),(70,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 08:40:19'),(71,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 08:40:52'),(72,15,6,15,8.00,1,'117.173.241.107','Android','2025-09-02 08:41:59'),(73,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 08:42:26'),(74,15,6,9,0.00,0,'117.173.241.107','Android','2025-09-02 08:42:57'),(75,15,5,6,0.00,0,'117.173.241.107','Android','2025-09-02 08:43:28'),(76,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 08:44:05'),(77,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 08:44:38'),(78,15,6,9,0.00,0,'117.173.241.107','Android','2025-09-02 08:45:08'),(79,15,6,9,0.00,0,'117.173.241.107','Android','2025-09-02 08:45:41'),(80,15,5,6,0.00,0,'117.173.241.107','Android','2025-09-02 09:08:46'),(81,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 09:09:22'),(82,15,5,10,5.00,1,'117.173.241.107','Android','2025-09-02 09:09:55'),(83,15,6,9,0.00,0,'60.255.166.243','Android','2025-09-03 07:38:56'),(84,15,5,10,5.00,1,'60.255.166.243','Android','2025-09-03 07:40:33'),(85,9,5,10,5.00,1,'117.175.136.108','Android','2025-09-03 11:53:25'),(86,9,6,15,8.00,1,'117.175.136.108','Android','2025-09-03 11:54:47'),(87,9,5,10,5.00,1,'117.175.136.108','Android','2025-09-03 11:55:15'),(88,1,6,30,8.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:11'),(89,1,6,15,8.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:12'),(90,2,5,10,5.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:13'),(91,3,5,10,5.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:15'),(92,4,6,15,8.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:16'),(93,1,5,10,5.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:18'),(94,1,5,10,5.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:20'),(95,1,6,15,8.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:21'),(96,1,8,30,10.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:23'),(97,1,8,30,10.00,1,'106.180.225.87',NULL,'2025-09-16 10:03:24'),(98,9,6,15,8.00,1,'112.232.17.116','Android','2025-09-16 10:03:29'),(99,9,6,15,8.00,1,'112.232.17.116','Android','2025-09-16 10:04:10'),(100,9,10,37,12.00,1,'112.232.17.116','Android','2025-09-16 10:16:00'),(101,9,6,15,8.00,1,'112.232.17.116','Android','2025-09-16 10:16:25'),(102,16,5,10,5.00,1,'111.55.145.30','Android','2025-09-16 12:49:55'),(103,16,6,15,8.00,1,'111.55.145.30','Android','2025-09-16 12:50:31'),(104,16,6,15,8.00,1,'111.55.145.30','Android','2025-09-16 12:51:09'),(105,9,5,10,5.00,1,'112.232.17.116','Android','2025-09-16 13:54:49'),(106,9,5,8,0.00,0,'112.232.17.116','Android','2025-09-16 13:55:55'),(107,9,6,15,8.00,1,'112.232.17.116','Android','2025-09-16 13:57:12'),(108,16,5,10,5.00,1,'111.55.145.30','Android','2025-09-16 13:59:03'),(109,16,8,30,10.00,1,'111.55.145.30','Android','2025-09-16 13:59:57'),(110,9,8,31,10.00,1,'112.232.17.116','Android','2025-09-16 14:00:53'),(111,9,5,10,5.00,1,'112.232.17.116','Android','2025-09-16 14:01:13'),(112,9,10,26,12.00,1,'112.232.17.116','Android','2025-09-16 14:02:03'),(113,9,5,10,5.00,1,'112.232.17.116','Android','2025-09-16 14:03:39'),(114,16,6,15,8.00,1,'111.55.145.30','Android','2025-09-16 14:06:24'),(115,16,6,15,8.00,1,'111.55.145.30','Android','2025-09-16 14:07:02'),(116,16,10,26,12.00,1,'111.55.145.30','Android','2025-09-16 14:07:48'),(117,16,6,36,8.00,1,'111.55.145.30','Android','2025-09-16 14:16:56'),(118,16,8,26,10.00,1,'111.55.145.30','Android','2025-09-16 14:17:42'),(119,16,8,26,10.00,1,'111.55.145.30','Android','2025-09-16 14:18:13'),(120,15,10,22,12.00,1,'60.255.166.43','Android','2025-09-16 20:52:32'),(121,15,9,26,15.00,1,'60.255.166.43','Android','2025-09-16 20:53:16'),(122,15,6,15,8.00,1,'60.255.166.43','Android','2025-09-16 20:53:39'),(123,15,9,26,15.00,1,'60.255.166.43','Android','2025-09-16 20:54:24');
/*!40000 ALTER TABLE `ad_watch_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `role` enum('SUPER_ADMIN','ADMIN','OPERATOR') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_login_time` datetime DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `status` int DEFAULT NULL COMMENT '状态：1正常，0禁用',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` (`id`, `username`, `password_hash`, `email`, `role`, `last_login_time`, `created_time`, `status`) VALUES (1,'admin','admin123','admin@game.com','SUPER_ADMIN',NULL,'2025-08-21 13:13:58',1);
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coin_transactions`
--

DROP TABLE IF EXISTS `coin_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coin_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` enum('AD_REWARD','GAME_REWARD','WITHDRAW','REGISTER_REWARD','ADMIN_ADJUST') COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL COMMENT '金币数量（正数为收入，负数为支出）',
  `balance_after` decimal(10,2) NOT NULL COMMENT '操作后余额',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '描述',
  `related_id` int DEFAULT NULL COMMENT '关联ID（如广告ID、游戏记录ID等）',
  `created_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_time` (`user_id`,`created_time`),
  CONSTRAINT `coin_transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coin_transactions`
--

LOCK TABLES `coin_transactions` WRITE;
/*!40000 ALTER TABLE `coin_transactions` DISABLE KEYS */;
INSERT INTO `coin_transactions` (`id`, `user_id`, `type`, `amount`, `balance_after`, `description`, `related_id`, `created_time`) VALUES (1,9,'AD_REWARD',5.00,5.00,'观看广告奖励: 淘宝购物广告',2,'2025-08-21 18:54:17'),(2,9,'AD_REWARD',5.00,10.00,'观看广告奖励: 淘宝购物广告',3,'2025-08-21 18:54:56'),(3,9,'AD_REWARD',50.00,60.00,'观看广告奖励: 游戏推广广告',4,'2025-08-21 19:11:43'),(4,10,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-22 12:05:17'),(5,11,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-22 12:05:17'),(6,12,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-22 12:05:17'),(7,13,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-22 12:05:17'),(8,14,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-22 12:05:17'),(9,10,'GAME_REWARD',15.00,115.00,'游戏奖励 - 得分: 2580',1,'2025-08-22 12:05:17'),(10,10,'GAME_REWARD',15.00,130.00,'游戏奖励 - 得分: 2200',2,'2025-08-22 12:05:17'),(11,10,'GAME_REWARD',15.00,145.00,'游戏奖励 - 得分: 1900',3,'2025-08-22 12:05:17'),(12,10,'GAME_REWARD',15.00,160.00,'游戏奖励 - 得分: 2100',4,'2025-08-22 12:05:17'),(13,11,'GAME_REWARD',15.00,115.00,'游戏奖励 - 得分: 2340',5,'2025-08-22 12:05:17'),(14,11,'GAME_REWARD',15.00,130.00,'游戏奖励 - 得分: 2000',6,'2025-08-22 12:05:17'),(15,11,'GAME_REWARD',15.00,145.00,'游戏奖励 - 得分: 1800',7,'2025-08-22 12:05:17'),(16,11,'GAME_REWARD',15.00,160.00,'游戏奖励 - 得分: 1950',8,'2025-08-22 12:05:17'),(17,12,'GAME_REWARD',15.00,115.00,'游戏奖励 - 得分: 2100',9,'2025-08-22 12:05:17'),(18,12,'GAME_REWARD',15.00,130.00,'游戏奖励 - 得分: 1850',10,'2025-08-22 12:05:17'),(19,12,'GAME_REWARD',15.00,145.00,'游戏奖励 - 得分: 1750',11,'2025-08-22 12:05:17'),(20,12,'GAME_REWARD',15.00,160.00,'游戏奖励 - 得分: 1900',12,'2025-08-22 12:05:17'),(21,13,'GAME_REWARD',15.00,115.00,'游戏奖励 - 得分: 1980',13,'2025-08-22 12:05:17'),(22,13,'GAME_REWARD',15.00,130.00,'游戏奖励 - 得分: 1700',14,'2025-08-22 12:05:17'),(23,13,'GAME_REWARD',15.00,145.00,'游戏奖励 - 得分: 1600',15,'2025-08-22 12:05:18'),(24,13,'GAME_REWARD',15.00,160.00,'游戏奖励 - 得分: 1800',16,'2025-08-22 12:05:18'),(25,14,'GAME_REWARD',11.00,111.00,'游戏奖励 - 得分: 680',17,'2025-08-22 12:05:18'),(26,14,'GAME_REWARD',10.00,121.00,'游戏奖励 - 得分: 550',18,'2025-08-22 12:05:18'),(27,14,'GAME_REWARD',9.00,130.00,'游戏奖励 - 得分: 420',19,'2025-08-22 12:05:18'),(28,14,'GAME_REWARD',11.00,141.00,'游戏奖励 - 得分: 600',20,'2025-08-22 12:05:18'),(29,9,'AD_REWARD',8.00,68.00,'观看广告奖励: 京东商城广告',5,'2025-08-22 18:08:47'),(30,15,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-23 10:13:02'),(31,9,'AD_REWARD',5.00,73.00,'观看广告奖励: 淘宝购物广告',6,'2025-08-23 10:14:25'),(32,9,'AD_REWARD',60.00,133.00,'观看广告奖励: 购物广告',7,'2025-08-23 10:16:01'),(33,9,'AD_REWARD',6.00,139.00,'观看广告奖励: 天猫超市广告',8,'2025-08-23 10:16:32'),(34,9,'AD_REWARD',8.00,147.00,'观看广告奖励: 京东商城广告',9,'2025-08-23 10:17:09'),(35,9,'AD_REWARD',8.00,155.00,'观看广告奖励: 京东商城广告',10,'2025-08-23 10:20:06'),(36,9,'AD_REWARD',5.00,160.00,'观看广告奖励: 淘宝购物广告',11,'2025-08-23 10:20:45'),(37,16,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-23 10:20:54'),(38,9,'AD_REWARD',8.00,168.00,'观看广告奖励: 京东商城广告',12,'2025-08-23 10:23:44'),(39,17,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-23 10:24:09'),(40,9,'AD_REWARD',8.00,176.00,'观看广告奖励: 京东商城广告',13,'2025-08-23 10:24:16'),(41,9,'AD_REWARD',6.00,182.00,'观看广告奖励: 天猫超市广告',14,'2025-08-23 10:27:56'),(42,9,'AD_REWARD',30.00,212.00,'观看广告奖励: 品牌推广广告',15,'2025-08-23 10:29:06'),(43,9,'AD_REWARD',8.00,220.00,'观看广告奖励: 京东商城广告',16,'2025-08-23 10:29:14'),(44,9,'AD_REWARD',8.00,228.00,'观看广告奖励: 京东商城广告',17,'2025-08-23 10:29:55'),(45,9,'AD_REWARD',50.00,278.00,'观看广告奖励: 游戏推广广告',18,'2025-08-23 10:31:59'),(46,18,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-08-23 11:25:01'),(47,9,'AD_REWARD',5.00,283.00,'观看广告奖励: 淘宝购物广告',19,'2025-08-23 11:29:33'),(48,9,'AD_REWARD',6.00,289.00,'观看广告奖励: 天猫超市广告',20,'2025-08-23 11:29:40'),(49,9,'AD_REWARD',8.00,297.00,'观看广告奖励: 京东商城广告',21,'2025-08-23 11:30:20'),(50,9,'AD_REWARD',60.00,357.00,'观看广告奖励: 购物广告',22,'2025-08-23 11:30:31'),(51,9,'AD_REWARD',6.00,363.00,'观看广告奖励: 天猫超市广告',23,'2025-08-23 11:30:51'),(52,9,'AD_REWARD',50.00,413.00,'观看广告奖励: 游戏推广广告',24,'2025-08-23 11:31:18'),(53,9,'AD_REWARD',6.00,419.00,'观看广告奖励: 天猫超市广告',25,'2025-08-23 11:31:44'),(54,9,'AD_REWARD',50.00,469.00,'观看广告奖励: 游戏推广广告',26,'2025-08-30 08:51:39'),(55,9,'AD_REWARD',50.00,519.00,'观看广告奖励: 游戏推广广告',27,'2025-08-30 08:53:45'),(56,9,'AD_REWARD',50.00,569.00,'观看广告奖励: 游戏推广广告',28,'2025-08-30 09:01:38'),(57,9,'AD_REWARD',50.00,619.00,'观看广告奖励: 游戏推广广告',29,'2025-08-30 09:01:40'),(58,9,'AD_REWARD',50.00,669.00,'观看广告奖励: 游戏推广广告',30,'2025-08-30 09:06:20'),(59,9,'AD_REWARD',80.00,749.00,'观看广告奖励: 应用下载广告',31,'2025-08-30 09:08:41'),(60,9,'AD_REWARD',30.00,779.00,'观看广告奖励: 品牌推广广告',32,'2025-08-30 09:13:57'),(61,9,'AD_REWARD',80.00,859.00,'观看广告奖励: 应用下载广告',33,'2025-08-30 09:20:54'),(62,9,'AD_REWARD',30.00,889.00,'观看广告奖励: 品牌推广广告',34,'2025-08-30 09:20:58'),(63,9,'AD_REWARD',60.00,949.00,'观看广告奖励: 购物广告',35,'2025-08-30 09:21:00'),(64,9,'AD_REWARD',5.00,954.00,'观看广告奖励: 淘宝购物广告',36,'2025-08-30 09:32:20'),(65,9,'AD_REWARD',6.00,960.00,'观看广告奖励: 天猫超市广告',37,'2025-08-30 09:33:37'),(66,9,'AD_REWARD',8.00,968.00,'观看广告奖励: 京东商城广告',38,'2025-08-30 09:38:01'),(67,9,'AD_REWARD',6.00,974.00,'观看广告奖励: 天猫超市广告',39,'2025-08-30 09:48:03'),(68,9,'AD_REWARD',8.00,982.00,'观看广告奖励: 京东商城广告',40,'2025-08-30 09:48:38'),(69,9,'AD_REWARD',5.00,987.00,'观看广告奖励: 淘宝购物广告',41,'2025-08-30 09:53:02'),(70,9,'AD_REWARD',5.00,992.00,'观看广告奖励: 淘宝购物广告',42,'2025-08-30 09:53:03'),(71,9,'AD_REWARD',5.00,997.00,'观看广告奖励: 淘宝购物广告',43,'2025-08-30 09:53:03'),(72,9,'AD_REWARD',5.00,1002.00,'观看广告奖励: 淘宝购物广告',44,'2025-08-30 09:53:41'),(73,9,'AD_REWARD',80.00,1082.00,'观看广告奖励: 应用下载广告',45,'2025-08-30 09:56:25'),(74,9,'AD_REWARD',6.00,1088.00,'观看广告奖励: 天猫超市广告',46,'2025-08-30 10:15:24'),(75,9,'AD_REWARD',5.00,1093.00,'观看广告奖励: 淘宝购物广告',47,'2025-08-30 10:15:55'),(76,9,'AD_REWARD',8.00,1101.00,'观看广告奖励: 京东商城广告',48,'2025-08-30 10:17:14'),(77,9,'AD_REWARD',5.00,1106.00,'观看广告奖励: 淘宝购物广告',49,'2025-08-30 10:18:46'),(78,9,'AD_REWARD',30.00,1136.00,'观看广告奖励: 品牌推广广告',50,'2025-08-30 10:21:26'),(79,9,'AD_REWARD',8.00,1144.00,'观看广告奖励: 京东商城广告',51,'2025-08-30 10:26:41'),(80,9,'AD_REWARD',30.00,1174.00,'观看广告奖励: 品牌推广广告',52,'2025-08-30 10:28:00'),(81,9,'AD_REWARD',5.00,1179.00,'观看广告奖励: 淘宝购物广告',53,'2025-08-30 10:46:42'),(82,9,'AD_REWARD',8.00,1187.00,'观看广告奖励: 京东商城广告',54,'2025-08-30 10:47:24'),(83,9,'AD_REWARD',8.00,1195.00,'观看广告奖励: 京东商城广告',55,'2025-08-30 10:47:58'),(84,9,'AD_REWARD',8.00,1203.00,'观看广告奖励: 京东商城广告',56,'2025-08-30 11:36:03'),(85,9,'AD_REWARD',8.00,1211.00,'观看广告奖励: 京东商城广告',57,'2025-08-30 11:36:41'),(86,9,'AD_REWARD',8.00,1219.00,'观看广告奖励: 京东商城广告',58,'2025-08-31 09:13:04'),(87,9,'AD_REWARD',8.00,1227.00,'观看广告奖励: 京东商城广告',59,'2025-08-31 09:13:46'),(88,9,'AD_REWARD',6.00,1233.00,'观看广告奖励: 天猫超市广告',60,'2025-08-31 09:14:17'),(89,9,'AD_REWARD',8.00,1241.00,'观看广告奖励: 京东商城广告',61,'2025-08-31 12:37:29'),(90,9,'AD_REWARD',8.00,1249.00,'观看广告奖励: 京东商城广告',62,'2025-08-31 12:38:03'),(91,9,'AD_REWARD',8.00,1257.00,'观看广告奖励: 京东商城广告',63,'2025-08-31 12:38:52'),(92,9,'AD_REWARD',8.00,1265.00,'观看广告奖励: 京东商城广告',64,'2025-08-31 12:39:23'),(93,19,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-01 22:33:48'),(94,20,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-01 22:33:53'),(95,21,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-01 22:33:53'),(96,20,'GAME_REWARD',6.00,106.00,'游戏奖励 - 得分: 100',21,'2025-09-01 22:34:19'),(97,20,'GAME_REWARD',6.00,112.00,'游戏奖励 - 得分: 100',22,'2025-09-01 22:34:19'),(98,20,'GAME_REWARD',6.00,118.00,'游戏奖励 - 得分: 100',23,'2025-09-01 22:34:19'),(99,20,'GAME_REWARD',6.00,124.00,'游戏奖励 - 得分: 100',24,'2025-09-01 22:34:19'),(100,20,'GAME_REWARD',6.00,130.00,'游戏奖励 - 得分: 100',25,'2025-09-01 22:34:19'),(101,20,'GAME_REWARD',6.00,136.00,'游戏奖励 - 得分: 100',26,'2025-09-01 23:13:37'),(102,20,'GAME_REWARD',6.00,142.00,'游戏奖励 - 得分: 100',27,'2025-09-01 23:13:37'),(103,20,'GAME_REWARD',6.00,148.00,'游戏奖励 - 得分: 100',28,'2025-09-01 23:13:37'),(104,20,'GAME_REWARD',6.00,154.00,'游戏奖励 - 得分: 100',29,'2025-09-01 23:13:37'),(105,20,'GAME_REWARD',6.00,160.00,'游戏奖励 - 得分: 100',30,'2025-09-01 23:13:38'),(106,9,'AD_REWARD',5.00,1270.00,'观看广告奖励: 淘宝购物广告',65,'2025-09-01 23:14:28'),(107,22,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-01 23:19:53'),(108,23,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-01 23:31:40'),(109,23,'WITHDRAW',-50.00,50.00,'提现申请 - 5.0元',NULL,'2025-09-01 23:37:55'),(110,9,'AD_REWARD',5.00,1275.00,'观看广告奖励: 淘宝购物广告',66,'2025-09-01 23:54:07'),(111,9,'AD_REWARD',8.00,1283.00,'观看广告奖励: 京东商城广告',67,'2025-09-01 23:57:27'),(112,24,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-01 23:57:44'),(113,9,'AD_REWARD',5.00,1288.00,'观看广告奖励: 淘宝购物广告',68,'2025-09-01 23:59:06'),(114,25,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-02 00:03:24'),(115,25,'GAME_REWARD',10.00,110.00,'游戏奖励 - 得分: 500',31,'2025-09-02 00:03:25'),(116,26,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-02 00:15:51'),(117,27,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-02 00:22:15'),(118,27,'WITHDRAW',-11.00,89.00,'提现申请 - 1.0元',NULL,'2025-09-02 00:22:15'),(119,9,'WITHDRAW',-11.00,1277.00,'提现申请 - 1.0元',NULL,'2025-09-02 00:24:08'),(120,28,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-02 00:24:55'),(121,28,'WITHDRAW',-11.00,89.00,'提现申请 - 1.0元',NULL,'2025-09-02 00:24:55'),(122,29,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-02 00:30:59'),(123,29,'WITHDRAW',-11.00,89.00,'提现申请 - 1.0元',NULL,'2025-09-02 00:31:08'),(124,9,'ADMIN_ADJUST',11.00,1288.00,'提现申请被拒绝，退还金币 - 申请ID: 3',3,'2025-09-02 00:47:22'),(125,30,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-02 00:48:13'),(126,30,'WITHDRAW',-22.00,78.00,'提现申请 - 2.0元',NULL,'2025-09-02 00:48:13'),(127,30,'ADMIN_ADJUST',22.00,100.00,'提现申请被拒绝，退还金币 - 申请ID: 6',6,'2025-09-02 00:48:13'),(128,9,'AD_REWARD',5.00,1293.00,'观看广告奖励: 淘宝购物广告',69,'2025-09-02 01:05:33'),(129,15,'AD_REWARD',5.00,105.00,'观看广告奖励: 淘宝购物广告',70,'2025-09-02 08:40:19'),(130,15,'AD_REWARD',5.00,110.00,'观看广告奖励: 淘宝购物广告',71,'2025-09-02 08:40:52'),(131,15,'AD_REWARD',8.00,118.00,'观看广告奖励: 京东商城广告',72,'2025-09-02 08:41:59'),(132,15,'AD_REWARD',5.00,123.00,'观看广告奖励: 淘宝购物广告',73,'2025-09-02 08:42:26'),(133,15,'AD_REWARD',5.00,128.00,'观看广告奖励: 淘宝购物广告',76,'2025-09-02 08:44:05'),(134,15,'AD_REWARD',5.00,133.00,'观看广告奖励: 淘宝购物广告',77,'2025-09-02 08:44:38'),(135,15,'AD_REWARD',5.00,138.00,'观看广告奖励: 淘宝购物广告',81,'2025-09-02 09:09:23'),(136,15,'AD_REWARD',5.00,143.00,'观看广告奖励: 淘宝购物广告',82,'2025-09-02 09:09:55'),(137,15,'AD_REWARD',5.00,148.00,'观看广告奖励: 淘宝购物广告',84,'2025-09-03 07:40:33'),(138,9,'AD_REWARD',5.00,1298.00,'观看广告奖励: 淘宝购物广告',85,'2025-09-03 11:53:25'),(139,9,'AD_REWARD',8.00,1306.00,'观看广告奖励: 京东商城广告',86,'2025-09-03 11:54:47'),(140,9,'AD_REWARD',5.00,1311.00,'观看广告奖励: 淘宝购物广告',87,'2025-09-03 11:55:15'),(141,1,'AD_REWARD',8.00,8.00,'观看广告奖励: 京东商城广告',88,'2025-09-16 10:03:11'),(142,1,'AD_REWARD',8.00,16.00,'观看广告奖励: 京东商城广告',89,'2025-09-16 10:03:12'),(143,2,'AD_REWARD',5.00,5.00,'观看广告奖励: 淘宝购物广告',90,'2025-09-16 10:03:13'),(144,3,'AD_REWARD',5.00,5.00,'观看广告奖励: 淘宝购物广告',91,'2025-09-16 10:03:15'),(145,4,'AD_REWARD',8.00,8.00,'观看广告奖励: 京东商城广告',92,'2025-09-16 10:03:16'),(146,1,'AD_REWARD',5.00,21.00,'观看广告奖励: 淘宝购物广告',93,'2025-09-16 10:03:18'),(147,1,'AD_REWARD',5.00,26.00,'观看广告奖励: 淘宝购物广告',94,'2025-09-16 10:03:20'),(148,1,'AD_REWARD',8.00,34.00,'观看广告奖励: 京东商城广告',95,'2025-09-16 10:03:21'),(149,1,'AD_REWARD',10.00,44.00,'观看广告奖励: 奔驰',96,'2025-09-16 10:03:23'),(150,1,'AD_REWARD',10.00,54.00,'观看广告奖励: 奔驰',97,'2025-09-16 10:03:24'),(151,9,'AD_REWARD',8.00,1319.00,'观看广告奖励: 京东商城广告',98,'2025-09-16 10:03:29'),(152,9,'AD_REWARD',8.00,1327.00,'观看广告奖励: 京东商城广告',99,'2025-09-16 10:04:10'),(153,9,'AD_REWARD',12.00,1339.00,'观看广告奖励: 字节跳动视频广告',100,'2025-09-16 10:16:00'),(154,9,'AD_REWARD',8.00,1347.00,'观看广告奖励: 京东商城广告',101,'2025-09-16 10:16:25'),(155,31,'REGISTER_REWARD',100.00,100.00,'注册奖励',NULL,'2025-09-16 10:18:22'),(156,16,'AD_REWARD',5.00,105.00,'观看广告奖励: 淘宝购物广告',102,'2025-09-16 12:49:55'),(157,16,'AD_REWARD',8.00,113.00,'观看广告奖励: 京东商城广告',103,'2025-09-16 12:50:31'),(158,16,'AD_REWARD',8.00,121.00,'观看广告奖励: 京东商城广告',104,'2025-09-16 12:51:09'),(159,9,'AD_REWARD',5.00,1352.00,'观看广告奖励: 淘宝购物广告',105,'2025-09-16 13:54:49'),(160,9,'AD_REWARD',8.00,1360.00,'观看广告奖励: 京东商城广告',107,'2025-09-16 13:57:12'),(161,16,'AD_REWARD',5.00,126.00,'观看广告奖励: 淘宝购物广告',108,'2025-09-16 13:59:03'),(162,16,'AD_REWARD',10.00,136.00,'观看广告奖励: 奔驰官网',109,'2025-09-16 13:59:57'),(163,9,'AD_REWARD',10.00,1370.00,'观看广告奖励: 奔驰官网',110,'2025-09-16 14:00:53'),(164,9,'AD_REWARD',5.00,1375.00,'观看广告奖励: 淘宝购物广告',111,'2025-09-16 14:01:13'),(165,9,'AD_REWARD',12.00,1387.00,'观看广告奖励: 字节跳动视频广告',112,'2025-09-16 14:02:03'),(166,9,'AD_REWARD',5.00,1392.00,'观看广告奖励: 淘宝购物广告',113,'2025-09-16 14:03:39'),(167,16,'AD_REWARD',8.00,144.00,'观看广告奖励: 京东商城广告',114,'2025-09-16 14:06:24'),(168,16,'AD_REWARD',8.00,152.00,'观看广告奖励: 京东商城广告',115,'2025-09-16 14:07:02'),(169,16,'AD_REWARD',12.00,164.00,'观看广告奖励: 字节跳动视频广告',116,'2025-09-16 14:07:48'),(170,16,'AD_REWARD',8.00,172.00,'观看广告奖励: 京东商城广告',117,'2025-09-16 14:16:56'),(171,16,'AD_REWARD',10.00,182.00,'观看广告奖励: 奔驰官网',118,'2025-09-16 14:17:42'),(172,16,'AD_REWARD',10.00,192.00,'观看广告奖励: 奔驰官网',119,'2025-09-16 14:18:13'),(173,15,'AD_REWARD',12.00,160.00,'观看广告奖励: 字节跳动视频广告',120,'2025-09-16 20:52:32'),(174,15,'AD_REWARD',15.00,175.00,'观看广告奖励: 汽车广告视频',121,'2025-09-16 20:53:16'),(175,15,'AD_REWARD',8.00,183.00,'观看广告奖励: 京东商城广告',122,'2025-09-16 20:53:39'),(176,15,'AD_REWARD',15.00,198.00,'观看广告奖励: 汽车广告视频',123,'2025-09-16 20:54:24'),(177,15,'WITHDRAW',-108900.00,329100.00,'提现申请 - 30.0元',NULL,'2025-09-16 20:56:47');
/*!40000 ALTER TABLE `coin_transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `game_records`
--

DROP TABLE IF EXISTS `game_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `score` int NOT NULL COMMENT '游戏得分',
  `duration` int NOT NULL COMMENT '游戏时长（秒）',
  `needles_inserted` int DEFAULT NULL COMMENT '成功插入针数',
  `reward_coins` decimal(8,2) DEFAULT NULL COMMENT '奖励金币',
  `play_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_score_time` (`score`,`play_time`),
  KEY `idx_user_score` (`user_id`,`score`),
  CONSTRAINT `game_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_records`
--

LOCK TABLES `game_records` WRITE;
/*!40000 ALTER TABLE `game_records` DISABLE KEYS */;
INSERT INTO `game_records` (`id`, `user_id`, `score`, `duration`, `needles_inserted`, `reward_coins`, `play_time`) VALUES (1,10,2580,72,49,15.00,'2025-08-22 12:05:17'),(2,10,2200,155,13,15.00,'2025-08-22 12:05:17'),(3,10,1900,133,43,15.00,'2025-08-22 12:05:17'),(4,10,2100,238,26,15.00,'2025-08-22 12:05:17'),(5,11,2340,262,45,15.00,'2025-08-22 12:05:17'),(6,11,2000,64,21,15.00,'2025-08-22 12:05:17'),(7,11,1800,125,39,15.00,'2025-08-22 12:05:17'),(8,11,1950,222,48,15.00,'2025-08-22 12:05:17'),(9,12,2100,121,28,15.00,'2025-08-22 12:05:17'),(10,12,1850,79,12,15.00,'2025-08-22 12:05:17'),(11,12,1750,118,18,15.00,'2025-08-22 12:05:17'),(12,12,1900,290,10,15.00,'2025-08-22 12:05:17'),(13,13,1980,145,23,15.00,'2025-08-22 12:05:17'),(14,13,1700,95,32,15.00,'2025-08-22 12:05:17'),(15,13,1600,263,30,15.00,'2025-08-22 12:05:18'),(16,13,1800,66,28,15.00,'2025-08-22 12:05:18'),(17,14,680,174,49,11.00,'2025-08-22 12:05:18'),(18,14,550,240,20,10.00,'2025-08-22 12:05:18'),(19,14,420,70,35,9.00,'2025-08-22 12:05:18'),(20,14,600,125,37,11.00,'2025-08-22 12:05:18'),(21,20,100,30,5,6.00,'2025-09-01 22:34:19'),(22,20,100,30,5,6.00,'2025-09-01 22:34:19'),(23,20,100,30,5,6.00,'2025-09-01 22:34:19'),(24,20,100,30,5,6.00,'2025-09-01 22:34:19'),(25,20,100,30,5,6.00,'2025-09-01 22:34:19'),(26,20,100,30,5,6.00,'2025-09-01 23:13:37'),(27,20,100,30,5,6.00,'2025-09-01 23:13:37'),(28,20,100,30,5,6.00,'2025-09-01 23:13:37'),(29,20,100,30,5,6.00,'2025-09-01 23:13:37'),(30,20,100,30,5,6.00,'2025-09-01 23:13:38'),(31,25,500,60,20,10.00,'2025-09-02 00:03:25');
/*!40000 ALTER TABLE `game_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_configs`
--

DROP TABLE IF EXISTS `system_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `config_value` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置描述',
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_configs`
--

LOCK TABLES `system_configs` WRITE;
/*!40000 ALTER TABLE `system_configs` DISABLE KEYS */;
INSERT INTO `system_configs` (`id`, `config_key`, `config_value`, `description`, `updated_time`) VALUES (1,'coin_to_rmb_rate','3300','金币兑换人民币比例（多少金币=1元）','2025-09-16 20:54:47'),(2,'min_withdraw_amount','1','最小提现金额（元）','2025-08-21 17:04:33'),(3,'max_withdraw_amount','500','最大提现金额（元）','2025-08-18 16:43:04'),(4,'daily_ad_limit','1000','每日广告观看上限','2025-08-30 10:15:00'),(5,'game_reward_coins','5','完成一局游戏奖励金币','2025-08-18 16:43:04'),(6,'register_reward_coins','100','注册奖励金币','2025-08-18 16:43:04'),(7,'level_up_reward_coins','50','升级奖励金币','2025-08-18 16:43:04'),(8,'max_daily_game_rewards','10','每日最大游戏奖励次数','2025-08-18 16:43:04'),(9,'ad_reward_coins_min','50','观看广告最小奖励金币','2025-08-21 15:35:44'),(10,'ad_reward_coins_max','200','观看广告最大奖励金币','2025-08-21 15:35:44'),(11,'ad_reward_coins_default','100','观看广告默认奖励金币','2025-08-21 15:35:44'),(12,'video_ad_min_duration','15','视频广告最小观看时长（秒）','2025-08-21 15:35:44'),(13,'webpage_ad_min_duration','10','网页广告最小观看时长（秒）','2025-08-21 15:35:44'),(14,'exchange_rate_enabled','1','是否启用动态汇率（1启用，0禁用）','2025-08-21 15:35:44'),(15,'exchange_rate_update_interval','3600','汇率更新间隔（秒）','2025-08-21 15:35:44'),(16,'withdrawal_fee_rate','10','提现手续费率（百分比，0表示免费）','2025-09-16 20:54:47'),(17,'withdrawal_min_coins','50','提现最小金币数量','2025-09-16 20:54:47');
/*!40000 ALTER TABLE `system_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_level_configs`
--

DROP TABLE IF EXISTS `user_level_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_level_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `level` int NOT NULL COMMENT '用户等级',
  `level_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '等级名称',
  `ad_coin_multiplier` decimal(3,2) DEFAULT NULL COMMENT '广告金币倍数',
  `game_coin_multiplier` decimal(3,2) DEFAULT NULL COMMENT '游戏金币倍数',
  `min_experience` int DEFAULT NULL COMMENT '该等级所需最小经验值',
  `max_experience` int DEFAULT NULL COMMENT '该等级最大经验值（null表示无上限）',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '等级描述',
  `is_active` int DEFAULT NULL COMMENT '是否启用：1启用，0禁用',
  `created_time` datetime DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `level` (`level`),
  KEY `idx_level` (`level`),
  KEY `idx_experience_range` (`min_experience`,`max_experience`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_level_configs`
--

LOCK TABLES `user_level_configs` WRITE;
/*!40000 ALTER TABLE `user_level_configs` DISABLE KEYS */;
INSERT INTO `user_level_configs` (`id`, `level`, `level_name`, `ad_coin_multiplier`, `game_coin_multiplier`, `min_experience`, `max_experience`, `description`, `is_active`, `created_time`, `updated_time`) VALUES (1,1,'新手',1.00,1.00,0,999,'初始等级，正常金币奖励',1,'2025-09-05 19:15:06','2025-09-05 19:15:06'),(2,2,'青铜',1.20,1.10,1000,2999,'广告金币+20%，游戏金币+10%',1,'2025-09-05 19:15:06','2025-09-05 19:15:06'),(3,3,'白银',1.50,1.20,3000,5999,'广告金币+50%，游戏金币+20%',1,'2025-09-05 19:15:06','2025-09-05 19:15:06'),(4,4,'黄金',1.80,1.30,6000,9999,'广告金币+80%，游戏金币+30%',1,'2025-09-05 19:15:06','2025-09-05 19:15:06'),(5,5,'铂金',2.00,1.50,10000,19999,'广告金币+100%，游戏金币+50%',1,'2025-09-05 19:15:06','2025-09-05 19:15:06'),(6,6,'钻石',2.50,1.80,20000,39999,'广告金币+150%，游戏金币+80%',1,'2025-09-05 19:15:06','2025-09-05 19:15:06');
/*!40000 ALTER TABLE `user_level_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `device_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '设备唯一标识',
  `device_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '设备名称（手机型号等）',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户名（可选）',
  `nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '昵称',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `coins` decimal(10,2) DEFAULT NULL COMMENT '金币余额',
  `total_coins` decimal(10,2) DEFAULT NULL COMMENT '历史总金币',
  `level` int DEFAULT NULL COMMENT '用户等级',
  `experience` int DEFAULT NULL COMMENT '经验值',
  `game_count` int DEFAULT NULL COMMENT '游戏次数',
  `best_score` int DEFAULT NULL COMMENT '最高分',
  `last_login_time` datetime DEFAULT NULL COMMENT '最后登录时间',
  `register_time` datetime DEFAULT NULL,
  `status` enum('ACTIVE','DISABLED') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '状态',
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_id` (`device_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`, `device_id`, `device_name`, `username`, `nickname`, `avatar`, `coins`, `total_coins`, `level`, `experience`, `game_count`, `best_score`, `last_login_time`, `register_time`, `status`) VALUES (1,'device_5ac087e538da91b1_503','Google Pixel 6',NULL,'玩家1535',NULL,54.00,54.00,1,0,0,0,'2025-08-21 15:36:46','2025-08-21 13:07:05','ACTIVE'),(2,'device_5ac087e538da91b1_345','Google Pixel 6',NULL,'玩家6009',NULL,5.00,5.00,1,0,0,0,'2025-08-21 16:05:20','2025-08-21 16:03:01','ACTIVE'),(3,'device_5ac087e538da91b1_646','Google Pixel 6',NULL,'玩家3762',NULL,5.00,5.00,1,0,0,0,'2025-08-21 17:16:46','2025-08-21 17:16:43','ACTIVE'),(4,'device_5ac087e538da91b1_714','Google Pixel 6',NULL,'玩家9898',NULL,8.00,8.00,1,0,0,0,'2025-08-21 17:47:31','2025-08-21 17:47:26','ACTIVE'),(5,'device_5ac087e538da91b1_544','Google Pixel 6',NULL,'玩家5528',NULL,0.00,0.00,1,0,0,0,'2025-08-21 17:47:54','2025-08-21 17:47:47','ACTIVE'),(6,'device_5ac087e538da91b1_298','Google Pixel 6',NULL,'玩家4538',NULL,0.00,0.00,1,0,0,0,'2025-08-21 17:51:01','2025-08-21 17:48:40','ACTIVE'),(7,'device_5ac087e538da91b1_533','Google Pixel 6',NULL,'玩家3710',NULL,0.00,0.00,1,0,0,0,'2025-08-21 17:51:43','2025-08-21 17:51:41','ACTIVE'),(8,'device_5ac087e538da91b1_685','Google Pixel 6',NULL,'玩家2481',NULL,0.00,0.00,1,0,0,0,'2025-08-21 17:55:17','2025-08-21 17:52:25','ACTIVE'),(9,'device_5ac087e538da91b1','Google Pixel 6',NULL,'玩家6052',NULL,1392.00,1403.00,1,0,0,0,'2025-09-01 23:59:29','2025-08-21 17:55:47','ACTIVE'),(10,'test_device_001',NULL,NULL,'游戏高手',NULL,160.00,160.00,1,878,4,2580,NULL,'2025-08-22 12:05:17','ACTIVE'),(11,'test_device_002',NULL,NULL,'针法大师',NULL,160.00,160.00,1,809,4,2340,NULL,'2025-08-22 12:05:17','ACTIVE'),(12,'test_device_003',NULL,NULL,'插针王者',NULL,160.00,160.00,1,760,4,2100,NULL,'2025-08-22 12:05:17','ACTIVE'),(13,'test_device_004',NULL,NULL,'见缝达人',NULL,160.00,160.00,1,708,4,1980,NULL,'2025-08-22 12:05:17','ACTIVE'),(14,'test_device_005',NULL,NULL,'新手玩家',NULL,141.00,141.00,1,225,4,680,NULL,'2025-08-22 12:05:17','ACTIVE'),(15,'device_7c49b519428332c7','Vivo V2048A',NULL,'玩家9511',NULL,329100.00,198.00,1,0,0,0,'2025-09-16 20:56:22','2025-08-23 10:13:02','ACTIVE'),(16,'device_b6869b8d3dc97661','Vivo V2307A',NULL,'玩家7374',NULL,192.00,192.00,1,0,0,0,'2025-09-16 12:11:59','2025-08-23 10:20:54','ACTIVE'),(17,'test_device_1755915849017',NULL,NULL,'TestUser_675',NULL,100.00,100.00,1,0,0,0,NULL,'2025-08-23 10:24:09','ACTIVE'),(18,'test_device_1755919558263',NULL,NULL,'TestUser_278',NULL,100.00,100.00,1,0,0,0,NULL,'2025-08-23 11:25:01','ACTIVE'),(19,'test_device_simple','Test Device',NULL,'测试用户',NULL,100.00,100.00,1,0,0,0,'2025-09-01 23:13:28','2025-09-01 22:33:48','ACTIVE'),(20,'test_device_withdraw','Test Device',NULL,'测试用户',NULL,160.00,160.00,1,100,10,100,'2025-09-01 23:13:38','2025-09-01 22:33:53','ACTIVE'),(21,'test_device_ad','Test Device',NULL,'广告测试用户',NULL,100.00,100.00,1,0,0,0,'2025-09-01 23:13:38','2025-09-01 22:33:53','ACTIVE'),(22,'test_withdraw_simple_001','Test Device',NULL,'提现测试用户',NULL,100.00,100.00,1,0,0,0,'2025-09-01 23:25:48','2025-09-01 23:19:53','ACTIVE'),(23,'withdraw_test_final','Test Device',NULL,'提现测试用户Final',NULL,50.00,100.00,1,0,0,0,NULL,'2025-09-01 23:31:40','ACTIVE'),(24,'final_test_001','Test Device Final',NULL,'最终测试用户',NULL,100.00,100.00,1,0,0,0,NULL,'2025-09-01 23:57:44','ACTIVE'),(25,'coin_test_001','金币测试设备',NULL,'金币测试用户',NULL,110.00,110.00,1,50,1,500,NULL,'2025-09-02 00:03:24','ACTIVE'),(26,'rate_test_001','汇率测试设备',NULL,'汇率测试用户',NULL,100.00,100.00,1,0,0,0,NULL,'2025-09-02 00:15:51','ACTIVE'),(27,'android_withdraw_test','Android提现测试',NULL,'Android测试用户',NULL,89.00,100.00,1,0,0,0,NULL,'2025-09-02 00:22:15','ACTIVE'),(28,'final_android_test','最终Android测试',NULL,'最终测试用户',NULL,89.00,100.00,1,0,0,0,NULL,'2025-09-02 00:24:55','ACTIVE'),(29,'android_final_test','Android最终测试',NULL,'Android最终用户',NULL,89.00,100.00,1,0,0,0,NULL,'2025-09-02 00:30:58','ACTIVE'),(30,'withdraw_test_reject','拒绝测试设备',NULL,'拒绝测试用户',NULL,100.00,122.00,1,0,0,0,NULL,'2025-09-02 00:48:13','ACTIVE'),(31,'test_level_1','Level 1 Test Device',NULL,'用户evel_1',NULL,100.00,100.00,1,0,0,0,NULL,'2025-09-16 10:18:22','ACTIVE');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `withdraw_requests`
--

DROP TABLE IF EXISTS `withdraw_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `withdraw_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `amount` decimal(8,2) NOT NULL COMMENT '提现金额（人民币）',
  `coins_used` decimal(10,2) NOT NULL COMMENT '消耗金币数量',
  `alipay_account` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '支付宝账号',
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '真实姓名',
  `status` enum('PENDING','APPROVED','REJECTED','COMPLETED') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `admin_note` text COLLATE utf8mb4_unicode_ci COMMENT '管理员备注',
  `request_time` datetime DEFAULT NULL,
  `process_time` datetime DEFAULT NULL COMMENT '处理时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_status` (`user_id`,`status`),
  CONSTRAINT `withdraw_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `withdraw_requests`
--

LOCK TABLES `withdraw_requests` WRITE;
/*!40000 ALTER TABLE `withdraw_requests` DISABLE KEYS */;
INSERT INTO `withdraw_requests` (`id`, `user_id`, `amount`, `coins_used`, `alipay_account`, `real_name`, `status`, `admin_note`, `request_time`, `process_time`) VALUES (1,23,5.00,50.00,'test@example.com','测试用户','APPROVED','','2025-09-01 23:37:55','2025-09-02 00:59:33'),(2,27,1.00,11.00,'test@android.com','Android测试用户','APPROVED','测试批准 - 用户信息验证通过','2025-09-02 00:22:15','2025-09-02 00:48:14'),(3,9,1.00,11.00,'test@android.com','Android测试','REJECTED','支付宝账号信息不符，请重新提交','2025-09-02 00:24:08','2025-09-02 00:47:22'),(4,28,1.00,11.00,'android@test.com','Android用户','APPROVED','审核通过，用户信息真实','2025-09-02 00:24:55','2025-09-02 00:47:04'),(5,29,1.00,11.00,'android@final.com','Android最终用户','APPROVED',NULL,'2025-09-02 00:31:08','2025-09-02 00:34:47'),(6,30,2.00,22.00,'reject@test.com','拒绝测试','REJECTED','测试拒绝 - 支付宝账号格式不正确','2025-09-02 00:48:13','2025-09-02 00:48:14'),(7,15,30.00,108900.00,'13659008211','刘虹益','APPROVED','','2025-09-16 20:56:47','2025-09-16 20:57:36');
/*!40000 ALTER TABLE `withdraw_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'game_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-27 23:02:45
