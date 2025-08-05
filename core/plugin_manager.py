import importlib
import logging
import os
import sys
import inspect
from pathlib import Path
from .base_plugin import BasePlugin


class PluginManager:
    def __init__(self):
        self.plugins = {'spiders': {}, 'processors': {}, 'storages': {}, 'verifications': {}}
        self.logger = logging.getLogger('plugin_manager')

        # 将项目根目录添加到系统路径
        project_root = Path(__file__).resolve().parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

    def load_plugins(self):
        """加载所有插件"""
        project_root = Path(__file__).resolve().parent.parent
        plugins_dir = project_root / "plugins"
        self.logger.info(f"扫描插件目录: {plugins_dir}")

        # 只处理有效插件类型
        valid_types = ['spiders', 'processors', 'storages', 'verifications']

        for plugin_type in os.listdir(plugins_dir):
            if plugin_type not in valid_types:
                continue

            type_dir = plugins_dir / plugin_type
            if not type_dir.is_dir():
                continue

            self.logger.debug(f"处理插件类型: {plugin_type}")
            for file in os.listdir(type_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    module_name = file[:-3]
                    try:
                        # 使用绝对导入路径
                        module_path = f"plugins.{plugin_type}.{module_name}"
                        self.logger.debug(f"导入模块: {module_path}")
                        module = importlib.import_module(module_path)

                        # 查找所有BasePlugin的子类
                        for name, obj in inspect.getmembers(module):
                            # 确保是类且不是BasePlugin本身
                            if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                                plugin_name = getattr(obj, 'plugin_name', name)
                                self.plugins[plugin_type][plugin_name] = obj
                                self.logger.info(f"注册插件: {plugin_type}/{plugin_name}")

                    except Exception as e:
                        self.logger.error(f"加载插件失败 {plugin_type}.{module_name}: {str(e)}", exc_info=True)

    def get_spider(self, name):
        return self.plugins['spiders'].get(name)

    def get_processor(self, name):
        return self.plugins['processors'].get(name)

    def get_storage(self, name):
        return self.plugins['storages'].get(name)

    def get_verification(self, name):
        return self.plugins['verifications'].get(name)





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