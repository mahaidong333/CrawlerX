import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.logger import setup_logger
import random
from config import settings

logger = setup_logger('requests_spider')

class RequestsSpider:
    """高级请求爬虫插件，支持重试和更多配置选项"""
    name = "requests_spider"
    description = "基于Requests库的高级爬虫插件，支持重试机制"

    def __init__(self):
        self.session = requests.Session()
        # 配置重试策略
        retry_strategy = Retry(
            total=settings.RETRY_TIMES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def crawl(self, url, method='GET', headers=None, params=None, 
             data=None, json=None, auth=None, cookies=None, 
             timeout=None, **kwargs):
        """执行爬取操作"""
        try:
            # 设置默认超时
            if timeout is None:
                timeout = settings.REQUEST_TIMEOUT
                
            # 设置随机User-Agent
            if headers is None:
                headers = {}
            if 'User-Agent' not in headers:
                headers['User-Agent'] = random.choice(settings.USER_AGENTS)
                
            logger.info(f"开始爬取: {url} [{method}]")
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                auth=auth,
                cookies=cookies,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()
            logger.info(f"成功爬取 {url} - 状态码: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Requests爬取失败: {str(e)}")
            raise Exception(f"Requests爬取失败: {str(e)}")