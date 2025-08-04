import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 日志配置
LOG_CONFIG = {
    'level': 'DEBUG',  # 改为DEBUG获取更详细日志
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(BASE_DIR, 'logs', 'crawlerx.log')
}

# 插件路径 - 确保路径正确
PLUGINS_DIR = os.path.join(BASE_DIR, 'plugins')

# 用户代理池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

# 请求设置
REQUEST_TIMEOUT = 30
RETRY_TIMES = 3

# 确保日志目录存在
LOG_DIR = os.path.dirname(LOG_CONFIG['file'])
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    print(f"创建日志目录: {LOG_DIR}")

# 确保插件目录存在
if not os.path.exists(PLUGINS_DIR):
    os.makedirs(PLUGINS_DIR)
    print(f"创建插件目录: {PLUGINS_DIR}")
    
    # 创建必要的子目录
    for subdir in ['spiders', 'processors', 'storages']:
        os.makedirs(os.path.join(PLUGINS_DIR, subdir))
        print(f"创建插件子目录: {subdir}")

# 确保数据目录存在
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"创建数据目录: {DATA_DIR}")