import importlib
import os
import logging
from importlib import util
from pathlib import Path
import pkgutil
from core.spider import Spider


class PluginManager:
    def __init__(self):
        # 确保 logger 最先初始化
        self.logger = logging.getLogger('plugin_manager')
        self.logger.info("初始化插件管理器")
        # 确保正确初始化spiders字典
        self.spiders = {}  # 添加这行
        self.load_plugins()

        
        
        self.load_plugins()
        self.logger.info(f"已加载爬虫: {list(self.spiders.keys())}")
        self.plugins = {
            'spiders': {},
            'processors': {},
            'storages': {},
            'verifications': {}
        }
        
    def load_plugins(self):
        """加载所有爬虫插件"""
        # 确保 logger 可用
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('plugin_manager_fallback')
        
        plugin_package = "plugins.spiders"
        
        # 确保插件目录存在
        plugin_path = plugin_package.replace(".", os.sep)
        if not os.path.exists(plugin_path):
            self.logger.warning(f"插件目录不存在: {plugin_path}")
            return
        
        # 动态导入所有插件模块
        try:
            self.logger.debug(f"尝试导入插件包: {plugin_package}")
            package = importlib.import_module(plugin_package)
        except ImportError as e:
            self.logger.error(f"导入插件包失败: {str(e)}")
            return
            
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                try:
                    full_module_name = f"{plugin_package}.{module_name}"
                    self.logger.debug(f"正在加载模块: {full_module_name}")
                    
                    module = importlib.import_module(full_module_name)
                    
                    # 注册所有继承自Spider的类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, Spider) and attr != Spider:
                            # 使用类名作为爬虫名称
                            spider_name = getattr(attr, 'name', None) or attr.__name__.lower()
                            self.spiders[spider_name] = attr
                            
                            self.logger.info(f"已注册爬虫: {spider_name}")
                except Exception as e:
                    self.logger.error(f"加载插件 {module_name} 失败: {str(e)}")
                    import traceback
                    self.logger.error(traceback.format_exc())
    
    def _load_plugins_by_type(self, plugin_path, plugin_type):
        """加载特定类型的插件"""
        if not plugin_path.exists():
            self.logger.warning(f"Plugin directory not found: {plugin_path}")
            return
            
        for filename in os.listdir(plugin_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                module_path = plugin_path / filename
                
                try:
                    # 动态导入模块
                    spec = util.spec_from_file_location(module_name, str(module_path))
                    if spec is None:
                        self.logger.error(f"Failed to load spec for {module_name}")
                        continue
                    
                    module = util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 查找插件类
                    loaded_plugin = False
                    for attr_name in dir(module):
                        if attr_name.startswith('__'):
                            continue
                            
                        attr = getattr(module, attr_name)
                        try:
                            # 检查是否是类且定义了 plugin_type
                            if (isinstance(attr, type) and 
                                hasattr(attr, 'plugin_type') and 
                                getattr(attr, 'plugin_type') == plugin_type):
                                
                                plugin_class = attr
                                plugin_name = plugin_class.__name__.lower()
                                
                                # 避免加载基类
                                if plugin_name == "basespiderplugin":
                                    self.logger.debug(f"Skipping base plugin: {plugin_name}")
                                    continue
                                
                                self.plugins[plugin_type + 's'][plugin_name] = plugin_class
                                self.logger.info(f"Loaded {plugin_type} plugin: {plugin_name}")
                                loaded_plugin = True
                                break
                        except TypeError:
                            # 跳过非类属性
                            continue
                    
                    if not loaded_plugin:
                        self.logger.warning(f"No valid plugin class found in {filename}")
                        
                except Exception as e:
                    self.logger.error(f"Error loading plugin {module_name}: {str(e)}")
    
    def get_spider(self, name):
        """获取指定名称的爬虫类"""
        if not name:
            return None
            
        # 尝试多种名称变体
        possible_names = [
            name.lower(),
            name.lower().replace("_", ""),
            name.lower().replace("spider", "")
        ]
        
        for n in possible_names:
            if n in self.spiders:
                return self.spiders[n]
        
        # 确保 logger 可用
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('plugin_manager_fallback')
            
        self.logger.warning(f"爬虫 '{name}' 未找到。可用爬虫: {list(self.spiders.keys())}")
        return None

    
    def list_spider_plugins(self):
        """列出所有可用的爬虫插件"""
        return list(self.plugins['spiders'].keys())
    
    # 添加其他类型插件的获取方法...