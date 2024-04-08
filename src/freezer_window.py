# coding=utf-8
import os, math
import win32ui, win32con
import typing
from enum import Enum
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF, QMargins, QPointF

from PyQt5.QtGui import QIcon, QCursor, QPainter, QColor, QPen, QPixmap, QPainterPath, QBrush, QMoveEvent, QFocusEvent
from PyQt5.QtWidgets import QLabel, QMenu, QWidget, QApplication, QSizePolicy, QVBoxLayout, QGraphicsDropShadowEffect, QToolBar, QAction
from qfluentwidgets import (RoundMenu, Action, FluentIcon)

from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QTextEdit
from painter_tools import QDragWindow, QPainterWidget
from ui_canvas_text_item import UICanvasTextItem, QGraphicsContainer
from PyQt5.QtGui import QImage, QPixmap

class FreezerWindow(QDragWindow):  # 固定图片类
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.shadowWidth = 30
        self.xRadius = 20
        self.yRadius = 20
        self.borderLineWidth = 0.5
        self.setGeometry(screenPoint.x()-self.shadowWidth, screenPoint.y()-self.shadowWidth, physicalSize.width()+2*self.shadowWidth, physicalSize.height()+2*self.shadowWidth)
        self.layout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

        self.pixmapWidget = QPainterWidget(self, physicalPixmap, self.xRadius, self.yRadius)
        self.layout.addWidget(self.pixmapWidget)

        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)

        self.initActions()

        self.unFocusColor = QColor(125, 125, 125, 50)
        self.focusColor = QColor(255, 0, 255, 50)
        self.focused = False
        self.painter = QPainter()
        self.closeCallback = closeCallback
        self.show()

    def initActions(self):
        actions = [
            Action("复制贴图", self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            Action("保存贴图", self, triggered=self.saveToDisk, shortcut="ctrl+s")
        ]
        self.addActions(actions)

    def copyToClipboard(self):
        self.pixmapWidget.copyToClipboard()

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

    # https://zhangzc.blog.csdn.net/article/details/113916322
    # 改变窗口穿透状态
    def changeMouseThought(self):
        if self.isMouseThought():
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowTransparentForInput)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)

        self.show()

    def setMouseThought(self, can:bool):
        if can:
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowTransparentForInput)

        self.show()

    # 判断窗口的鼠标是否穿透了
    def isMouseThought(self):
        return (self.windowFlags() | Qt.WindowTransparentForInput) == self.windowFlags()

    def mousePressEvent(self, event):
        self.isPresse = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.isPresse = False
        # textContainer = QGraphicsContainer()
        # textContainer.setGeometry(QRectF(self.rect().center(), QSizeF(100, 100)))
        # self.scene.addItem(textContainer)

        # self.layout.addWidget(view)
        # self.show()

        # textContainer.realItem.setPlainText("")
        # textContainer.switchEditableBox()
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.close()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

    	# 阴影
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        self.painter.fillPath(path, QBrush(Qt.white))
        if self.focused:
            color = self.focusColor
        else:
            color = self.unFocusColor

        for i in range(10):
            i_path = QPainterPath()
            i_path.setFillRule(Qt.WindingFill)
            ref = QRectF(self.shadowWidth-i, self.shadowWidth-i, self.width()-(self.shadowWidth-i)*2, self.height()-(self.shadowWidth-i)*2)
            # i_path.addRect(ref)
            i_path.addRoundedRect(ref, self.xRadius, self.yRadius)
            color.setAlpha(150 - i**0.5*50)
            # color.setAlpha(150 - math.sqrt(i) * 50)
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        self.painter.end()

    def closeEvent(self, event) -> None:
        self.pixmapWidget.close()
        if self.closeCallback != None:
            self.closeCallback()