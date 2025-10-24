-- 检查今日统计数据
SELECT '当前日期' as info, CURDATE() as value;

SELECT '今日广告观看记录' as info, 
       COUNT(*) as count, 
       SUM(reward_coins) as total_coins
FROM ad_watch_records 
WHERE DATE(watch_time) = CURDATE();

SELECT '今日金币交易记录' as info,
       COUNT(*) as count,
       SUM(amount) as total_amount
FROM coin_transactions 
WHERE amount > 0 AND DATE(created_time) = CURDATE();

-- 查看最近的广告记录
SELECT '最近10条广告记录' as info;
SELECT watch_time, reward_coins, user_id, 
       DATE(watch_time) = CURDATE() as is_today
FROM ad_watch_records 
ORDER BY watch_time DESC 
LIMIT 10;

-- 查看各日期的广告统计
SELECT '最近7天广告统计' as info;
SELECT DATE(watch_time) as date,
       COUNT(*) as count,
       SUM(reward_coins) as coins
FROM ad_watch_records
GROUP BY DATE(watch_time)
ORDER BY date DESC
LIMIT 7;

-- 查看各日期的金币统计
SELECT '最近7天金币统计' as info;
SELECT DATE(created_time) as date,
       COUNT(*) as count,
       SUM(amount) as total,
       type
FROM coin_transactions
WHERE amount > 0
GROUP BY DATE(created_time), type
ORDER BY date DESC, type
LIMIT 20;

