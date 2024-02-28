# coding=utf-8
import os
import sys, math
from enum import Enum
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF, QMargins, QPointF, QSizeF

from PyQt5.QtGui import QIcon, QCursor, QPainter, QColor, QPen, QPixmap, QPainterPath, QBrush, QMoveEvent, QFocusEvent, QRegion, QFont
from PyQt5.QtWidgets import QLabel, QMenu, QWidget, QApplication, QSizePolicy, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QToolBar, QAction, QActionGroup
from qfluentwidgets import (RoundMenu, Action, FluentIcon, InfoBar, InfoBarPosition, CommandBarView, Flyout, FlyoutAnimationType, TeachingTip, TeachingTipTailPosition, TeachingTipView)
from icon import ScreenShotIcon

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView
# from ui_canvas_rect_item import UICanvasRectItem
from ui_canvas_text_item import UICanvasTextItem, QGraphicsContainer
# from ui_canvas_view import UICanvasView

from canvas_scene import CanvasScene
from canvas_view import CanvasView as UICanvasView

class QAutoSizeTextEdit(QTextEdit):
    focusChanged = QtCore.pyqtSignal(int)
    """ 支持自动调整大小的文本框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置该控件的背景透明
        self.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                font-family: 微软雅黑;
                font-size: 16px;
                color: red;
                padding: 1px;
                margin: 4px;
                selection-background-color: rgb(0, 120, 255);
                selection-color: white;
            }

            QTextEdit:hover {
                border-style: dashed;
                border-width: 1.3px;
                border-color: white
            }

            QTextEdit:focus {
                border-style: solid;
                border-width: 1px;
                border-color: white
            }
        """)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignLeft)
        self.setLineWrapMode(QTextEdit.NoWrap)

        self.contentDocument = self.document()
        self.contentDocument.contentsChanged.connect(self.textAreaChanged)
        # 去掉文本内容框的边距
        # self.contentDocument.setDocumentMargin(0)

    def defaultShow(self, pos:QPoint):
        self.show()
        self.setText("")
        # 光标与文本框的偏移量
        offsetPos = self.rect().center()
        self.move(pos - offsetPos)
        self.setFocus()

    def textAreaChanged(self):
        self.contentDocument.adjustSize()
 
        # 计算文本框的宽度和高度
        newWidth = self.contentDocument.size().width()
        newHeight = self.contentDocument.size().height()
        contentsMargins = self.contentsMargins()
        newFixedSize = QSize(newWidth + contentsMargins.left() + contentsMargins.right() + 1, newHeight + contentsMargins.top() + contentsMargins.bottom())
        self.setFixedSize(newFixedSize)

    def focusInEvent(self, event:QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focusChanged.emit(1)

    def focusOutEvent(self, event:QFocusEvent) -> None:
        super().focusOutEvent(event)
        self.focusChanged.emit(-1)
        # 当该文本框焦点失去时，则取消其文本选中状态
        textCursor = self.textCursor()
        textCursor.clearSelection()
        self.setTextCursor(textCursor)

# 拖曳移动窗口类
class QDragWindow(QLabel):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.drag = False

    def startDrag(self):
        pass

    def endDrag(self):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = True
            self.posX, self.posY = event.x(), event.y()
            self.startDrag()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.endDrag()

    def mouseMoveEvent(self, event):
        if self.isVisible():
            if self.drag:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                self.move(event.x() + self.x() - self.posX, event.y() + self.y() - self.posY)

# 贴图控件
class QPixmapWidget(QLabel):
    def __init__(self, parent=None, physicalPixmap:QPixmap=None, xRadius:float=20, yRadius:float=20):
        super().__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)
        self.physicalPixmap = physicalPixmap
        self.xRadius = xRadius
        self.yRadius = yRadius
        self.borderLineWidth = 1
        self.blinkColors = [Qt.GlobalColor.red, Qt.GlobalColor.yellow, Qt.GlobalColor.green]
        self.blinkTimers = 0
        self.blinkColor = self.blinkColors[self.blinkTimers]

        self.blinkTimer = QtCore.QTimer(self)
        self.blinkTimer.timeout.connect(self.onBlinkTimerTimeout)
        self.blinkTimer.start(300)

        self.painter = QPainter()

    def onBlinkTimerTimeout(self):
        if self.blinkTimers < len(self.blinkColors) - 1:
            self.blinkTimers += 1
            self.blinkColor = self.blinkColors[self.blinkTimers]
            self.update()
        else:
            self.blinkTimer.stop()
            self.blinkColor = None
            self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        canvasPixmap = self.physicalPixmap.copy()
        self.painter.begin(canvasPixmap)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # # 绘制闪烁边框
        if self.blinkColor != None:
            blinkPen = QPen(self.blinkColor)  # 实线，浅蓝色
            blinkPen.setStyle(QtCore.Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
            blinkPen.setWidthF(self.borderLineWidth)  # 0表示线宽为1
            self.painter.setPen(blinkPen)
            rect = self.rect()
            self.painter.drawRect(rect)
            # self.painter.drawRoundedRect(rect, self.xRadius, self.yRadius)

        self.painter.end()

        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # clipPath = QPainterPath()
        # clipPath.addRoundedRect(QRectF(self.rect()), self.xRadius, self.yRadius)
        # self.painter.setClipPath(clipPath)
        self.painter.drawPixmap(self.rect(), canvasPixmap)
        self.painter.end()

# 描边控件
class QOutlineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.isHover = False

    def enterEvent(self, e):
        self.isHover = True
        self.update()

    def leaveEvent(self, e):
        self.isHover = False
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        if not self.isEnabled():
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        rect = self.rect()

        pen = QPen(Qt.DashLine)
        if self.isHover:
            pen.setColor(Qt.green)
        else:
            pen.setColor(Qt.red)
        painter.setPen(pen)

        painter.drawRect(rect)

class QPenErase(QWidget):
    """ 橡皮擦工具，将橡皮擦划过的痕迹的背景覆盖到最顶层达到擦除的效果 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.pointsItems = []
        self.isRecord = False

        imgpix:QPixmap = parent.physicalPixmap.copy()
        screenDevicePixelRatio = QApplication.primaryScreen().grabWindow(0).devicePixelRatio()

        self.brush = QBrush(imgpix)
        self.brush.setTransform(QtGui.QTransform().scale(1/screenDevicePixelRatio, 1/screenDevicePixelRatio))
        self.pen = QPen(self.brush, 10)

        self.painter = QPainter()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        if len(self.pointsItems) > 0:
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.setPen(self.pen)

            for points in self.pointsItems:
                for i in range(len(points) - 1):
                    self.painter.drawLine(points[i], points[i+1])

        self.painter.end()

        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isRecord = True
            self.points = []
            self.pointsItems.append(self.points)
            self.points.append(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.isRecord:
                self.points.append(event.pos())
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isRecord:
                self.points.append(event.pos())
                self.isRecord = False
                self.update()

class QPenLine(QWidget):
    """ 画笔工具 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.pointsItems = []
        self.isRecord = False

        self.pen = QPen(QColor(Qt.red), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.painter = QPainter()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        if len(self.pointsItems) > 0:
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.setPen(self.pen)

            for points in self.pointsItems:
                for i in range(len(points) - 1):
                    self.painter.drawLine(points[i], points[i+1])
        self.painter.end()

        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isRecord = True
            self.points = []
            self.pointsItems.append(self.points)
            self.points.append(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.isRecord:
                self.points.append(event.pos())
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isRecord:
                self.points.append(event.pos())
                self.isRecord = False
                self.update()

class DraggableRect(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setBrush(QBrush(QColor(255, 0, 0, 100)))
        self.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))
        self.resize_mode = False

    def hoverMoveEvent(self, event):
        if self.isSelected():
            if event.pos().x() > self.boundingRect().width() - 5 and event.pos().y() > self.boundingRect().height() - 5:
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        else:
            super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isSelected() and self.cursor() == Qt.SizeFDiagCursor:
            self.resize_mode = True
            self.start_pos = event.pos()
            self.start_rect = self.rect()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resize_mode:
            delta = event.pos() - self.start_pos
            new_rect = QRectF(self.start_rect)
            new_rect.setWidth(self.start_rect.width() + delta.x())
            new_rect.setHeight(self.start_rect.height() + delta.y())
            self.setRect(new_rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.resize_mode:
            self.resize_mode = False
        else:
            super().mouseReleaseEvent(event)

class QPenPolygonalLine(QWidget):
    """ 折线工具 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.pointsItems = []
        self.isRecord = False
        # 光标正在移动的点
        self.movePoint = None

        self.pen = QPen(QColor(Qt.red), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.painter = QPainter()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        count = len(self.pointsItems)
        if count > 0:
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.setPen(self.pen)

            for points in self.pointsItems:
                count = count - 1
                for i in range(len(points) - 1):
                    self.painter.drawLine(points[i], points[i+1])

                if self.isRecord and count == 0 and len(points) > 0 and not self.movePoint == None:
                    # 获取points最后一个元素
                    self.painter.drawLine(points[-1], self.movePoint)

        self.painter.end()

        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.isRecord:
                self.isRecord = True
                self.points = []
                self.pointsItems.append(self.points)
                self.points.append(event.pos())
            else:
                self.points.append(event.pos())
            self.update()

    def mouseMoveEvent(self, event):
        if self.isRecord:
            self.movePoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.isRecord:
                self.isRecord = False
                self.update()
                self.movePoint = None

class QPenRectangleBak(QWidget):
    """ 绘制矩形工具 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def initUI(self):
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scene = CanvasScene()
        view = UICanvasView(self.scene)
        self.layout.addWidget(view)

    def init(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # view = QOutlineWidget(self)

        self.scene = CanvasScene()
        view = UICanvasView(self.scene, self)
        # self.scene = QGraphicsScene()
        # view = UICanvasView(self.scene, self)
        # view = QGraphicsView(self.scene, self)
        view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        view.scene().setSceneRect(0, 0, self.width(), self.height())
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setStyleSheet("background: transparent; border:0px;")
        view.setRenderHint(QPainter.Antialiasing)
        view.setDragMode(QGraphicsView.RubberBandDrag)
        # rect = DraggableRect(0, 0, 100, 100)

        # rectItem = UICanvasRectItem()
        # rectItem.setSize(100, 100)
        # rectItem.setPos(20, 30)
        # self.scene.addItem(rectItem)

        # textItem = UICanvasTextItem()
        # textItem.setPlainText("测试文本")
        # textItem.setPos(self.rect().center())
        # self.scene.addItem(textItem)

        # textContainer = QGraphicsContainer()
        # textContainer.setGeometry(QRectF(self.rect().center(), QSizeF(100, 100)))
        # self.scene.addItem(textContainer)

        textContainer = QGraphicsContainer()
        textContainer.setGeometry(QRectF(self.rect().center(), QSizeF(100, 100)))
        self.scene.addItem(textContainer)

        self.layout.addWidget(view)
        self.show()

        textContainer.realItem.setPlainText("")
        textContainer.switchEditableBox()

class QPenRectangle(QWidget):
    """ 绘制矩形工具 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.points = None
        self.pointsItems = []
        self.isRecord = False

        self.pen = QPen(QColor(Qt.yellow), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.borderPen = QPen(QColor(Qt.blue), 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
        self.borderPen.setDashPattern([5, 5])
        self.painter = QPainter()

        self.borderWidth = 2
        self.topEdgeRect = None
        self.bottomEdgeRect = None
        self.leftEdgeRect = None
        self.rightEdgeRect = None

        self.isMoving = False

    def containsBoarder(self, pos:QPoint, rect:QRect):
        # 计算Qt.TopEdge的所在区域
        self.topEdgeRect = QRect(rect.topLeft() - QPoint(0, self.borderWidth), QSize(rect.width(), self.borderWidth * 2))
        # 计算Qt.BottomEdge的所在区域
        self.bottomEdgeRect = QRect(rect.bottomLeft() - QPoint(0, self.borderWidth), QSize(rect.width(), self.borderWidth * 2))
        # 计算Qt.LeftEdge的所在区域
        self.leftEdgeRect = QRect(rect.topLeft() - QPoint(self.borderWidth, 0), QSize(self.borderWidth * 2, rect.height()))
        # 计算Qt.RightEdge的所在区域
        self.rightEdgeRect = QRect(rect.topRight() - QPoint(self.borderWidth, 0), QSize(self.borderWidth * 2, rect.height() - self.borderWidth * 2))

        checkRects = [(Qt.Edge.TopEdge, self.topEdgeRect), (Qt.Edge.BottomEdge, self.bottomEdgeRect), (Qt.Edge.LeftEdge, self.leftEdgeRect), (Qt.Edge.RightEdge, self.rightEdgeRect)]

        for checkRect in checkRects:
            if checkRect[1].contains(pos):
                return checkRect[0]
        return None

    def ban(self):
        self.isMoving = False
        self.isRecord = True
        self.update()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        if len(self.pointsItems) > 0:
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.setPen(self.pen)

            for points in self.pointsItems:
                self.painter.drawRect(QRect(points[0], points[-1]))

            if self.topEdgeRect != None and not self.isRecord:
                self.painter.setPen(self.borderPen)
                self.painter.drawRect(QRect(self.points[0], self.points[-1]))

        self.painter.end()

        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.points != None and not self.isRecord:
                result = self.containsBoarder(event.pos(), QRect(self.points[0], self.points[-1]))
                if result != None:
                    self.isMoving = True
                    self._drag_vector = event.pos() - self.points[0]
                    self.editingRect = QRect(self.points[0], self.points[-1])
                    return

            self.isRecord = True
            self.points = [event.pos(), event.pos()]
            self.pointsItems.append(self.points)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if event.buttons() == Qt.LeftButton:
            if self.isMoving:
                self.editingRect.moveTo(pos - self._drag_vector)
                self.points[0] = self.editingRect.topLeft()
                self.points[-1] = self.editingRect.bottomRight()
            elif self.isRecord:
                self.points[-1] = event.pos()
            self.update()

        if self.points != None and not self.isRecord:
            result = self.containsBoarder(event.pos(), QRect(self.points[0], self.points[-1]))
            self.update()
            if result != None:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isMoving:
                self.isMoving = False
                self.update()
            elif self.isRecord:
                self.points[-1] = event.pos()
                self.isRecord = False
                self.update()

class QPenArrow(QWidget):
    """ 绘制箭头工具 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.points = None
        self.pointsItems = []
        self.isRecord = False

        self.pen = QPen(QColor(Qt.yellow), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.borderPen = QPen(QColor(Qt.blue), 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
        self.borderPen.setDashPattern([5, 5])
        self.painter = QPainter()

        self.borderWidth = 2
        self.topEdgeRect = None
        self.bottomEdgeRect = None
        self.leftEdgeRect = None
        self.rightEdgeRect = None

        self.isMoving = False

    def containsBoarder(self, pos:QPoint, rect:QRect):
        # 计算Qt.TopEdge的所在区域
        self.topEdgeRect = QRect(rect.topLeft() - QPoint(0, self.borderWidth), QSize(rect.width(), self.borderWidth * 2))
        # 计算Qt.BottomEdge的所在区域
        self.bottomEdgeRect = QRect(rect.bottomLeft() - QPoint(0, self.borderWidth), QSize(rect.width(), self.borderWidth * 2))
        # 计算Qt.LeftEdge的所在区域
        self.leftEdgeRect = QRect(rect.topLeft() - QPoint(self.borderWidth, 0), QSize(self.borderWidth * 2, rect.height()))
        # 计算Qt.RightEdge的所在区域
        self.rightEdgeRect = QRect(rect.topRight() - QPoint(self.borderWidth, 0), QSize(self.borderWidth * 2, rect.height() - self.borderWidth * 2))

        checkRects = [(Qt.Edge.TopEdge, self.topEdgeRect), (Qt.Edge.BottomEdge, self.bottomEdgeRect), (Qt.Edge.LeftEdge, self.leftEdgeRect), (Qt.Edge.RightEdge, self.rightEdgeRect)]

        for checkRect in checkRects:
            if checkRect[1].contains(pos):
                return checkRect[0]
        return None

    def ban(self):
        self.isMoving = False
        self.isRecord = True
        self.update()

    # 绘制箭头
    def paintArrow(self, begin:QPoint, end:QPoint, p:QPainter):
        if begin == end:
            return

        p.save()

        x1 = begin.x()                                      # 取 points[0] 起点的 x
        y1 = begin.y()                                      # 取 points[0] 起点的 y  
        x2 = end.x()                                        # 取 points[count-1] 终点的 x  
        y2 = end.y()                                        # 取 points[count-1] 终点的 y  
        l = 32.0                                            # 箭头的长度  
        a = 0.5                                             # 箭头与线段角度  
        x3 = x2 - l * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - a) # 计算箭头的终点（x3,y3）  
        y3 = y2 - l * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - a)   
        x4 = x2 - l * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - a) # 计算箭头的终点（x4,y4）  
        y4 = y2 - l * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - a)   

        i = 18                                              # 箭身的长度
        b = 0.2                                             # 箭身与线段角度  
        x5 = x2 - i * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - b) # 计算箭头的终点（x5,y5）  
        y5 = y2 - i * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - b)   
        x6 = x2 - i * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - b) # 计算箭头的终点（x6,y6）  
        y6 = y2 - i * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - b)   

        arrowTailPos = QPointF(x1, y1) # 箭尾位置点
        arrowHeadPos = QPointF(x2, y2) # 箭头位置点
        arrowHeadRightPos = QPointF(x3, y3) # 箭头右侧边缘位置点
        arrowHeadLeftPos = QPointF(x4, y4) # 箭头左侧边缘位置点
        arrowBodyRightPos = QPointF(x5, y5) # 箭身右侧位置点
        arrowBodyLeftPos = QPointF(x6, y6) # 箭身左侧位置点

        p.setPen(QPen(Qt.red, 2))
        p.setBrush(Qt.red)

        fullPath = QPainterPath()
        fullPath.moveTo(arrowTailPos)
        fullPath.lineTo(arrowBodyLeftPos)
        fullPath.lineTo(arrowHeadLeftPos)
        fullPath.lineTo(arrowHeadPos)
        fullPath.lineTo(arrowHeadRightPos)
        fullPath.lineTo(arrowBodyRightPos)
        fullPath.closeSubpath()
        p.drawPath(fullPath)

        p.setPen(QPen(Qt.white, 2))
        font = QFont()
        font.setPointSizeF(12)
        p.setFont(font)

        p.restore()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        if len(self.pointsItems) > 0:
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.setPen(self.pen)

            for points in self.pointsItems:
                self.paintArrow(points[0], points[-1], self.painter)

            # if self.topEdgeRect != None and not self.isRecord and points[0] != points[-1]:
            #     self.painter.setPen(self.borderPen)
            #     self.painter.drawRect(QRect(self.points[0], self.points[-1]))

        self.painter.end()

        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.points != None and not self.isRecord:
                result = self.containsBoarder(event.pos(), QRect(self.points[0], self.points[-1]))
                if result != None:
                    self.isMoving = True
                    self._drag_vector = event.pos() - self.points[0]
                    self.editingRect = QRect(self.points[0], self.points[-1])
                    return

            self.isRecord = True
            self.points = [event.pos(), event.pos()]
            self.pointsItems.append(self.points)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if event.buttons() == Qt.LeftButton:
            if self.isMoving:
                self.editingRect.moveTo(pos - self._drag_vector)
                self.points[0] = self.editingRect.topLeft()
                self.points[-1] = self.editingRect.bottomRight()
            elif self.isRecord:
                self.points[-1] = event.pos()
            self.update()

        if self.points != None and not self.isRecord:
            result = self.containsBoarder(event.pos(), QRect(self.points[0], self.points[-1]))
            self.update()
            if result != None:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isMoving:
                self.isMoving = False
                self.update()
            elif self.isRecord:
                self.points[-1] = event.pos()
                self.isRecord = False
                self.update()

