# coding=utf-8
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import (RoundMenu, Action, FluentIcon, StateToolTip)
from canvas_item.canvas_util import ZoomComponent
from .painter_interface import PainterInterface
from canvas_item import *
from base import *
from common import cfg

class PinEditorWindow(PinWindow):
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent, screenPoint, physicalSize, physicalPixmap, closeCallback)
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

        self.painterWidget = PainterInterface(self, physicalPixmap)
        self.contentLayout.addWidget(self.painterWidget)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

        self.painterWidget.initDrawLayer()
        self.painterWidget.drawWidget.setEditorEnabled(False)

        self.initActions()

    def initActions(self):
        actions = [
            Action("复制贴图", self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            Action("保存贴图", self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            Action("开始OCR", self, triggered=self.startOcr, shortcut="ctrl+a"),
        ]
        self.addActions(actions)

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        finalValue = min(max(0.2, finalValue), 1)

        self.setWindowOpacity(finalValue)

    def startOcr(self):
        print("开始OCR")

    def copyToClipboard(self):
        # 因为Windows下剪贴板不支持透明度，其会将Image里的alpha值用255直接进行填充，相关讨论可以看下面这两个链接
        # https://stackoverflow.com/questions/44177115/copying-from-and-to-clipboard-loses-image-transparency/46424800#46424800
        # https://stackoverflow.com/questions/44287407/text-erased-from-screenshot-after-using-clipboard-getimage-on-windows-10/46400011#46400011

        # self.pixmapWidget.copyToClipboard()
        finalPixmap = self.grab()
        QApplication.clipboard().setPixmap(finalPixmap)

    def saveToDisk(self):
        # 获取当前时间，并格式化
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = f"Snipaste_{now_str}.png"

        tempFolder = cfg.get(cfg.tempFolder)
        finalFolder = "./"
        if os.path.exists(tempFolder):
            finalFolder = tempFolder
        finalPath = os.path.join(finalFolder, fileName)
        savePath, _ = QFileDialog.getSaveFileName(self, "Save File", finalPath, "PNG(*.png)")
        # 检查用户是否点击了“取消”
        if savePath != None:
            # 保存的截图无阴影
            # finalPixmap = self.pixmapWidget.getFinalPixmap()

            # 保存带阴影的截图
            finalPixmap = self.grab()
            finalPixmap.save(savePath, "png")

    def isAllowDrag(self):
        if self.painterWidget.drawWidget != None:
            return not self.painterWidget.drawWidget.isEditorEnabled()
        return True

    def isAllowModifyOpactity(self):
        return self.isAllowDrag()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isAllowDrag():
                self.close()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.isAllowModifyOpactity() and int(event.modifiers()) == Qt.ControlModifier:
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        else:
            return super().wheelEvent(event)

    def closeEvent(self, event) -> None:
        self.painterWidget.close()
        super().closeEvent(event)