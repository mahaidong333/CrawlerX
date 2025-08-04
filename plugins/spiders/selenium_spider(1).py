from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from datetime import datetime

class SeleniumSpider:
    plugin_type = "spider"
    
    def __init__(self):
        self.logger = logging.getLogger("SeleniumSpider")
        self.driver = None
    
    def setup(self, config=None):
        """初始化爬虫"""
        self.logger.info("Selenium爬虫初始化")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 从配置获取选项
        if config:
            for arg in config.get("chrome_args", []):
                chrome_options.add_argument(arg)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(
                service=service, 
                options=chrome_options
            )
            self.driver.set_page_load_timeout(30)
            self.logger.info("Selenium驱动已初始化")
        except Exception as e:
            self.logger.error(f"初始化Selenium驱动失败: {str(e)}")
            raise
    
    def crawl(self, url):
        """执行爬取操作"""
        if not self.driver:
            raise RuntimeError("Selenium驱动未初始化")
        
        try:
            # 访问页面
            self.driver.get(url)
            time.sleep(2)  # 等待页面渲染
            
            # 获取页面信息
            title = self.driver.title
            current_url = self.driver.current_url
            
            # 提取所有链接
            links = []
            for link in self.driver.find_elements(By.TAG_NAME, 'a'):
                href = link.get_attribute('href')
                if href and href.startswith(('http://', 'https://')):
                    links.append({
                        "url": href,
                        "text": link.text.strip()
                    })
            
            # 提取正文文本（简化版）
            body = self.driver.find_element(By.TAG_NAME, 'body')
            content = body.text.strip()[:1000]  # 只取前1000字符
            
            return {
                "status": "success",
                "url": current_url,
                "title": title,
                "content": content,
                "links": links,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Selenium爬取失败: {url} - {str(e)}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def teardown(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium驱动已关闭")
            except Exception as e:
                self.logger.error(f"关闭Selenium驱动失败: {str(e)}")