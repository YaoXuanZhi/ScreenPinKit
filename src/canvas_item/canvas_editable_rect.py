import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QStyleOptionGraphicsItem, QWidget
import sys

class CanvasEllipseItem(QGraphicsEllipseItem):
    def __init__(self, interfaceCursor:QCursor, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.lastCursor = None
        self.interfaceCursor = interfaceCursor

        pen = QPen()
        pen.setColor(Qt.lightGray)
        pen.setWidth(1)
        self.setPen(pen)
        self.setBrush(Qt.blue)
   
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.interfaceCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        if self.isSelected():
            option.state = QStyle.StateFlag.State_None
        return super().paint(painter, option, widget)

class CanvasEditableRect(QGraphicsRectItem):
    ControllerPosTL = 1
    ControllerPosTC = 2
    ControllerPosTR = 3
    ControllerPosRC = 4
    ControllerPosBR = 5
    ControllerPosBC = 6
    ControllerPosBL = 7
    ControllerPosLC = 8

    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)

        self._pen_default = QPen(Qt.white)
        # self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.edge_size = 10.0
        self._padding = 4.0

        self.initUI()

    def getControllerPosition(self, rect:QRectF, radius, posType:int):
        if posType == self.ControllerPosTL:
            # 左上角
            return rect.topLeft() - QPointF(radius, radius)
        elif posType == self.ControllerPosTC:
            # 顶端居中
            return (rect.topLeft() + rect.topRight()) / 2 - QPointF(radius, radius)
        elif posType == self.ControllerPosTR:
            # 右上角
            return rect.topRight() - QPointF(radius, radius)
        elif posType == self.ControllerPosRC:
            # 右侧居中
            return (rect.topRight() + rect.bottomRight()) / 2 - QPointF(radius, radius)
        elif posType == self.ControllerPosBL:
            # 左下角
            return rect.bottomLeft() - QPointF(radius, radius)
        elif posType == self.ControllerPosBC:
            # 底端居中
            return (rect.bottomLeft() + rect.bottomRight()) / 2 - QPointF(radius, radius)
        elif posType == self.ControllerPosBR:
            # 右下角
            return rect.bottomRight() - QPointF(radius, radius)
        elif posType == self.ControllerPosLC:
            # 左侧居中
            return (rect.topLeft() + rect.bottomLeft()) / 2 - QPointF(radius, radius)

    def initControllers(self):
        self.controllers:list[CanvasEllipseItem] = []
        rect = self.boundingRect()
        radius = 5
        size = QSizeF(radius*2, radius*2)
        posTypes = [
            [self.ControllerPosTL, Qt.CursorShape.SizeFDiagCursor], 
            [self.ControllerPosTC, Qt.CursorShape.SizeVerCursor], 
            [self.ControllerPosTR, Qt.CursorShape.SizeBDiagCursor], 
            [self.ControllerPosRC, Qt.CursorShape.SizeHorCursor], 
            [self.ControllerPosBR, Qt.CursorShape.SizeFDiagCursor], 
            [self.ControllerPosBC, Qt.CursorShape.SizeVerCursor], 
            [self.ControllerPosBL, Qt.CursorShape.SizeBDiagCursor], 
            [self.ControllerPosLC, Qt.CursorShape.SizeHorCursor],
            ]

        for info in posTypes:
            pos = self.getControllerPosition(rect, radius, info[0])
            controller = CanvasEllipseItem(info[-1], self)
            controller.setRect(QRectF(pos, size))
            self.controllers.append(controller)

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.lastCursor = None

        self.initControllers()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        print(f" {__class__.__name__}:{sys._getframe().f_code.co_name} ====> ")
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        print(f" {__class__.__name__}:{sys._getframe().f_code.co_name} ====> ")
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        # outline
        path_outline = QPainterPath()
        # path_outline.addRoundedRect(self.boundingRect(), self.edge_size, self.edge_size)
        path_outline.addRect(self.boundingRect())
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())