import typing
from enum import Enum
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
import sys

class EnumPosType(Enum):
    ControllerPosTL = 1
    ControllerPosTC = 2
    ControllerPosTR = 3
    ControllerPosRC = 4
    ControllerPosBR = 5
    ControllerPosBC = 6
    ControllerPosBL = 7
    ControllerPosLC = 8

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

    def getControllerPosition(self, rect:QRectF, radius, posType:EnumPosType):
        if posType == EnumPosType.ControllerPosTL:
            # 左上角
            return rect.topLeft() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosTC:
            # 顶端居中
            return (rect.topLeft() + rect.topRight()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosTR:
            # 右上角
            return rect.topRight() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosRC:
            # 右侧居中
            return (rect.topRight() + rect.bottomRight()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosBL:
            # 左下角
            return rect.bottomLeft() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosBC:
            # 底端居中
            return (rect.bottomLeft() + rect.bottomRight()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosBR:
            # 右下角
            return rect.bottomRight() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosLC:
            # 左侧居中
            return (rect.topLeft() + rect.bottomLeft()) / 2 - QPointF(radius, radius)

    def setRectWrapper(self, attachRect:QRectF, posType:EnumPosType, radius:float, size:QSizeF):
        self.posType = posType
        pos = self.getControllerPosition(attachRect, radius, posType)
        self.setRect(QRectF(pos, size))

    def resetPosition(self, attachRect:QRectF, radius:float, size:QSizeF):
        pos = self.getControllerPosition(attachRect, radius, self.posType)
        self.setRect(QRectF(pos, size))

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        parentItem.updateEdge(self.posType, event.pos())

class CanvasEditableFrame(QGraphicsRectItem):
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)

        self.m_margin = 20.0
        self.m_borderWidth = 5
        self.m_padding = 20.0

        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

        self.initUI()

    def getMarginRect(self) -> QRectF:
        return self.rect()

    def getPaddingRect(self) -> QRectF:
        contentRect = self.getContentRect()
        offset = self.m_padding
        return contentRect + QMarginsF(offset, offset, offset, offset)

    def getBorderRect(self) -> QRectF:
        contentRect = self.getContentRect()
        offset = self.m_borderWidth + self.m_padding
        return contentRect + QMarginsF(offset, offset, offset, offset)

    def getContentRect(self) -> QRectF:
        contentRect = self.rect()
        offset = self.m_margin + self.m_borderWidth + self.m_padding
        return contentRect - QMarginsF(offset, offset, offset, offset)

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.lastCursor = None
        self.shapePath = QPainterPath()

        # self.initControllers()

    def initControllers(self):
        if not hasattr(self, "controllers"):
            self.controllers:list[CanvasEllipseItem] = []

        # rect = self.rect()
        rect = self.getBorderRect()
        radius = 8
        size = QSizeF(radius*2, radius*2)
        posTypes = [
            [EnumPosType.ControllerPosTL, Qt.CursorShape.SizeFDiagCursor], 
            [EnumPosType.ControllerPosTC, Qt.CursorShape.SizeVerCursor], 
            [EnumPosType.ControllerPosTR, Qt.CursorShape.SizeBDiagCursor], 
            [EnumPosType.ControllerPosRC, Qt.CursorShape.SizeHorCursor], 
            [EnumPosType.ControllerPosBR, Qt.CursorShape.SizeFDiagCursor], 
            [EnumPosType.ControllerPosBC, Qt.CursorShape.SizeVerCursor], 
            [EnumPosType.ControllerPosBL, Qt.CursorShape.SizeBDiagCursor], 
            [EnumPosType.ControllerPosLC, Qt.CursorShape.SizeHorCursor],
            ]

        if len(self.controllers) == 0:
            for info in posTypes:
                controller = CanvasEllipseItem(info[-1], self)
                controller.setRectWrapper(rect, info[0], radius, size)
                self.controllers.append(controller)
        else:
            for controller in self.controllers:
                controller.resetPosition(rect, radius, size)
                if not controller.isVisible():
                    controller.show()

    def hideControllers(self):
        for controller in self.controllers:
            if controller.isVisible():
                controller.hide()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        self.initControllers()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if not self.isSelected():
            self.hideControllers()
        return super().focusOutEvent(event)

    def updateEdge(self, currentPosType, localPos:QPointF):
        offset = self.m_margin + self.m_borderWidth / 2
        lastRect = self.rect()
        newRect = lastRect.adjusted(0, 0, 0, 0)
        if currentPosType == EnumPosType.ControllerPosTL:
            localPos += QPointF(-offset, -offset)
            newRect.setTopLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosTC:
            localPos += QPointF(0, -offset)
            newRect.setTop(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosTR:
            localPos += QPointF(offset, -offset)
            newRect.setTopRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosRC:
            localPos += QPointF(offset, 0)
            newRect.setRight(localPos.x())
        elif currentPosType == EnumPosType.ControllerPosBR:
            localPos += QPointF(offset, offset)
            newRect.setBottomRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosBC:
            localPos += QPointF(0, offset)
            newRect.setBottom(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosBL:
            localPos += QPointF(-offset, offset)
            newRect.setBottomLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosLC:
            localPos = localPos - QPointF(offset, offset)
            newRect.setLeft(localPos.x())

        self.setRect(newRect)
        self.initControllers()

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        self.shapePath.clear()
        if self.isSelected():
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            for controller in self.controllers:
                rects.append(controller.boundingRect().toRect())
            region.setRects(rects)
            self.shapePath.addRegion(region)
        else:
            fullRect = self.boundingRect()
            selectRegion = QRegion(fullRect.toRect())
            subRect:QRectF = self.boundingRect() - QMarginsF(self.m_padding, self.m_padding, self.m_padding, self.m_padding)
            finalRegion = selectRegion.subtracted(QRegion(subRect.toRect()))
            self.shapePath.addRegion(finalRegion)
        return self.shapePath

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        boundingRect = self.rect()
        borderRect:QRect = self.getBorderRect()
        contentRect = self.getContentRect()

        boundingColor = QColor(0, 0, 125)
        borderColor = QColor(255, 255, 153)
        contentColor = QColor(253, 203, 151)

        painter.setPen(boundingColor)
        painter.drawRect(boundingRect)
        painter.setPen(Qt.white)
        painter.drawText(boundingRect, Qt.AlignTop | Qt.AlignLeft, "margin")

        painter.setPen(QPen(borderColor, self.m_borderWidth))
        painter.drawRect(borderRect)
        painter.setPen(Qt.white)
        borderRect.adjust(self.m_borderWidth, self.m_borderWidth, -self.m_borderWidth, -self.m_borderWidth)
        painter.drawText(borderRect, Qt.AlignTop | Qt.AlignLeft, "border")

        painter.setPen(contentColor)
        painter.drawRect(contentRect)
        painter.setPen(Qt.white)
        painter.drawText(contentRect, Qt.AlignTop | Qt.AlignLeft, "content")

        painter.restore()