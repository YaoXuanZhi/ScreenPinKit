import os, glob, re
from base import *
from view import *
from misc import *

class PinWindowManager():
    def __init__(self):
        super().__init__()
        self.screenDevicePixelRatio = CanvasUtil.getDevicePixelRatio()
        self._windowsDict = {}

        startupImagePath, screenX, screenY = self.findScreenImagePath()
        if startupImagePath != None and os.path.exists(startupImagePath):
            imgpix = QPixmap(startupImagePath)
            realSize = self.autoFitScreenPixelRatioForPixmap(imgpix)
            self.addPinWindow(QPoint(screenX, screenY), realSize,  imgpix)

    def addPinWindow(self, screenPoint:QPoint, realSize:QSize, pixmap:QPixmap):
        hashCode = OsHelper.calculateHashForQPixmap(pixmap, 8)
        if not hashCode in self._windowsDict:
            self._windowsDict[hashCode] = PinEditorWindow(None, screenPoint, realSize, pixmap, lambda: self.handleWindowClose(hashCode))

    def showClipboard(self):
        '''将剪贴板上的图像数据作为冻结窗口'''
        clipboard = QApplication.clipboard()
        mimeData = clipboard.mimeData()
        if mimeData.hasImage():
            image = clipboard.image()
            pixmap = QPixmap.fromImage(image)
            realSize = self.autoFitScreenPixelRatioForPixmap(pixmap)
            screenPoint = QCursor().pos() - QPoint(realSize.width() / 2, realSize.height() / 2)
            self.addPinWindow(screenPoint, realSize, pixmap)

    def autoFitScreenPixelRatioForPixmap(self, pixmap:QPixmap) -> QSize:
        '''自动适配屏幕缩放比例'''
        screenDevicePixelRatio = CanvasUtil.getDevicePixelRatio()
        pixmap.setDevicePixelRatio(screenDevicePixelRatio)
        realSize = pixmap.size() / screenDevicePixelRatio
        return realSize

    def handleWindowClose(self, hashCode:str):
        widget:QWidget = self._windowsDict.pop(hashCode)
        widget.deleteLater()

    def switchMouseThroughState(self):
        '''鼠标穿透策略：优先判断获取焦点窗口的'''
        pinWnd:PinWindow = None
        screenPos = QCursor.pos()
        for wnd0 in self._windowsDict.items():
            wnd:PinWindow = wnd0
            if wnd != None and wnd.geometry().contains(screenPos):
                pinWnd = wnd
                break
        if pinWnd != None:
            pinWnd.switchMouseThroughState()
        else:
            for wnd in self._windowsDict.items():
                wnd:PinWindow = wnd0
                if wnd != None:
                    wnd.setMouseThroughState(False)

    def snip(self, screenPoint:QPoint, realSize:QSize, pixmap:QPixmap):
        self.clearScreenImages()
        saveFolder = cfg.get(cfg.cacheFolder)
        savePath = os.path.join(saveFolder, self.getScreenImageName(screenPoint))
        pixmap.save(savePath, 'png')
        self.addPinWindow(screenPoint, realSize, pixmap)

    def clearScreenImages(self):
        searchFolder = cfg.get(cfg.cacheFolder)
        searchPattern = '*.png'
        finalSearch = os.path.join(searchFolder, searchPattern)
        filePaths = glob.glob(finalSearch)
        for filePath in filePaths:
            matchResult = re.match(self.getImageNamePattern(), filePath)
            if matchResult != None and len(matchResult.groups()) > 0:
                os.remove(filePath)

    def getScreenImageName(self, screenPoint:QPoint):
        return f'screen {screenPoint.x()}-{screenPoint.y()}.png'

    def getImageNamePattern(self):
        return r'.*screen ([-]*\d+)-([-]*\d+).png'

    def findScreenImagePath(self):
        searchFolder = cfg.get(cfg.cacheFolder)
        searchPattern = '*.png'
        finalSearch = os.path.join(searchFolder, searchPattern)
        filePaths = glob.glob(finalSearch)
        if len(filePaths) > 0:
            # 遍历filePaths中的文件路径
            for filePath in filePaths:
                matchResult = re.match(self.getImageNamePattern(), filePath)

                if matchResult != None:
                    x = int(matchResult.group(1))
                    y = int(matchResult.group(2))
                    return filePath, x, y
        return None, 0, 0