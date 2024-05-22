# coding=utf-8
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import (RoundMenu, Action, FluentIcon, TeachingTipTailPosition)
from icon import ScreenShotIcon
from painter_tools import QPainterWidget, DrawActionEnum, QMouseThroughWindow
from canvas_item import *
from extend_widgets import *

class QScreenPainterWidget(QPainterWidget):
    completeDrawAfterSignal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent, None, 0, 0)

    def getCommandBarPosition(self) -> BubbleTipTailPosition:
        return BubbleTipTailPosition.TOP_CENTER

    def contextMenuEvent(self, event:QtGui.QContextMenuEvent):
        return

    def completeDraw(self):
        super().completeDraw()
        self.completeDrawAfterSignal.emit()

    def keyPressEvent(self, event) -> None:
        # 监听ESC键，当按下ESC键时，逐步取消编辑状态
        if event.key() == Qt.Key_Escape:
            # 如果当前绘图工具不在绘制状态，则本次按下Esc键会关掉绘图工具条
            if self.currentDrawActionEnum != DrawActionEnum.SelectItem:
                self.selectItemAction.setChecked(True)
                self.selectItemAction.triggered.emit()
            elif self.toolbar != None and self.toolbar.isVisible():
                self.completeDraw()

class ScreenPaintWindow(QMouseThroughWindow):  # 屏幕窗口
    def __init__(self, parent = None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def initUI(self):
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self.setGeometry(finalGeometry)

        self.canvasEditor = QScreenPainterWidget(self)
        self.canvasEditor.completeDrawAfterSignal.connect(self.onCompleteDrawAfter)
        self.contentLayout.addWidget(self.canvasEditor)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

    def onCompleteDrawAfter(self):
        self.setMouseThroughState(True)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        if self.canvasEditor.drawWidget != None and not self.canvasEditor.drawWidget.isEditorEnabled():
            return
        self.canvasEditor.initDrawLayer()
        self.canvasEditor.showCommandBar()

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        # 经测试，发现该数值小于0.5之后，透明部分会穿透，因此透明度范围设为[0.5, 1]
        finalValue = min(max(0.5, finalValue), 1)

        self.setWindowOpacity(finalValue)

    def initActions(self):
        actions = [
            Action("切换到演示模式", self, triggered=self.switchPreviewMode, shortcut="ctrl+w"),
        ]
        self.addActions(actions)

    def switchPreviewMode(self):
        self.canvasEditor.completeDraw()

    def startDraw(self):
        self.canvasEditor.drawWidget.setEditorEnabled(True)
        self.setMouseThroughState(False)

    def isAllowModifyOpactity(self):
        # return not self.canvasEditor.drawWidget.isEditorEnabled()
        return True

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.isAllowModifyOpactity() and int(event.modifiers()) == Qt.ControlModifier:
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        else:
            return super().wheelEvent(event)