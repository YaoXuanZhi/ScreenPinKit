from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
from collections import OrderedDict

class CanvasROIItem(QGraphicsEllipseItem):
    def __init__(self, id:int, hoverCursor:QCursor = None, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemSendsGeometryChanges)
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
            parentItem:ResizableRectItem = self.parentItem()
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

class ResizableRectItem(QGraphicsItemGroup):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        self.rect_item = QGraphicsRectItem(x, y, w, h, self)
        self.rect_item.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        self.rect_item.setBrush(QBrush(QColor(255, 255, 255, 0)))
        self.rect_item.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.rect_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.rect_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
        self.rect_item.setAcceptHoverEvents(True)
        self.resize_handles = []
        self.create_resize_handles()

    def create_resize_handles(self):
        self.rect_item.roiMgr = CanvasROIManager(self.rect_item)
        self.rect_item.roiMgr.addROI(self.rect_item.rect().topLeft())
        self.rect_item.roiMgr.addROI(self.rect_item.rect().topRight())
        self.rect_item.roiMgr.addROI(self.rect_item.rect().bottomLeft())
        self.rect_item.roiMgr.addROI(self.rect_item.rect().bottomRight())

    def create_resize_handlesBak(self):
        radius = 10
        for i in range(4):
            handle = QGraphicsEllipseItem(-radius, -radius, radius*2, radius*2, self.rect_item)
            handle.setBrush(QBrush(QColor(255, 255, 255, 0)))
            handle.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            handle.setFlag(QGraphicsItem.ItemIsMovable, True)
            handle.setFlag(QGraphicsItem.ItemIsSelectable, True)
            handle.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            handle.setAcceptHoverEvents(True)
            self.resize_handles.append(handle)

        self.resize_handles[0].setPos(self.rect_item.rect().topLeft())
        self.resize_handles[1].setPos(self.rect_item.rect().topRight())
        self.resize_handles[2].setPos(self.rect_item.rect().bottomRight())
        self.resize_handles[3].setPos(self.rect_item.rect().bottomLeft())

    def boundingRect(self):
        return self.rect_item.boundingRect()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(255, 255, 255, 0)))
        painter.drawRect(self.rect_item.rect())

    # def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     if event.button() == Qt.MouseButton.RightButton:
    #         lastScale = self.rect_item.scale()
    #         self.rect_item.setScale(lastScale + 0.1)
    #     elif event.button() == Qt.MouseButton.LeftButton:
    #         lastRotation = self.rect_item.rotation()
    #         self.rect_item.setRotation(lastRotation + 10)
    #     return super().mouseDoubleClickEvent(event)
