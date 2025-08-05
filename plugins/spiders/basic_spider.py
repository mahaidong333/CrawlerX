from core.base_plugin import BasePlugin


class BasicSpider(BasePlugin):
    plugin_name = "basic"

    def __init__(self, config=None):
        super().__init__(config)

    def run(self):
        return {"status": "success", "data": []}

    
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