CREATE DATABASE crawlerx_db;
CREATE USER 'crawlerx'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON crawlerx_db.* TO 'crawlerx'@'localhost';
FLUSH PRIVILEGES;