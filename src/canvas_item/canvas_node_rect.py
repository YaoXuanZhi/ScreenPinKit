import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
from collections import OrderedDict

class CanvasROIItem(QGraphicsEllipseItem):
    def __init__(self, id:int, hoverCursor:QCursor = None, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.id = id
        self.lastCursor = None
        if hoverCursor == None:
            hoverCursor = Qt.CursorShape.SizeAllCursor
        self.interfaceCursor = hoverCursor
        self.radius = 10

        pen = QPen()
        pen.setColor(Qt.lightGray)
        pen.setWidth(1)
        self.setPen(pen)
        # self.setBrush(QBrush(Qt.NoBrush))
        self.setBrush(Qt.blue)
        self.setRect(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
   
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

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:CanvasNodeRect = self.parentItem()
            parentItem.roiManager.removeROI(self.id)
        return super().mouseDoubleClickEvent(event)

class CanvasROIManager():
    def __init__(self, parent: QGraphicsItem) -> None:
        self.parent = parent
        self.itemsOrderDict = OrderedDict()
        self.lastId = 0
        pass

    def addROI(self, pos:QPointF, hoverCursor:QCursor = None):
        ''''添加操作点'''
        self.lastId += 1
        id = self.lastId
        roiItem = CanvasROIItem(id, hoverCursor, self.parent)
        self.itemsOrderDict[id] = roiItem
        roiItem.setPos(pos)

    def removeROI(self, id:int):
        ''''移除操作点'''
        roiItem = self.itemsOrderDict.pop(id)
        self.parent.scene().removeItem(roiItem)

class CanvasNodeRect(QGraphicsRectItem):
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.edge_size = 10.0
        self._padding = 4.0

        self.roiManager = CanvasROIManager(self)

        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(self.boundingRect(), self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.roiManager.addROI(event.pos())
        return super().mouseDoubleClickEvent(event)