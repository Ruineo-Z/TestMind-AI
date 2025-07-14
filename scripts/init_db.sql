-- TestMind AI - 数据库初始化脚本
-- 创建开发和测试数据库

-- 创建开发数据库
CREATE DATABASE testmind_dev;

-- 创建测试数据库  
CREATE DATABASE testmind_test;

-- 授权用户访问所有数据库
GRANT ALL PRIVILEGES ON DATABASE testmind TO testmind;
GRANT ALL PRIVILEGES ON DATABASE testmind_dev TO testmind;
GRANT ALL PRIVILEGES ON DATABASE testmind_test TO testmind;
