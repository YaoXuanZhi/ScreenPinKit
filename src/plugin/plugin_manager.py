import importlib.util
import os, sys, glob
import importlib
from .plugin_interface import PluginInterface, GlobalEventEnum
from common import *

class CustomLoader(importlib.abc.Loader):
    def __init__(self, module_code):
        self.module_code = module_code

    def exec_module(self, module):
        exec(self.module_code, module.__dict__)

class PluginManager:
    def __init__(self):
        self.plugins = []

    def loadPlugins(self):
        self.__loadPluginsInside()
        self.__loadPluginsOutside()

    def __loadPluginsInside(self):
        folderPath = os.getcwd()
        folderPath = os.path.join(folderPath, "internal_plugins")
        sys.path.append(folderPath)
        self.__loadPluginsByFolder(folderPath)
        # if os.environ.get("debug"):
        #     folderPath = os.getcwd()
        #     folderPath = os.path.join(folderPath, "internal_plugins")
        #     sys.path.append(folderPath)
        #     self.__loadPluginsByFolder(folderPath)
        # else:
        #     self.__loadPluginsByFilePath("ocr_progress_display", ":/InternalData/resource/internal_plugins/ocr_progress_display.py")

    def __loadPluginsOutside(self):
        folderPath = cfg.get(cfg.pluginsFolder)
        self.__loadPluginsByFolder(folderPath)

    def __loadPluginsByText(self, moduleName, text):
        loader = CustomLoader(text)
        spec = importlib.util.spec_from_loader(moduleName, loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.__filterInterface(module)

    def __loadPluginsByFilePath(self, moduleName, filePath):
        file = QFile(filePath)
        # 打开文件，只读模式
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            # 创建 QTextStream 对象
            stream = QTextStream(file)
            stream.setCodec("utf-8")

            # 读取文件内容
            text = stream.readAll()
            self.__loadPluginsByText(moduleName, text)

    # def __loadPluginsByFilePathBak(self, moduleName, filePath):
    #     '''该方法不支持从qt资源文件里读取，因此弃用'''
    #     spec = importlib.util.spec_from_file_location(moduleName, filePath)
    #     module = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(module)
    #     self.__filterInterface(module)

    def __loadPluginsByFolder(self, folderPath):
        sys.path.append(folderPath)
        pyFiles = glob.glob(f"{folderPath}/*.py", recursive=False)
        for filePath in pyFiles:
            filename = os.path.basename(filePath)
            module_name = filename[:-3]
            module_path = f"{module_name}"
            module = importlib.import_module(module_path)
            self.__filterInterface(module)

    def __filterInterface(self, module):
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