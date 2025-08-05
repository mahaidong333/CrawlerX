class BasePlugin:
    """所有插件必须继承的基类"""
    plugin_type = ""
    plugin_name = ""

    def __init__(self, *args, **kwargs):
        """支持任意参数的初始化方法"""
        self.config = kwargs.get('config', {})

    @classmethod
    def register(cls, name, plugin_type):
        """更安全的插件注册方法"""
        cls.plugin_name = name
        cls.plugin_type = plugin_type
        return cls