# coding=utf-8
import win32ui, win32con
import typing
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import (RoundMenu, Action, FluentIcon, TeachingTipTailPosition)
from icon import ScreenShotIcon
from painter_tools import QPainterWidget, DrawActionEnum
from canvas_item import *

class QScreenPainterWidget(QPainterWidget):
    def __init__(self, parent=None):
        super().__init__(parent, None, 0, 0)

    def getCommandBarPosition(self) -> TeachingTipTailPosition:
        return TeachingTipTailPosition.LEFT_BOTTOM

    def contextMenuEvent(self, event:QtGui.QContextMenuEvent):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(ScreenShotIcon.WHITE_BOARD, '标注', triggered=self.showCommandBar),
            Action(ScreenShotIcon.COPY, '复制', triggered=self.copyToClipboard),
            Action(ScreenShotIcon.CLICK_THROUGH, '预览模式', triggered=self.switchPreviewMode),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def switchPreviewMode(self):
        self.parentWidget().swtichShow()
        pass

    def completeDraw(self):
        super().completeDraw()

class ScreenPaintWindow(QWidget):  # 屏幕窗口
    def __init__(self, parent = None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def initUI(self):
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self.setGeometry(finalGeometry)

        self.canvasEditor = QScreenPainterWidget(self)
        self.contentLayout.addWidget(self.canvasEditor)
        self.canvasEditor.showCommandBar()

    def initActions(self):
        actions = [
            Action("复制贴图", self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            Action("保存贴图", self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            Action("隐藏标注", self, triggered=self.hide),
            Action("切换到演示模式", self, triggered=self.swtichShow, shortcut="ctrl+w"),
            # Action("切换到绘画模式", self, triggered=self.startDraw, shortcut="ctrl+t"),
        ]
        self.addActions(actions)

    def swtichShow(self):
        self.canvasEditor.drawWidget.setEditorEnabled(False)
        self.setMouseThought(True)

    def startDraw(self):
        self.canvasEditor.drawWidget.setEditorEnabled(True)
        self.setMouseThought(False)

    def copyToClipboard(self):
        # self.pixmapWidget.copyToClipboard()
        finalPixmap = self.grab()
        QApplication.clipboard().setPixmap(finalPixmap)

    def saveToDisk(self):
        savePath = self.save_file_dialog()
        if savePath != None:
            # 保存的截图无阴影
            # finalPixmap = self.pixmapWidget.getFinalPixmap()

            # 保存带阴影的截图
            finalPixmap = self.grab()
            finalPixmap.save(savePath, "png")

    def save_file_dialog(self):
        openFlags = win32con.OFN_OVERWRITEPROMPT|win32con.OFN_EXPLORER
        fspec = "PNG(*.png)"
        # 获取当前时间，并格式化
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = f"Snipaste_{now_str}.png"
        dlg = win32ui.CreateFileDialog(0, None, fileName, openFlags, fspec)  # 0表示保存文件对话框
        dlg.SetOFNInitialDir('C:\\')  # 设置保存文件对话框中的初始显示目录
        isOk = dlg.DoModal()
        if isOk == 1:
            return dlg.GetPathName()  # 获取选择的文件名称
        return None

    def setMouseThought(self, isThought:bool):
        self.setWindowFlag(Qt.WindowTransparentForInput, isThought)
        self.show()