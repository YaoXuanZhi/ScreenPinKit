import importlib.util
import os, sys, glob, re
import importlib
from .plugin_interface import PluginInterface, GlobalEventEnum
from .plugin_config import *
from common import *
from misc import *

class CustomLoader(importlib.abc.Loader):
    def __init__(self, module_code):
        self.module_code = module_code

    def exec_module(self, module):
        exec(self.module_code, module.__dict__)


class PluginManager:
    def __init__(self):
        self.pluginDict = {}
        pluginCfg.load("plugin_settings.json")

    def loadPlugins(self):
        self.__loadPluginsInside()
        self.__loadPluginsOutside()

    def __loadPluginsInside(self):
        internalPath = os.path.join(OsHelper.getInternalPath(), "internal_deps/internal_plugins")
        self.__loadPluginsByFolder(internalPath)

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
        '''遍历指定路径下所有包含PluginInterface的py文件，并作为插件导入'''
        for root, dirs, files in os.walk(folderPath):
            isAppendSysPath = False
        
            # 打印当前目录中的文件
            for fileName in files:
                if fileName.endswith(".py"):
                    maybePath = os.path.join(root, fileName)
                    # 检查文件内是否包含PluginInterface的子类
                    with open(maybePath, "r", encoding="utf-8") as f:
                        text = f.read()
                        isMatch = re.search(r"class.*PluginInterface", text)
                        if isMatch:
                            if not isAppendSysPath:
                                # 添加到sys.path中，以便导入模块
                                isAppendSysPath = True
                                sys.path.append(root)

                            moduleName = fileName[:-3]
                            try:
                                module = importlib.import_module(moduleName)
                                self.__filterInterface(module)
                            except Exception as e:
                                print("\n".join(e.args))

    def __loadPluginByModuleName(self, moduleName):
        module = importlib.import_module(moduleName)
        self.__filterInterface(module)

    def __filterInterface(self, module):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginInterface)
                and attr != PluginInterface
            ):
                pluginInst = attr()
                if pluginInst.name in self.pluginDict:
                    continue

                pluginInst.enable = pluginCfg.isOnByPluginName(pluginInst.name)
                self.pluginDict[pluginInst.name] = pluginInst
                if pluginInst.enable:
                    pluginInst.onLoaded()

    def handleEvent(self, eventName: GlobalEventEnum, *args, **kwargs):
        for plugin0 in self.pluginDict.values():
            plugin: PluginInterface = plugin0
            if plugin.enable:
                plugin.handleEvent(eventName, *args, **kwargs)

    def removePlugin(self, pluginName: str):
        # removedPlugin = self.plugins.pop(pluginName)
        pass

pluginMgr = PluginManager()
