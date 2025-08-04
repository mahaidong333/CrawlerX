# plugins/spiders/playwright_spider.py

# 要添加新的爬虫插件，只需在 plugins/spiders/ 目录下创建新文件
# 系统会自动检测并加载新插件，无需重启核心引擎。

from playwright.sync_api import sync_playwright
from utils.logger import setup_logger

logger = setup_logger('playwright_spider')

class PlaywrightSpider:
    name = "playwright_spider"
    description = "基于Playwright的爬虫插件，支持现代Web应用"

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        
    def crawl(self, url, actions=None, wait_for=None, timeout=30000):
        context = self.browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url, timeout=timeout)
            
            if wait_for:
                page.wait_for_selector(wait_for, timeout=timeout)
                
            if actions:
                for action in actions:
                    self._execute_action(page, action)
            
            content = page.content()
            return content
        except Exception as e:
            logger.error(f"Playwright爬取失败: {str(e)}")
            return None
        finally:
            page.close()
            context.close()
            
    def _execute_action(self, page, action):
        action_type = action.get('type')
        selector = action.get('selector')
        value = action.get('value')
        
        if action_type == 'click':
            page.click(selector)
        elif action_type == 'fill':
            page.fill(selector, value)
        elif action_type == 'scroll':
            if value == 'bottom':
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif value == 'top':
                page.evaluate("window.scrollTo(0, 0)")
        elif action_type == 'wait':
            page.wait_for_timeout(value * 1000)
