# coding=utf-8
from datetime import datetime
from qfluentwidgets import (RoundMenu, Action)
from base import *
from canvas_item import *
from canvas_item.canvas_util import ZoomComponent
from canvas_editor import DrawActionEnum
from common import cfg, ScreenShotIcon
from .painter_interface import PainterInterface

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

        self.setRoundStyle(cfg.get(cfg.useRoundStyle))
        self.setShadowColor(cfg.get(cfg.focusShadowColor), cfg.get(cfg.unFocusShadowColor))

        self.initActions()

    def contextMenuEvent(self, event:QContextMenuEvent):
        if self.painterWidget.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(ScreenShotIcon.WHITE_BOARD, self.tr("Show toolbar"), triggered=self.showCommandBar),
            Action(ScreenShotIcon.COPY, self.tr("Copy"), triggered=self.copyToClipboard),
            Action(ScreenShotIcon.SAVE_AS, self.tr("Save as"), triggered=self.saveToDisk),
            Action(ScreenShotIcon.CLICK_THROUGH, self.tr("Mouse through"), triggered=self.clickThrough),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def showCommandBar(self):
        self.painterWidget.showCommandBar()

    def clickThrough(self):
        self.painterWidget.clickThrough()

    def initActions(self):
        actions = [
            Action(self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            Action(self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            Action(self, triggered=self.startOcr, shortcut="ctrl+a"),
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

        if cfg.get(cfg.isCopyWithShadow):
            finalPixmap = self.grab()
        else:
            finalPixmap = self.painterWidget.getFinalPixmap()
        QApplication.clipboard().setPixmap(finalPixmap)

    def saveToDisk(self):
        # 获取当前时间，并格式化
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = cfg.get(cfg.imageNameFormat) % (now_str)

        tempFolder = cfg.get(cfg.cacheFolder)
        finalFolder = "./"
        if os.path.exists(tempFolder):
            finalFolder = tempFolder
        finalPath = os.path.join(finalFolder, fileName)
        savePath, _ = QFileDialog.getSaveFileName(self, "Save File", finalPath, "PNG(*.png)")
        if savePath != None:
            if cfg.get(cfg.isSaveWithShadow):
                finalPixmap = self.grab()
            else:
                finalPixmap = self.painterWidget.getFinalPixmap()
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

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            if self.painterWidget.tryQuitDraw():
                self.close()
        super().keyPressEvent(event)