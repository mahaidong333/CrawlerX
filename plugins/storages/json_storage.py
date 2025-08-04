import json
import os
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger('json_storage')

class JsonStorage:
    name = "json_storage"
    description = "JSON文件存储插件"

    def __init__(self):
        self.output_dir = 'data'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建数据存储目录: {self.output_dir}")

    def save(self, task_id, data, filename=None, **kwargs):
        """保存数据到JSON文件"""
        try:
            # 生成文件名
            if not filename:
                filename = f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            file_path = os.path.join(self.output_dir, filename)
            
            # 写入数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存数据到JSON失败: {str(e)}")
            raise Exception(f"保存数据到JSON失败: {str(e)}")