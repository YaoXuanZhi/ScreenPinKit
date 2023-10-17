# https://blog.csdn.net/qq_33659478/article/details/126646020
# https://blog.csdn.net/xiaonuo911teamo/article/details/106129696
# https://blog.csdn.net/xiaonuo911teamo/article/details/106075647
import math
from enum import Enum
from collections import OrderedDict, deque
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget

class EnumPosType(Enum):
    ControllerPosTL = "左上角"
    ControllerPosTC = "顶部居中"
    ControllerPosTR = "右上角"
    ControllerPosRC = "右侧居中"
    ControllerPosBR = "右下角"
    ControllerPosBC = "底部居中"
    ControllerPosBL = "左下角"
    ControllerPosLC = "左侧居中"
    ControllerPosTT = "顶部悬浮"

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

class CanvasEllipseItem(CanvasBaseItem):
    def __init__(self, interfaceCursor:QCursor, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.lastCursor = None
        self.interfaceCursor = interfaceCursor

        pen = QPen()
        pen.setColor(Qt.lightGray)
        pen.setWidth(1)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.NoBrush))
        # self.setBrush(Qt.blue)
   
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
        elif posType == EnumPosType.ControllerPosTT:
            # 顶部悬浮
            hoverDistance = 30
            return (rect.topLeft() + rect.topRight()) / 2 - QPointF(radius, radius + hoverDistance)

    def setRectWrapper(self, attachRect:QRectF, posType:EnumPosType, radius:float, size:QSizeF):
        self.posType = posType
        pos = self.getControllerPosition(attachRect, radius, posType)
        self.setRect(QRectF(pos, size))

    def resetPosition(self, attachRect:QRectF, radius:float, size:QSizeF):
        pos = self.getControllerPosition(attachRect, radius, self.posType)
        self.setRect(QRectF(pos, size))

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.mouseMoveRotateOperator(event.scenePos(), event.pos())
            return
        parentItem.updateEdge(self.posType, event.pos())

    def focusInEvent(self, event: QFocusEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        parentItem.focusInEvent(event)
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        parentItem.focusOutEvent(event)
        return super().focusOutEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.startRotate(event.pos())
        else:
            parentItem.startResize(event.pos())
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.endRotate(event.pos())
        else:
            parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

class CanvasEditableFrame(QGraphicsRectItem):
    PI = 3.14159265358979

    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)

        self.radius = 8
        self.m_borderWidth = 1

        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.lastCursor = None
        self.shapePath = QPainterPath()

        self.m_pressPos = QPointF() # 本地坐标点击的点

    def initControllers(self):
        if not hasattr(self, "controllers"):
            self.controllers:list[CanvasEllipseItem] = []

        rect = self.boundingRect()
        size = QSizeF(self.radius*2, self.radius*2)
        posTypes = [
            [EnumPosType.ControllerPosTL, Qt.CursorShape.SizeFDiagCursor], 
            [EnumPosType.ControllerPosTC, Qt.CursorShape.SizeVerCursor], 
            [EnumPosType.ControllerPosTR, Qt.CursorShape.SizeBDiagCursor], 
            [EnumPosType.ControllerPosRC, Qt.CursorShape.SizeHorCursor], 
            [EnumPosType.ControllerPosBR, Qt.CursorShape.SizeFDiagCursor], 
            [EnumPosType.ControllerPosBC, Qt.CursorShape.SizeVerCursor], 
            [EnumPosType.ControllerPosBL, Qt.CursorShape.SizeBDiagCursor], 
            [EnumPosType.ControllerPosLC, Qt.CursorShape.SizeHorCursor],
            [EnumPosType.ControllerPosTT, Qt.CursorShape.PointingHandCursor],
            ]

        if len(self.controllers) == 0:
            for info in posTypes:
                controller = CanvasEllipseItem(info[-1], self)
                controller.setRectWrapper(rect, info[0], self.radius, size)
                self.controllers.append(controller)
        else:
            for controller in self.controllers:
                controller.resetPosition(rect, self.radius, size)
                if not controller.isVisible():
                    controller.show()

    def hideControllers(self):
        for controller in self.controllers:
            if controller.isVisible():
                controller.hide()

    def mouseMoveRotateOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        p1 = QLineF(self.originPos, self.m_pressPos)
        p2 = QLineF(self.originPos, localPos)

        dRotateAngle = p2.angleTo(p1)

        dCurAngle = self.rotation() + dRotateAngle
        while dCurAngle > 360.0:
            dCurAngle -= 360.0
        self.setRotation(dCurAngle)
        self.update()

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
        if self.hasFocusWrapper():
            self.initControllers()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        scenePos = self.gtCurrentScenePos()

        # 计算绘图区和工具区的并集
        rects = [self.sceneBoundingRect().toRect()]
        for controller in self.controllers:
            rects.append(controller.sceneBoundingRect().toRect())
        region = QRegion()
        region.setRects(rects)

        # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
        if not region.contains(scenePos):
            self.hideControllers()

    def gtCurrentScenePos(self):
        screenPos = self.cursor().pos()
        view = self.scene().views()[0]
        widgetPos = view.mapFromGlobal(screenPos)
        scenePos = view.mapToScene(widgetPos)
        return scenePos.toPoint()

    def updateEdge(self, currentPosType, localPos:QPointF):
        offset = self.m_borderWidth / 2
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

    def hasFocusWrapper(self):
        # if self.hasFocus() or self.isSelected():
        if self.hasFocus():
            return True
        else:
            if hasattr(self, 'controllers'):
                for controller in self.controllers:
                    if controller.hasFocus():
                        return True
        return False

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        self.shapePath.clear()
        if self.hasFocusWrapper():
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            if hasattr(self, 'controllers'):
                for controller in self.controllers:
                    rects.append(controller.boundingRect().toRect())
            region.setRects(rects)
            self.shapePath.addRegion(region)
        else:
            fullRect = self.boundingRect()
            selectRegion = QRegion(fullRect.toRect())
            offset = self.m_borderWidth
            subRect:QRectF = self.boundingRect() - QMarginsF(offset, offset, offset, offset)
            finalRegion = selectRegion.subtracted(QRegion(subRect.toRect()))
            self.shapePath.addRegion(finalRegion)
        return self.shapePath

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        boundingRect = self.rect()
        boundingColor = QColor(0, 0, 125)

        # painter.setPen(boundingColor)
        painter.setPen(self.m_penDefault if not self.hasFocusWrapper() else self.m_penSelected)
        painter.drawRect(boundingRect)
        painter.setPen(Qt.white)

        painter.restore()

    def startResize(self, localPos:QPointF) -> None:
        pass

    def endResize(self, localPos:QPointF) -> None:
        # 解决有旋转角度的矩形，拉伸之后，再次旋转，旋转中心该仍然为之前坐标，手动设置为中心，会产生漂移的问题
        rect = self.rect()
        angle = math.radians(self.rotation())

        p1 = rect.center()
        origin = self.transformOriginPoint()
        p2 = QPointF(0, 0)

        p2.setX(origin.x() + math.cos(angle)*(p1.x() - origin.x()) - math.sin(angle)*(p1.y() - origin.y()))
        p2.setY(origin.y() + math.sin(angle)*(p1.x() - origin.x()) + math.cos(angle)*(p1.y() - origin.y()))

        diff:QPointF = p1 - p2

        self.setRect(rect.adjusted(-diff.x(), -diff.y(), -diff.x(), -diff.y()))
        self.setTransformOriginPoint(self.rect().center())

        self.initControllers()

    def startRotate(self, localPos:QPointF) -> None:
        self.originPos = self.boundingRect().center()
        self.setTransformOriginPoint(self.originPos)
        self.m_pressPos = localPos
    
    def endRotate(self, localPos:QPointF) -> None:
        pass

