import os, sys, glob, importlib
from .ocr_loader_interface import OcrLoaderInterface
from common import *
from canvas_item import *
# 该模块的引用会传递到loader实现上
from misc import *

class CustomLoader(importlib.abc.Loader):
    def __init__(self, module_code):
        self.module_code = module_code

    def exec_module(self, module):
        exec(self.module_code, module.__dict__)

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

    def initLoaders(self):
        self.__initLoadersInside()
        self.__initLoadersOutside()

    def __initLoadersInside(self):
        import cv2
        import onnxruntime
        import pyclipper
        from shapely.geometry import Polygon
        # 打包指令：pyinstaller --onefile --icon=../images/logo.png --add-data "internal_plugins/*.py;internal_plugins" --add-data "internal_ocr_loaders/*.py;internal_ocr_loaders" --add-data "internal_ocr_loaders/PaddleOCRModel;internal_ocr_loaders/PaddleOCRModel" --windowed main.py -n ScreenPinKit
        self.__initLoadersByModuleName("internal_ocr_loader_return_text")
        self.__initLoadersByModuleName("internal_ocr_loader_return_text_plus")
        self.__initLoadersByModuleName("internal_ocr_loader_return_json")

    def __initLoadersOutside(self):
        plugin_dir = cfg.get(cfg.ocrLoaderFolder)
        self.__initLoadersByFolder(plugin_dir)

    def __initLoadersByText(self, moduleName, text):
        loader = CustomLoader(text)
        spec = importlib.util.spec_from_loader(moduleName, loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.__filterInterface(module)

    def __initLoadersByFilePath(self, moduleName, filePath):
        file = QFile(filePath)
        # 打开文件，只读模式
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            # 创建 QTextStream 对象
            stream = QTextStream(file)
            stream.setCodec("utf-8")

            # 读取文件内容
            text = stream.readAll()
            self.__initLoadersByText(moduleName, text)

    # def __initLoadersByFilePathBak(self, moduleName, filePath):
    #     '''该方法不支持从qt资源文件里读取，因此弃用'''
    #     spec = importlib.util.spec_from_file_location(moduleName, filePath)
    #     module = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(module)
    #     self.__filterInterface(module)

    def __initLoadersByFolder(self, folderPath):
        sys.path.append(folderPath)
        pyFiles = glob.glob(f"{folderPath}/*.py", recursive=False)
        for filePath in pyFiles:
            filename = os.path.basename(filePath)
            module_name = filename[:-3]
            module_path = f"{module_name}"
            try:
                module = importlib.import_module(module_path)
                self.__filterInterface(module)
            except Exception:
                pass

    def __initLoadersByModuleName(self, moduleName):
        module = importlib.import_module(moduleName)
        self.__filterInterface(module)

    def __filterInterface(self, module):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, OcrLoaderInterface) and attr != OcrLoaderInterface:
                loaderInst = attr()
                if loaderInst.name in self.loaderDict:
                    continue
                self.loaderDict[loaderInst.name] = loaderInst

ocrLoaderMgr = OcrLoaderManager()