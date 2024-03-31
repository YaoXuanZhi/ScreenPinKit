import math
from enum import Enum
from collections import OrderedDict, deque
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget

class CanvasBaseItem(QGraphicsObject):
    def __init__(self, parent: QGraphicsItem) -> None:
        super().__init__(parent)

        self.m_pen = QPen(Qt.yellow)
        self.m_brush = QBrush(Qt.red)

        self.m_rect = QRectF()
        self.m_boundingRect = QRectF()

    def setPen(self, pen:QPen):
        if self.m_pen == pen:
            return
        self.prepareGeometryChange()
        self.m_pen = pen
        self.m_boundingRect = QRectF()
        self.update()

    def setBrush(self, brush:QBrush):
        if self.m_brush == brush:
            return
        self.m_brush = brush
        self.update()

    def setBrush(self, brush:QBrush):
        self.m_brush = brush

    def rect(self) -> QRectF:
        return self.m_rect

    def setRect(self, rect:QRectF):
        if self.m_rect == rect:
            return

        self.prepareGeometryChange()
        self.m_rect = rect
        self.m_boundingRect = QRectF()
        self.update()

    def boundingRect(self) -> QRectF:
        if(self.m_boundingRect.isNull()):
            self.m_boundingRect = self.m_rect
        return self.m_boundingRect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        if self.m_rect.isNull():
            return path
        path.addEllipse(self.m_rect)
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        painter.setPen(self.m_pen)
        painter.setBrush(self.m_brush)

        painter.drawEllipse(self.m_rect)

        painter.restore()

# class CanvasROI(CanvasBaseItem):
# class CanvasROI(QGraphicsRectItem):
class CanvasROI(QGraphicsEllipseItem):
    def __init__(self, hoverCursor:QCursor, id:int, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.hoverCursor = hoverCursor
        self.id = id
        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.lastCursorDeque = deque()
        self.isMoving = False

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = False
        # parentItem:CanvasEditableFrame = self.parentItem()
        # parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.isMoving:
            parentItem:CanvasEditablePath = self.parentItem()
        #     localPos = self.mapToItem(parentItem, self.rect().center())
        #     parentItem.movePointById(self, localPos)
            parentItem.rebuild()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:CanvasEditablePath = self.parentItem()
            parentItem.removePoint(self)
        return super().mouseDoubleClickEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        super().paint(painter, option, widget)
        parentItem:CanvasEditablePath = self.parentItem()
        # if not hasattr(parentItem, "canRoiItemEditable") or not parentItem.canRoiItemEditable:
        #     return

        painter.save()
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPixelSize(12)
        painter.setFont(font)
        index = parentItem.roiItemList.index(self)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{index}/{self.id}")
        painter.restore()