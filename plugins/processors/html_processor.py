from bs4 import BeautifulSoup
from utils.logger import setup_logger

logger = setup_logger('html_processor')

class HtmlProcessor:
    name = "html_processor"
    description = "HTML内容处理器，使用BeautifulSoup解析HTML内容"

    def process(self, html_content, extraction_rules):
        """处理HTML响应并提取数据"""
        try:
            if not extraction_rules:
                logger.warning("没有提供提取规则，返回原始HTML")
                return {"raw_html": html_content}
                
            soup = BeautifulSoup(html_content, 'html.parser')
            results = {}
            
            # 应用提取规则
            for key, rule in extraction_rules.items():
                selector = rule.get('selector')
                attr = rule.get('attr', 'text')
                multiple = rule.get('multiple', False)
                
                if not selector:
                    logger.warning(f"规则 {key} 缺少选择器")
                    continue
                
                try:
                    if multiple:
                        elements = soup.select(selector)
                        values = [self._extract_value(el, attr) for el in elements]
                        results[key] = values
                    else:
                        element = soup.select_one(selector)
                        results[key] = self._extract_value(element, attr) if element else None
                except Exception as e:
                    logger.error(f"处理规则 {key} 时出错: {str(e)}")
                    results[key] = None
            
            return results
        except Exception as e:
            logger.error(f"HTML处理失败: {str(e)}")
            return {"error": str(e)}

    def _extract_value(self, element, attr):
        """从元素中提取值"""
        if not attr or attr == 'text':
            return element.get_text(strip=True)
        elif attr == 'html':
            return str(element)
        elif attr == 'outer_html':
            return str(element)
        else:
            return element.get(attr, '')