class QPenStar(QWidget):
    """ 绘制五角星工具 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.points = None
        self.pointsItems = []
        self.isRecord = False

        self.pen = QPen(QColor(Qt.yellow), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.borderPen = QPen(QColor(Qt.blue), 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
        self.borderPen.setDashPattern([5, 5])
        self.painter = QPainter()

        self.borderWidth = 2
        self.topEdgeRect = None
        self.bottomEdgeRect = None
        self.leftEdgeRect = None
        self.rightEdgeRect = None

        self.isMoving = False

    def containsBoarder(self, pos:QPoint, rect:QRect):
        # 计算Qt.TopEdge的所在区域
        self.topEdgeRect = QRect(rect.topLeft() - QPoint(0, self.borderWidth), QSize(rect.width(), self.borderWidth * 2))
        # 计算Qt.BottomEdge的所在区域
        self.bottomEdgeRect = QRect(rect.bottomLeft() - QPoint(0, self.borderWidth), QSize(rect.width(), self.borderWidth * 2))
        # 计算Qt.LeftEdge的所在区域
        self.leftEdgeRect = QRect(rect.topLeft() - QPoint(self.borderWidth, 0), QSize(self.borderWidth * 2, rect.height()))
        # 计算Qt.RightEdge的所在区域
        self.rightEdgeRect = QRect(rect.topRight() - QPoint(self.borderWidth, 0), QSize(self.borderWidth * 2, rect.height() - self.borderWidth * 2))

        checkRects = [(Qt.Edge.TopEdge, self.topEdgeRect), (Qt.Edge.BottomEdge, self.bottomEdgeRect), (Qt.Edge.LeftEdge, self.leftEdgeRect), (Qt.Edge.RightEdge, self.rightEdgeRect)]

        for checkRect in checkRects:
            if checkRect[1].contains(pos):
                return checkRect[0]
        return None

    def ban(self):
        self.isMoving = False
        self.isRecord = True
        self.update()

    # 绘制五角星
    def paintStar(self, targetBottomLeft:QPoint, targetTopRight:QPoint, p:QPainter):
        p.save()

        # 计算正五角星的十个点
        # 计算公式网站 https://zhidao.baidu.com/question/2073567152212492428/answer/1566351173.html
        r = 100
        A = QPointF(r * math.cos(18 * math.pi / 180), r * math.sin(18 * math.pi / 180))
        B = QPointF(r * math.cos(90 * math.pi / 180), r * math.sin(90 * math.pi / 180))
        C = QPointF(r * math.cos(162 * math.pi / 180), r * math.sin(162 * math.pi / 180))
        D = QPointF(r * math.cos(234 * math.pi / 180), r * math.sin(234 * math.pi / 180))
        E = QPointF(r * math.cos(306 * math.pi / 180), r * math.sin(306 * math.pi / 180))
        r1 = r * math.sin(18 * math.pi / 180) / math.sin(126 * math.pi / 180)
        F = QPointF(r1 * math.cos(54 *  math.pi / 180), r1 * math.sin(54 *  math.pi / 180))
        G = QPointF(r1 * math.cos(126 * math.pi / 180), r1 * math.sin(126 * math.pi / 180))
        H = QPointF(r1 * math.cos(198 * math.pi / 180), r1 * math.sin(198 * math.pi / 180))
        I = QPointF(r1 * math.cos(270 * math.pi / 180), r1 * math.sin(270 * math.pi / 180))
        J = QPointF(r1 * math.cos(342 * math.pi / 180), r1 * math.sin(342 * math.pi / 180))

        # 根据起始点和结束点来缩放这个坐标，当前五角星的实际矩形是：
        oldBottomLeft = QPointF(C.x(), B.y())
        oldTopRight = QPointF(A.x(), E.y())

        # 两个矩形的左下角对齐
        offsetPos = oldBottomLeft - targetBottomLeft
        A -= offsetPos
        B -= offsetPos
        C -= offsetPos
        D -= offsetPos
        E -= offsetPos
        F -= offsetPos
        G -= offsetPos
        H -= offsetPos
        I -= offsetPos
        J -= offsetPos

        oldBottomLeft -= offsetPos
        oldTopRight -= offsetPos

        # 右上角的拉伸
        lastRect = QRectF(oldBottomLeft, oldTopRight)
        newRect = QRectF(targetBottomLeft, targetTopRight)

        xScale = newRect.width() / lastRect.width()
        yScale = newRect.height() / lastRect.height()

        allPoints:list[QPointF] = [A, B, C, D, E, F, G, H, I, J, oldBottomLeft, oldTopRight]

        for i in range(0, len(allPoints)):
            oldPos = allPoints[i]
            xPos = oldPos.x() + abs(oldPos.x() - lastRect.bottomLeft().x()) * (xScale - 1)
            yPos = oldPos.y() - abs(oldPos.y() - lastRect.topRight().y()) * (yScale - 1)

            oldPos.setX(xPos)
            oldPos.setY(yPos)

        # 画五角星
        path = QPainterPath()
        path.moveTo(B)
        path.lineTo(F)
        path.lineTo(A)
        path.lineTo(J)
        path.lineTo(E)
        path.lineTo(I)
        path.lineTo(D)
        path.lineTo(H)
        path.lineTo(C)
        path.lineTo(G)
        path.lineTo(B)
        p.drawPath(path)

        # 透明度
        p.setOpacity(0.6)
        p.fillPath(path, QBrush(Qt.yellow))

        # font = QFont()
        # font.setPointSizeF(20)
        # p.setFont(font)
        # p.setPen(QPen(Qt.red, 2))

        # p.drawText(A, "A")
        # p.drawText(B, "B")
        # p.drawText(C, "C")
        # p.drawText(D, "D")
        # p.drawText(E, "E")
        # p.drawText(F, "F")
        # p.drawText(G, "G")
        # p.drawText(H, "H")
        # p.drawText(I, "I")
        # p.drawText(J, "J")

        # p.drawText(targetBottomLeft, "targetBottomLeft")
        # p.drawText(targetTopRight, "targetTopRight")

        # p.drawText(oldBottomLeft, "oldBottomLeft")
        # p.drawText(oldTopRight, "oldTopRight")

        # p.setPen(QPen(Qt.green, 1, Qt.DashLine))
        # p.drawRect(QRectF(oldBottomLeft, oldTopRight))

        p.restore()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        if len(self.pointsItems) > 0:
            self.painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self.painter.setPen(self.pen)

            for points in self.pointsItems:
                self.paintStar(points[0], points[-1], self.painter)

            # if self.topEdgeRect != None and not self.isRecord:
            #     self.painter.setPen(self.borderPen)
            #     self.painter.drawRect(QRect(self.points[0], self.points[-1]))

        self.painter.end()

        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.points != None and not self.isRecord:
                result = self.containsBoarder(event.pos(), QRect(self.points[0], self.points[-1]))
                if result != None:
                    self.isMoving = True
                    self._drag_vector = event.pos() - self.points[0]
                    self.editingRect = QRect(self.points[0], self.points[-1])
                    return

            self.isRecord = True
            self.points = [event.pos(), event.pos()]
            self.pointsItems.append(self.points)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if event.buttons() == Qt.LeftButton:
            if self.isMoving:
                self.editingRect.moveTo(pos - self._drag_vector)
                self.points[0] = self.editingRect.topLeft()
                self.points[-1] = self.editingRect.bottomRight()
            elif self.isRecord:
                self.points[-1] = event.pos()
            self.update()

        if self.points != None and not self.isRecord:
            result = self.containsBoarder(event.pos(), QRect(self.points[0], self.points[-1]))
            self.update()
            if result != None:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isMoving:
                self.isMoving = False
                self.update()
            elif self.isRecord:
                self.points[-1] = event.pos()
                self.isRecord = False
                self.update()


class DrawActionEnum(Enum):
    DrawNone = "无操作"
    DrawText = "编辑文字"
    DrawLine = "使用画笔"
    ApplyErase = "应用橡皮擦"
    DrawRectangle = "绘制矩形"
    DrawArrow = "绘制箭头"
    DrawStar = "绘制五角星"
    DrawPolygonalLine = "绘制多边形"

# 绘制动作
class DrawAction():
    def __init__(self, actionEnum:DrawActionEnum, painterTool:QWidget, callback=None) -> None:
        self.actionEnum:DrawActionEnum = actionEnum
        self.painterTool = painterTool
        self.callback = callback

    def switchEditState(self, isEdit:bool):
        if self.callback != None:
            self.callback(isEdit)

    def IsShouldRemove(self):
        if self.actionEnum == DrawActionEnum.DrawText:
            return len(self.painterTool.toPlainText()) == 0
        if self.actionEnum == DrawActionEnum.DrawLine:
            return len(self.painterTool.pointsItems) == 0
        if self.actionEnum == DrawActionEnum.ApplyErase:
            return len(self.painterTool.pointsItems) == 0
        return False

# 绘图控件
class QPainterWidget(QPixmapWidget):
    def __init__(self, parent=None, physicalPixmap:QPixmap=None, xRadius:float=20, yRadius:float=20):
        super().__init__(parent, physicalPixmap, xRadius, yRadius)
        self.toolbar:QWidget = None
        self.actionGroup:QActionGroup = None
        self.clearDraw(True)

    def showCommandBar(self):
        if self.toolbar != None:
            self.toolbar.show()
            return

        position = TeachingTipTailPosition.TOP_RIGHT
        view = CommandBarView(self)
        closeAction = Action(ScreenShotIcon.FINISHED, '完成绘画')

        drawActions = [
            Action(ScreenShotIcon.RECTANGLE, '矩形', triggered=self.drawRectangle),
            Action(ScreenShotIcon.POLYGONAL_LINE, '折线', triggered=self.drawPolygonalLine),
            Action(ScreenShotIcon.POLYGON, '多边形', triggered=self.drawPolygonal),
            Action(ScreenShotIcon.ARROW, '箭头', triggered=self.drawArrow),
            Action(ScreenShotIcon.STAR, '星星', triggered=self.drawStar),
            Action(ScreenShotIcon.MARKER_PEN, '记号笔', triggered=self.useMarkerPen),
            Action(ScreenShotIcon.PENCIL, '铅笔', triggered=self.usePencil),
            Action(ScreenShotIcon.TEXT, '文本', triggered=self.drawText),
            Action(ScreenShotIcon.ERASE, '橡皮擦', triggered=self.applyErase),
        ]

        self.actionGroup = QActionGroup(self)
        for action in drawActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)

        view.addActions(drawActions)
        view.addSeparator()
        view.addActions([
            # Action(ScreenShotIcon.OCR, '退出绘画', triggered=self.clearDrawFlag),
            Action(ScreenShotIcon.DELETE_ALL, '清除绘画', triggered=self.clearDraw),
            Action(ScreenShotIcon.UNDO2, '撤销', triggered=self.undo),
            Action(ScreenShotIcon.REDO2, '重做', triggered=self.redo),
            closeAction,
        ])

        view.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        view.setIconSize(QSize(20, 20))

        view.resizeToSuitableWidth()
        self.toolbar = TeachingTip.make(
            target=self,
            view=view,
            duration=-1,
            tailPosition=position,
            parent=self
        )

        closeAction.triggered.connect(self.completeDraw)

    def completeDraw(self):
        if self.toolbar != None:
            self.clearDrawFlag()
            self.toolbar.close()
            self.toolbar.destroy()
            self.toolbar = None

    def closeEvent(self, event):
        super().closeEvent(event)
        self.completeDraw()

    def hasFocusByActionEnum(self, actionEnum:DrawActionEnum):
        for action in self.drawActions:
            if action.actionEnum == actionEnum and action.painterTool.hasFocus():
                return True, action
        return False, None

    def keyPressEvent(self, event) -> None:
        # 监听ESC键，当按下ESC键时，逐步取消编辑状态
        if event.key() == Qt.Key_Escape:
            #如果当前绘图工具处于获取焦点状态，则先取消其焦点状态
            if self.currentDrawActionEnum != DrawActionEnum.DrawNone and len(self.drawActions) > 0:
                hasFocus, focusedDrawAction = self.hasFocusByActionEnum(self.currentDrawActionEnum)
                if hasFocus:
                    focusedDrawAction.painterTool.clearFocus()
                    self.setFocus()
                    return

            # 如果当前绘图工具不在编辑状态，则本次按下Esc键会关掉绘图工具条
            if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
                self.clearDrawFlag()
            elif self.toolbar != None and self.toolbar.isVisible():
                self.completeDraw()
            else:
                self.destroyImage()

    def contextMenuEvent(self, event:QtGui.QContextMenuEvent):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(ScreenShotIcon.WHITE_BOARD, '标注', triggered=self.showCommandBar),
            Action(ScreenShotIcon.COPY, '复制', triggered=self.copyToClipboard),
            Action(ScreenShotIcon.CLICK_THROUGH, '鼠标穿透', triggered=self.clickThrough),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def checkDrawActionChange(self):
        # 如果中途切换了绘图工具，则关闭上一个绘图工具的编辑状态
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum != self.currentDrawActionEnum:
            self.setDrawActionEditable(self.drawActions[-1].actionEnum, False)
            self.clearInvalidDrawAction()
            self.createCustomInfoBar(f"绘图工具切换到 【{self.currentDrawActionEnum.value}】")

    def clearInvalidDrawAction(self):
        # 反向遍历self.drawActions，删掉无效的编辑行为
        for i in range(len(self.drawActions) - 1, -1, -1):
            if self.drawActions[i].actionEnum == DrawActionEnum.DrawText:
                if self.drawActions[i].IsShouldRemove():
                    self.drawActions[i].painterTool.close()
                    self.drawActions[i].painterTool.destroy()
                    self.drawActions.remove(self.drawActions[i])

    def addDrawAction(self, drawAction:DrawAction):
        self.drawActions.append(drawAction)

    def setDrawActionEditable(self, drawFlag:DrawActionEnum, isEdit:bool):
        for action in self.drawActions:
            if action.actionEnum == drawFlag:
                action.switchEditState(isEdit)

    def undo(self):
        self.createCustomInfoBar(f"【撤销】待支持")

    def clickThrough(self):
        self.parentWidget().setMouseThought(True)

    def redo(self):
        self.createCustomInfoBar(f"【重做】待支持")

    def destroyImage(self):
        self.parentWidget().close()

    # 得到最终绘制后的Pixmap
    def getFinalPixmap(self) -> QPixmap:
        # 经测试，这种方式截屏会有概率出现白边，推测是精度问题导致的，遂改成下面的实现
        # return self.grab()
        
        basePixmap = self.physicalPixmap.copy()
        painter = QPainter()
        painter.begin(basePixmap)
        for action in self.drawActions:
            widget:QWidget = action.painterTool
            painter.drawPixmap(widget.geometry(), widget.grab())
        painter.end()
        return basePixmap
        
    def copyToClipboard(self):
        finalPixmap = self.getFinalPixmap()
        QApplication.clipboard().setPixmap(finalPixmap)

    def drawText(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawText
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.IBeamCursor))

        # 恢复其它输入框的可编辑状态
        self.setDrawActionEditable(DrawActionEnum.DrawText, True)

    def useMarkerPen(self):
        self.createCustomInfoBar(f"【使用记号笔】待支持")

    def drawPolygonalLine(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawPolygonalLine
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawPolygonalLine:
            # 如果上一个绘图工具是绘制折线，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.setBeginDrawPolygonalLine()

    def drawPolygonal(self):
        self.createCustomInfoBar(f"【绘制多边形】待支持")

    def drawRectangle(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawRectangle
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawRectangle:
            # 如果上一个绘图工具是绘制矩形，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.setBeginDrawRectangle()

    def drawArrow(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawArrow
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawArrow:
            # 如果上一个绘图工具是绘制箭头，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.setBeginDrawArrow()

    def drawStar(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawStar
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawStar:
            # 如果上一个绘图工具是绘制五角星，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.setBeginDrawStar()

    def usePencil(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawLine
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setBeginDrawLine()

    def applyErase(self):
        self.currentDrawActionEnum = DrawActionEnum.ApplyErase
        self.checkDrawActionChange()
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.setBeginApplyErase()

    def clearDraw(self, isInit:bool=False):
        if not isInit:
            # 反向遍历self.drawActions，删除掉所有已有绘画行为对应的QWidget
            for drawAction in self.drawActions:
                drawAction.painterTool.close()
                drawAction.painterTool.destroy()

        self.drawActions: list[DrawAction] = []
        self.clearDrawFlag()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.currentDrawActionEnum == DrawActionEnum.DrawText:
                self.setBeginDrawText(pos)
            else:
                super().mousePressEvent(event)

    def focusInEvent(self, event) -> None:
        self.parentWidget().focused = True
        self.parentWidget().update()

    def focusOutEvent(self, event) -> None:
        # 获取鼠标居于屏幕上的位置点
        pos = QCursor.pos()

        # 计算绘图区和工具区的并集
        painterRect = QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(self.rect().bottomRight()))
        rects = [painterRect]
        if self.toolbar != None:
            toolbarRect = QRect(self.toolbar.mapToGlobal(self.toolbar.rect().topLeft()), self.toolbar.mapToGlobal(self.toolbar.rect().bottomRight()))
            rects.append(toolbarRect)
        region = QRegion()
        region.setRects(rects)

        # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
        if not region.contains(pos):
            self.parentWidget().focused = False
            self.parentWidget().update()

    def setBeginDrawLine(self):
        drawWidget = QPenLine(self)
        drawWidget.move(0, 0)
        drawWidget.resize(self.size())
        drawWidget.show()

        def ban(canEnabled):
            drawWidget.setEnabled(canEnabled)
            drawWidget.setAttribute(Qt.WA_TransparentForMouseEvents, not canEnabled)

        self.addDrawAction(DrawAction(DrawActionEnum.DrawLine, drawWidget, callback=lambda canEnabled: ban(canEnabled)))

    def setBeginDrawRectangle(self):
        # drawWidget = QPenRectangle(self)
        drawWidget = QPenRectangleBak(self)
        drawWidget.move(0, 0)
        drawWidget.resize(self.size())
        drawWidget.init()
        # drawWidget.initUI()
        # drawWidget.show()

        def ban(canEnabled):
            if hasattr(drawWidget, "ban"):
                drawWidget.ban()
            drawWidget.setEnabled(canEnabled)
            drawWidget.setAttribute(Qt.WA_TransparentForMouseEvents, not canEnabled)

        self.addDrawAction(DrawAction(DrawActionEnum.DrawRectangle, drawWidget, callback=lambda canEnabled: ban(canEnabled)))

    def setBeginDrawPolygonalLine(self):
        drawWidget = QPenPolygonalLine(self)
        drawWidget.move(0, 0)
        drawWidget.resize(self.size())
        drawWidget.show()

        def ban(canEnabled):
            drawWidget.setEnabled(canEnabled)
            drawWidget.setAttribute(Qt.WA_TransparentForMouseEvents, not canEnabled)

        self.addDrawAction(DrawAction(DrawActionEnum.DrawPolygonalLine, drawWidget, callback=lambda canEnabled: ban(canEnabled)))

    def setBeginDrawArrow(self):
        drawWidget = QPenArrow(self)
        drawWidget.move(0, 0)
        drawWidget.resize(self.size())
        drawWidget.show()

        def ban(canEnabled):
            if hasattr(drawWidget, "ban"):
                drawWidget.ban()
            drawWidget.setEnabled(canEnabled)
            drawWidget.setAttribute(Qt.WA_TransparentForMouseEvents, not canEnabled)

        self.addDrawAction(DrawAction(DrawActionEnum.DrawArrow, drawWidget, callback=lambda canEnabled: ban(canEnabled)))

    def setBeginDrawStar(self):
        drawWidget = QPenStar(self)
        drawWidget.move(0, 0)
        drawWidget.resize(self.size())
        drawWidget.show()

        def ban(canEnabled):
            if hasattr(drawWidget, "ban"):
                drawWidget.ban()
            drawWidget.setEnabled(canEnabled)
            drawWidget.setAttribute(Qt.WA_TransparentForMouseEvents, not canEnabled)

        self.addDrawAction(DrawAction(DrawActionEnum.DrawStar, drawWidget, callback=lambda canEnabled: ban(canEnabled)))

    def setBeginApplyErase(self):
        drawWidget = QPenErase(self)
        drawWidget.move(0, 0)
        drawWidget.resize(self.size())
        drawWidget.show()
        def ban(canEnabled):
            drawWidget.setEnabled(canEnabled)
            drawWidget.setAttribute(Qt.WA_TransparentForMouseEvents, not canEnabled)
        self.addDrawAction(DrawAction(DrawActionEnum.ApplyErase, drawWidget, callback=lambda canEnabled: ban(canEnabled)))

    def setBeginDrawText(self, pos:QPoint):
        textEdit = QAutoSizeTextEdit(self)
        textEdit.defaultShow(pos)
        textEdit.focusChanged.connect(self.textEditFocusChanged)
        self.addDrawAction(DrawAction(DrawActionEnum.DrawText, textEdit, callback=lambda canEnabled: textEdit.setEnabled(canEnabled)))        

    def textEditFocusChanged(self, value):
        if value < 0:
            self.clearInvalidDrawAction()
            self.focusOutEvent(None)

    def clearDrawFlag(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        for action in self.drawActions:
            action.switchEditState(False)

        if self.actionGroup != None:
            for action in self.actionGroup.actions():
                action.setChecked(False)

        if len(self.drawActions) > 0:
            self.createCustomInfoBar("退出绘图")

    def createCustomInfoBar(self, text:str):
        w = InfoBar.new(
            icon=ScreenShotIcon.GUIDE,
            title='',
            content=text,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.BOTTOM,
            duration=1000,
            parent=self
        )
        # w.iconWidget.setFixedSize(QSize(40, 40))
        w.setCustomBackgroundColor('white', '#202020')
