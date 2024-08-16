# coding=utf-8
import typing, os, threading
from datetime import datetime
from qfluentwidgets import (RoundMenu, Action, StateToolTip)
from base import *
from canvas_item import *
from canvas_item.canvas_util import ZoomComponent
from canvas_editor import DrawActionEnum
from common import cfg, ScreenShotIcon
from ocr_service import *
from .painter_interface import PainterInterface
from pdf_viewer import *

class PinEditorWindow(PinWindow):
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent, screenPoint, physicalSize, physicalPixmap, closeCallback)
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.painterWidget = PainterInterface(self, physicalPixmap)
        self.contentLayout.addWidget(self.painterWidget)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

        self.painterWidget.initDrawLayer()
        self.painterWidget.drawWidget.setEditorEnabled(False)

        self.setShadowColor(cfg.get(cfg.windowShadowStyleFocusColor), cfg.get(cfg.windowShadowStyleUnFocusColor))

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
            Action(ScreenShotIcon.OCR, self.tr("OCR"), triggered=self.startOcr),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def defaultFlag(self) -> None:
        super().defaultFlag()
        self.roundRadius = cfg.get(cfg.windowShadowStyleRoundRadius)

    def showCommandBar(self):
        self.painterWidget.showCommandBar()

    def clickThrough(self):
        self.painterWidget.clickThrough()

    def initActions(self):
        actions = [
            QAction(self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            QAction(self, triggered=self.completeDraw, shortcut="ctrl+w"),
        ]
        self.addActions(actions)

        cfg.windowShadowStyleRoundRadius.valueChanged.connect(self.setRoundRadius)
        cfg.windowShadowStyleUnFocusColor.valueChanged.connect(self.refreshShadowColor)
        cfg.windowShadowStyleFocusColor.valueChanged.connect(self.refreshShadowColor)

    def refreshShadowColor(self, _):
        focusColor = cfg.get(cfg.windowShadowStyleFocusColor)
        unFocusColor = cfg.get(cfg.windowShadowStyleUnFocusColor)
        self.setShadowColor(focusColor, unFocusColor)

    def completeDraw(self):
        self.painterWidget.completeDraw()

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        finalValue = min(max(0.2, finalValue), 1)

        self.setWindowOpacity(finalValue)

    def startOcr(self):
        self.painterWidget.startOcr()

    def onBlinkStop(self):
        self.activateWindow()

    def copyToClipboard(self):
        # 因为Windows下剪贴板不支持透明度，其会将Image里的alpha值用255直接进行填充，相关讨论可以看下面这两个链接
        # https://stackoverflow.com/questions/44177115/copying-from-and-to-clipboard-loses-image-transparency/46424800#46424800
        # https://stackoverflow.com/questions/44287407/text-erased-from-screenshot-after-using-clipboard-getimage-on-windows-10/46400011#46400011

        if cfg.get(cfg.windowShadowStyleIsCopyWithShadow):
            finalPixmap = self.grabWithShaodw()
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
            if cfg.get(cfg.windowShadowStyleIsSaveWithShadow):
                finalPixmap = self.grabWithShaodw()
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
        cfg.windowShadowStyleRoundRadius.valueChanged.disconnect(self.setRoundRadius)
        cfg.windowShadowStyleUnFocusColor.valueChanged.disconnect(self.refreshShadowColor)
        cfg.windowShadowStyleFocusColor.valueChanged.disconnect(self.refreshShadowColor)
        super().closeEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            if self.painterWidget.tryQuitDraw():
                self.close()
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copyToClipboard()

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
            self.startOcr()

        super().keyPressEvent(event)

    def setMouseThroughState(self, isThrough: bool):
        self.painterWidget.completeDraw()
        self.painterWidget.clearFocus()
        self.focusOutEvent(QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.NoFocusReason))
        return super().setMouseThroughState(isThrough)