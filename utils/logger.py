import logging
import os
from config import settings

def setup_logger(name):
    """配置并返回一个日志记录器"""
    # 创建日志目录
    log_dir = os.path.dirname(settings.LOG_CONFIG['file'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_CONFIG['level'])
    
    # 创建文件处理器
    file_handler = logging.FileHandler(settings.LOG_CONFIG['file'])
    file_handler.setLevel(settings.LOG_CONFIG['level'])
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOG_CONFIG['level'])
    
    # 创建格式化器
    formatter = logging.Formatter(settings.LOG_CONFIG['format'])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger