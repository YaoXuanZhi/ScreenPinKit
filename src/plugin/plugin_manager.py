import os, sys
import importlib
from .plugin_interface import PluginInterface, GlobalEventEnum
from common import *

class PluginManager:
    def __init__(self, plugin_dir):
        # self.plugin_dir = plugin_dir
        self.plugin_dir = "../plugins_demos"
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
                        pluginInst = attr()
                        self.plugins.append(pluginInst)
                        pluginInst.onLoaded()

    def handleEvent(self, eventName: GlobalEventEnum, *args, **kwargs):
        for plugin0 in self.plugins:
            plugin:PluginInterface = plugin0
            plugin.handleEvent(eventName, *args, **kwargs)

pluginMgr = PluginManager(cfg.get(cfg.pluginsFolder))