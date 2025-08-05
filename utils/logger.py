import logging
import os
from config import settings
from logging.handlers import RotatingFileHandler


def setup_logging():
    """配置项目日志系统"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 主日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # 控制台输出
            RotatingFileHandler(
                os.path.join(log_dir, 'crawlerx.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )

    # 设置特定模块的日志级别
    logging.getLogger('plugin_manager').setLevel(logging.DEBUG)
    logging.getLogger('engine').setLevel(logging.DEBUG)


def setup_logger(name):

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('crawlerx.log')
        ]
    )

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