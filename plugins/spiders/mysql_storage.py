import mysql.connector
from mysql.connector import Error
from config import settings

class MysqlStorage:
    name = "mysql_storage"
    description = "MySQL数据库存储插件"

    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB
            )
        except Error as e:
            raise Exception(f"连接MySQL失败: {str(e)}")

    def save(self, task_id, data, table_name='crawler_data', **kwargs):
        """保存数据到MySQL"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # 创建表（如果不存在）
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id VARCHAR(255) NOT NULL,
                url VARCHAR(2048) NOT NULL,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            
            # 插入数据
            insert_query = f"""
            INSERT INTO {table_name} (task_id, url, data)
            VALUES (%s, %s, %s)
            """
            
            # 假设data是一个字典，包含url和其他数据
            url = data.get('url', '')
            record = (task_id, url, data)
            cursor.execute(insert_query, record)
            
            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            raise Exception(f"保存数据到MySQL失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()