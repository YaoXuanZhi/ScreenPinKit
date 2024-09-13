import os, sys, glob, importlib
from enum import Enum
from .ocr_loader_interface import OcrLoaderInterface
from common import *

class OcrThread(QThread):
    ocrStartSignal = pyqtSignal()
    ocrEndSignal = pyqtSignal(list, list, list)
    def __init__(self, action:QAction, pixmap:QPixmap) -> None:
        super().__init__()
        self.action = action
        self.pixmap = pixmap
        
    def run(self):
        self.action(self.pixmap)

class OcrLoaderManager:
    def __init__(self):
        self.loaderDict = {}
        self.workDir = os.path.dirname(__file__)

    def initLoaders(self):
        self.__initLoadersInside()
        self.__initLoadersOutside()

        folderPath = os.path.join(self.workDir, "outside_ocr_loaders")
        self.__initLoadersByFolder(folderPath)

    def __initLoadersInside(self):
        folderPath = os.path.dirname(__file__)
        folderPath = os.path.join(self.workDir, "internal_ocr_loaders")
        self.__initLoadersByFolder(folderPath)

    def __initLoadersOutside(self):
        plugin_dir = cfg.get(cfg.pluginsFolder)
        self.__initLoadersByFolder(plugin_dir)

    def __initLoadersByFolder(self, folderPath):
        sys.path.append(folderPath)
        pyFiles = glob.glob(f"{folderPath}/*.py", recursive=False)
        for filePath in pyFiles:
            filename = os.path.basename(filePath)
            module_name = filename[:-3]
            module_path = f"{module_name}"
            module = importlib.import_module(module_path)
                
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, OcrLoaderInterface) and attr != OcrLoaderInterface:
                    loaderInst = attr()
                    if loaderInst.name in self.loaderDict:
                        continue
                    self.loaderDict[loaderInst.name] = loaderInst

ocrLoaderMgr = OcrLoaderManager()