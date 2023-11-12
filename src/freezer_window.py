# coding=utf-8
import os
import sys
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

        self.unFocusColor = QColor(125, 125, 125, 50)
        self.focusColor = QColor(255, 0, 255, 50)
        self.focused = False
        self.painter = QPainter()
        self.closeCallback = closeCallback
        self.show()

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
        return (self.windowFlags() | Qt.WindowTransparentForInput) == self.windowFlags();

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
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        self.painter.end()

    def closeEvent(self, event) -> None:
        self.pixmapWidget.close()
        if self.closeCallback != None:
            self.closeCallback()