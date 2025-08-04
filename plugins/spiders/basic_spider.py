import requests
from bs4 import BeautifulSoup
import logging
from core.spider import Spider

class BasicSpider:
    plugin_type = "spider"
    name = "basic"  # 确保有这个属性
    def __init__(self):
        super().__init__(config)
        self.logger = logging.getLogger("BasicSpider")
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }


    def run(self):
        """基础爬虫实现"""
        print(f"基础爬虫开始运行: {self.config['url']}")
        
        try:
            # 添加超时设置和异常处理
            response = requests.get(
                self.config['url'],
                headers=self.config.get('headers', {}),
                timeout=10
            )
            response.raise_for_status()
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 提取所有链接
            for link in soup.find_all('a', href=True):
                results.append({
                    "url": link['href'],
                    "text": link.get_text(strip=True)
                })
            
            # 保存结果并返回计数
            return self.save_results(results)
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
            return self.save_results(0)
        except Exception as e:
            print(f"解析失败: {str(e)}")
            return self.save_results(0)

    
    def setup(self, config=None):
        """初始化爬虫"""
        self.logger.info("基础爬虫初始化")
        if config:
            self.headers.update(config.get("headers", {}))
    
    def crawl(self, url):
        """执行爬取操作"""
        try:
            # 发送请求
            response = self.session.get(
                url, 
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            # 解析内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取数据
            title = soup.title.string.strip() if soup.title else "无标题"
            
            # 提取所有链接
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if href and href.startswith(('http://', 'https://')):
                    links.append({
                        "url": href,
                        "text": link.get_text(strip=True)
                    })
            
            # 提取正文文本（简化版）
            content = ""
            for p in soup.find_all('p'):
                content += p.get_text(strip=True) + "\n"
            content = content.strip()
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "content": content[:500] + "..." if len(content) > 500 else content,
                "links": links,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"爬取失败: {url} - {str(e)}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def teardown(self):
        """清理资源"""
        self.logger.info("基础爬虫清理资源")
        self.session.close()