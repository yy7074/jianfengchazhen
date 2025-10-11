-- 修改等级配置表的金币倍数字段，允许更大的值
-- 从 DECIMAL(3,2) 改为 DECIMAL(10,2)
-- 这样可以支持从 0.01 到 99999999.99 的倍数

USE game_db;

-- 修改广告金币倍数字段
ALTER TABLE user_level_configs 
MODIFY COLUMN ad_coin_multiplier DECIMAL(10, 2) DEFAULT 1.00 COMMENT '广告金币倍数';

-- 修改游戏金币倍数字段
ALTER TABLE user_level_configs 
MODIFY COLUMN game_coin_multiplier DECIMAL(10, 2) DEFAULT 1.00 COMMENT '游戏金币倍数';

-- 验证修改
DESCRIBE user_level_configs;

