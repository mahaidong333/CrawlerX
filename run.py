import logging
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 记录启动信息
logger = logging.getLogger('main')
logger.info("Starting CrawlerX...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

# 打印项目目录结构
logger.debug("项目目录结构:")
for root, dirs, files in os.walk('.'):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 4 * level
    logger.debug(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 4 * (level + 1)
    for f in files:
        logger.debug(f"{subindent}{f}")

from core.engine import CrawlerEngine
from web.app import app, initialize_web  # 导入重命名后的函数

def main():
   
    # 导入引擎并记录插件信息
    from core.engine import CrawlerEngine
    engine = CrawlerEngine()
    logger.info(f"Engine instance created: {id(engine)}")
    
    # 创建引擎实例
    engine = CrawlerEngine()
    logger.info(f"Engine instance created: {id(engine)}")
    
    # 初始化 Web 界面并传递引擎实例
    logger.info("Initializing web interface...")
    initialize_web(engine)  # 使用重命名后的函数
    
    # 列出所有可用的爬虫插件
    try:
        spider_plugins = engine.plugin_manager.list_spider_plugins()
        logger.info(f"Available spider plugins: {', '.join(spider_plugins)}")
    except Exception as e:
        logger.error(f"Error listing spider plugins: {str(e)}")
    
    # 启动 Web 服务器
    logger.info("Starting web server at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    main()