class CanvasROI(CanvasBaseItem):
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
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.isMoving:
            parentItem:CanvasEditablePath = self.parentItem()
            localPos = self.mapToItem(parentItem, self.rect().center())
            parentItem.movePointById(self.id, localPos)

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
            parentItem.removePoint(self.id)
        return super().mouseDoubleClickEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        super().paint(painter, option, widget)

        painter.save()
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPixelSize(16)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, str(self.id))
        painter.restore()

class CanvasEditablePath(QGraphicsObject):
    def __init__(self, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)

        self.radius = 8
        self.m_borderWidth = 1

        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.itemOrderDict = OrderedDict()
        self.lastCursorDeque = deque()
        self.hoverCursor = Qt.SizeAllCursor

        self.polygon = QPolygonF()
        self.shapePath = QPainterPath()

    def addPoint(self, point:QPointF, cursor:QCursor = Qt.SizeAllCursor) -> CanvasROI:
        id = self.polygon.count()
        self.polygon.append(point)

        roiItem = CanvasROI(cursor, id, self)
        rect = QRectF(QPointF(0, 0), QSizeF(16, 16))
        rect.moveCenter(point)
        roiItem.setRect(rect)

        self.itemOrderDict[id] = roiItem
        return roiItem

    def removePoint(self, id:int):
        lastRemoveKey = -1
        for key in self.itemOrderDict.keys():
            value = self.itemOrderDict[key]
            roiItem:CanvasROI = value
            if roiItem.id == id:
                lastRemoveKey = key 
            elif roiItem.id > id:
                roiItem.id -= 1
                roiItem.update()

        self.polygon.remove(id)
        removeROIItem = self.itemOrderDict.pop(lastRemoveKey)
        self.scene().removeItem(removeROIItem)

    def movePointById(self, id:int, localPos:QPointF):
        self.prepareGeometryChange()
        self.polygon.replace(id, localPos)
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        boundingRect = self.boundingRect()

        painter.setPen(self.m_penDefault if not self.hasFocusWrapper() else self.m_penSelected)
        painter.drawPolygon(self.polygon)

        if self.hasFocusWrapper():
            painter.setPen(QPen(Qt.yellow, 1, Qt.DashLine))
            painter.drawRect(boundingRect)

        painter.restore()

    def hasFocusWrapper(self):
        # if self.hasFocus() or self.isSelected():
        if self.hasFocus():
            return True
        else:
            for value in self.itemOrderDict.values():
                roiItem:CanvasROI = value
                if roiItem.hasFocus():
                    return True
        return False

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        self.shapePath.clear()
        if self.hasFocusWrapper():
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            for value in self.itemOrderDict.values():
                roiItem:CanvasROI = value
                rects.append(roiItem.boundingRect().toRect())
            region.setRects(rects)
            self.shapePath.addRegion(region)
        else:
            self.shapePath.addPolygon(self.polygon)
        return self.shapePath

    def boundingRect(self) -> QRectF:
        return self.polygon.boundingRect()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursorDeque.append(self.cursor())
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if len(self.lastCursorDeque) > 0:
            lastCursor = self.lastCursorDeque.pop()
            self.setCursor(lastCursor)
        return super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.addPoint(event.pos(), Qt.CursorShape.SizeBDiagCursor)
        return super().mouseDoubleClickEvent(event)