import os, sys
import importlib
from .plugin_interface import PluginInterface

class PluginManager:
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
        self.plugins = []

    def loadPlugins(self):
        sys.path.append(self.plugin_dir)
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py'):
                module_name = filename[:-3]
                module_path = f"{module_name}"
                module = importlib.import_module(module_path)
                
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                        self.plugins.append(attr())

    def executeAllPlugins(self):
        for plugin0 in self.plugins:
            plugin:PluginInterface = plugin0
            plugin.execute()