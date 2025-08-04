class BaseSpiderPlugin:
    plugin_type = "spider"  # 标识插件类型
    
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def setup(self):
        """初始化爬虫"""
        pass
        
    def crawl(self, url):
        """执行爬取操作"""
        raise NotImplementedError("crawl method must be implemented")
        
    def teardown(self):
        """清理资源"""
        pass