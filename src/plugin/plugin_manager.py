import os, sys, glob
import importlib
from .plugin_interface import PluginInterface, GlobalEventEnum
from common import *

class PluginManager:
    def __init__(self):
        self.plugins = []

    def loadPlugins(self):
        self.__loadPluginsInside()
        self.__loadPluginsOutside()

    def __loadPluginsInside(self):
        folderPath = os.path.dirname(__file__)
        folderPath = os.path.join(folderPath, "internal_plugins")
        sys.path.append(folderPath)
        self.__loadPluginsByFolder(folderPath)

    def __loadPluginsOutside(self):
        folderPath = cfg.get(cfg.pluginsFolder)
        self.__loadPluginsByFolder(folderPath)

    def __loadPluginsByFolder(self, folderPath):
        sys.path.append(folderPath)
        pyFiles = glob.glob(f"{folderPath}/*.py", recursive=False)
        for filePath in pyFiles:
            filename = os.path.basename(filePath)
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

pluginMgr = PluginManager()