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

    def setCustomCursor(self) -> QCursor:
        parentItem:CanvasEditableFrame = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            self.setCursor(self.interfaceCursor)
            return
        elif self.posType == EnumPosType.ControllerPosRC:
            pixmap = QPixmap("images/horizontal resize.png")
        elif self.posType == EnumPosType.ControllerPosLC:
            pixmap = QPixmap("images/horizontal resize.png")
        elif self.posType == EnumPosType.ControllerPosTC:
            pixmap = QPixmap("images/vertical resize.png")
        elif self.posType == EnumPosType.ControllerPosBC:
            pixmap = QPixmap("images/vertical resize.png")
        elif self.posType == EnumPosType.ControllerPosTL:
            pixmap = QPixmap("images/diagonal resize 1.png")
        elif self.posType == EnumPosType.ControllerPosBR:
            pixmap = QPixmap("images/diagonal resize 1.png")
        elif self.posType == EnumPosType.ControllerPosTR:
            pixmap = QPixmap("images/diagonal resize 2.png")
        elif self.posType == EnumPosType.ControllerPosBL:
            pixmap = QPixmap("images/diagonal resize 2.png")
        else:
            pixmap = QPixmap("images/location select.png")

        pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        transform = parentItem.transform()
        transform.rotate(parentItem.rotation())
        finalPixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        newFinal = QCursor(finalPixmap, -1, -1)
        self.setCursor(newFinal)
   
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        # self.setCursor(self.interfaceCursor)
        self.setCustomCursor()
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
        parentItem.updateEdge(self.posType, event.pos().toPoint())

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

    def updateEdge(self, currentPosType, localPos:QPoint):
        offset = self.m_borderWidth / 2
        lastRect = self.rect()
        newRect = lastRect.adjusted(0, 0, 0, 0)
        if currentPosType == EnumPosType.ControllerPosTL:
            localPos += QPoint(-offset, -offset)
            newRect.setTopLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosTC:
            localPos += QPoint(0, -offset)
            newRect.setTop(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosTR:
            localPos += QPoint(offset, -offset)
            newRect.setTopRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosRC:
            localPos += QPoint(offset, 0)
            newRect.setRight(localPos.x())
        elif currentPosType == EnumPosType.ControllerPosBR:
            localPos += QPoint(offset, offset)
            newRect.setBottomRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosBC:
            localPos += QPoint(0, offset)
            newRect.setBottom(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosBL:
            localPos += QPoint(-offset, offset)
            newRect.setBottomLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosLC:
            localPos = localPos - QPoint(offset, offset)
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
        self.setTransformOriginPoint(p1-diff)

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
        parentItem:CanvasEditableFrame = self.parentItem()
        parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.isMoving:
            parentItem:CanvasEditablePath = self.parentItem()
            localPos = self.mapToItem(parentItem, self.rect().center())
            parentItem.movePointById(self, localPos)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        parentItem.focusInEvent(event)
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        parentItem:CanvasEditableFrame = self.parentItem()
        parentItem.focusOutEvent(event)
        return super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:CanvasEditablePath = self.parentItem()
            parentItem.removePoint(self)
        return super().mouseDoubleClickEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        super().paint(painter, option, widget)

        painter.save()
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPixelSize(12)
        painter.setFont(font)
        parentItem:CanvasEditablePath = self.parentItem()
        index = parentItem.roiItemList.index(self)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{index}/{self.id}")
        painter.restore()

class CanvasEditablePath(QGraphicsObject):
    def __init__(self, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)

        self.radius = 8
        self.roiRadius = 14
        self.m_borderWidth = 4

        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)
        self.m_instId = 0

        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.lastCursorDeque = deque()
        self.hoverCursor = Qt.SizeAllCursor

        self.roiItemList:list[CanvasROI] = []
        self.polygon = QPolygonF()
        self.shapePath = QPainterPath()

    def addPoint(self, point:QPointF, cursor:QCursor = Qt.PointingHandCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId
        self.polygon.append(point)

        roiItem = CanvasROI(cursor, id, self)
        rect = QRectF(QPointF(0, 0), QSizeF(self.roiRadius*2, self.roiRadius*2))
        rect.moveCenter(point)
        roiItem.setRect(rect)

        self.roiItemList.append(roiItem)
        return roiItem

    def insertPoint(self, insertIndex:int, point:QPointF, cursor:QCursor = Qt.SizeAllCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId

        self.polygon.insert(insertIndex, point)

        roiItem = CanvasROI(cursor, id, self)
        rect = QRectF(QPointF(0, 0), QSizeF(self.roiRadius*2, self.roiRadius*2))
        rect.moveCenter(point)
        roiItem.setRect(rect)

        self.roiItemList.insert(insertIndex, roiItem)
        self.initControllers()
        return roiItem

    def removePoint(self, roiItem:CanvasROI):
        index = self.roiItemList.index(roiItem)
        self.polygon.remove(index)
        self.roiItemList.remove(roiItem)
        self.scene().removeItem(roiItem)
        self.endResize(None)
        self.focusOutEvent(None)

    def movePointById(self, roiItem:CanvasROI, localPos:QPointF):
        index = self.roiItemList.index(roiItem)
        self.prepareGeometryChange()
        self.polygon.replace(index, localPos)
        self.update()
        self.initControllers()

    def moveRoiItemsBy(self, offset:QPointF):
        '''将所有的roiItem都移动一下'''
        for i in range(0, self.polygon.count()):
            roiItem:CanvasROI = self.roiItemList[i]
            roiItem.moveBy(-offset.x(), -offset.y())
            oldPos = self.polygon.at(i)
            newPos = oldPos - offset
            self.polygon.replace(i, newPos)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        painter.setPen(self.m_penDefault if not self.hasFocusWrapper() else self.m_penSelected)
        painter.drawPolygon(self.polygon)

        if self.hasFocusWrapper():
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.polygon.boundingRect())

            painter.setPen(QPen(Qt.yellow, 1, Qt.DashLine))
            rect = self.getStretchableRect()
            painter.drawRect(rect)

        pen = QPen(Qt.green, 1, Qt.DashLine)
        pen.setDashPattern([10, 5])
        painter.setPen(pen)
        painter.drawPath(self.shapePath)

        painter.restore()

    def hasFocusWrapper(self):
        # if self.hasFocus() or self.isSelected():
        if self.hasFocus():
            return True
        else:
            for value in self.roiItemList:
                roiItem:CanvasROI = value
                if roiItem.hasFocus():
                    return True

            if hasattr(self, 'controllers'):
                for controller in self.controllers:
                    if controller.hasFocus():
                        return True
        return False

    def calcOffset(self, startPoint:QPointF, endPoint:QPointF, dbRadious:float) -> QPointF:
        '''计算线段法向量，并且将其长度设为圆的半径，计算它们的偏移量'''
        v = QLineF(startPoint, endPoint)
        n = v.normalVector()
        n.setLength(dbRadious)
        return n.p1() - n.p2()

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        if self.hasFocusWrapper():
            selectPath = QPainterPath()
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            for value in self.roiItemList:
                roiItem:CanvasROI = value
                rects.append(roiItem.boundingRect().toRect())
            region.setRects(rects)
            selectPath.addRegion(region)
            return selectPath

        return self.shapePath

    def foreachPolygonSegments(self, callback:callable):
        for i in range(0, self.polygon.count()):
            points = []
            polygonPath = QPainterPath()
            startIndex = i
            endIndex = i + 1
            endIndex %= self.polygon.count()
            startPoint = self.polygon.at(startIndex)
            endPoint = self.polygon.at(endIndex)

            offset = self.calcOffset(startPoint, endPoint, self.roiRadius)

            points.append(startPoint - offset)
            points.append(startPoint + offset)
            points.append(endPoint + offset)
            points.append(endPoint - offset)

            polygonPath.addPolygon(QPolygonF(points))
            polygonPath.closeSubpath()
            if callback(startIndex, endIndex, polygonPath):
                break

            if self.polygon.count() < 3:
                break

    def boundingRect(self) -> QRectF:
        self.shapePath.clear()

        def appendShapePath(startIndex, endIndex, polygonPath):
            self.shapePath.addPath(polygonPath)
            return False

        self.foreachPolygonSegments(appendShapePath)
        return self.shapePath.boundingRect()


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

            def hitTest(startIndex, endIndex, polygonPath:QPainterPath):
                if polygonPath.contains(event.pos()):
                    self.insertPoint(endIndex, event.pos(), Qt.CursorShape.SizeBDiagCursor)
                    return True
                return False

            self.foreachPolygonSegments(hitTest)
        return super().mouseDoubleClickEvent(event)

    def initControllers(self):
        if not hasattr(self, "controllers"):
            self.controllers:list[CanvasEllipseItem] = []

        rect = self.getStretchableRect()
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

    def handleFocusChanged(self, originItem, reason, value):
        if value > 0:
            if self.hasFocusWrapper():
                self.initControllers()
        elif value < 0 and reason == Qt.ActiveWindowFocusReason:
            self.hideControllers()
        else:
            scenePos = self.gtCurrentScenePos()

            # 计算绘图区和工具区的并集
            rects = [self.mapRectToScene(self.getStretchableRect()).toRect()]
            for controller in self.controllers:
                rects.append(controller.sceneBoundingRect().toRect())

            region = QRegion()
            region.setRects(rects)

            # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
            if not region.contains(scenePos):
                self.hideControllers()
            else:
                self.setFocus(Qt.OtherFocusReason)

    def focusInEvent(self, event: QFocusEvent) -> None:
        if self.hasFocusWrapper():
            self.initControllers()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if event != None and event.reason() != Qt.MouseFocusReason:
            return
        # if event != None and event.reason() == Qt.ActiveWindowFocusReason:
        #     self.hideControllers()
        #     return

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
        else:
            self.setFocus(Qt.OtherFocusReason)

    def gtCurrentScenePos(self):
        screenPos = self.cursor().pos()
        view = self.scene().views()[0]
        widgetPos = view.mapFromGlobal(screenPos)
        scenePos = view.mapToScene(widgetPos)
        return scenePos.toPoint()

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect() + QMarginsF(self.roiRadius, self.roiRadius, self.roiRadius, self.roiRadius)

    def updateEdge(self, currentPosType, localPos:QPoint):
        offset = -self.roiRadius
        lastRect = self.polygon.boundingRect().toRect()
        newRect = lastRect.adjusted(0, 0, 0, 0)
        if currentPosType == EnumPosType.ControllerPosTL:
            localPos += QPoint(-offset, -offset)
            newRect.setTopLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosTC:
            localPos += QPoint(0, -offset)
            newRect.setTop(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosTR:
            localPos += QPoint(offset, -offset)
            newRect.setTopRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosRC:
            localPos += QPoint(offset, 0)
            newRect.setRight(localPos.x())
        elif currentPosType == EnumPosType.ControllerPosBR:
            localPos += QPoint(offset, offset)
            newRect.setBottomRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosBC:
            localPos += QPoint(0, offset)
            newRect.setBottom(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosBL:
            localPos += QPoint(-offset, offset)
            newRect.setBottomLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosLC:
            localPos = localPos - QPoint(offset, offset)
            newRect.setLeft(localPos.x())

        xScale = newRect.width() / lastRect.width()
        yScale = newRect.height() / lastRect.height()

        # self.prepareGeometryChange()

        for i in range(0, self.polygon.count()):
            oldPos = self.polygon.at(i)

            if currentPosType == EnumPosType.ControllerPosTC:
                yPos = oldPos.y() - abs(oldPos.y() - lastRect.bottomRight().y()) * (yScale - 1)
                newPos = QPointF(oldPos.x(), yPos)
            elif currentPosType == EnumPosType.ControllerPosBC:
                yPos = oldPos.y() + abs(oldPos.y() - lastRect.topLeft().y()) * (yScale - 1)
                newPos = QPointF(oldPos.x(), yPos)
            elif currentPosType == EnumPosType.ControllerPosLC:
                xPos = oldPos.x() - abs(oldPos.x() - lastRect.bottomRight().x()) * (xScale - 1)
                newPos = QPointF(xPos, oldPos.y())
            elif currentPosType == EnumPosType.ControllerPosRC:
                xPos = oldPos.x() + abs(oldPos.x() - lastRect.topLeft().x()) * (xScale - 1)
                newPos = QPointF(xPos, oldPos.y())
            elif currentPosType == EnumPosType.ControllerPosTL:
                xPos = oldPos.x() - abs(oldPos.x() - lastRect.bottomRight().x()) * (xScale - 1)
                yPos = oldPos.y() - abs(oldPos.y() - lastRect.bottomRight().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)
            elif currentPosType == EnumPosType.ControllerPosTR:
                xPos = oldPos.x() + abs(oldPos.x() - lastRect.topLeft().x()) * (xScale - 1)
                yPos = oldPos.y() - abs(oldPos.y() - lastRect.bottomRight().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)
            elif currentPosType == EnumPosType.ControllerPosBR:
                xPos = oldPos.x() + abs(oldPos.x() - lastRect.topLeft().x()) * (xScale - 1)
                yPos = oldPos.y() + abs(oldPos.y() - lastRect.topLeft().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)
            elif currentPosType == EnumPosType.ControllerPosBL:
                xPos = oldPos.x() - abs(oldPos.x() - lastRect.bottomRight().x()) * (xScale - 1)
                yPos = oldPos.y() + abs(oldPos.y() - lastRect.topLeft().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)

            roiItem:CanvasROI = self.roiItemList[i]
            rect = roiItem.rect()
            rect.moveCenter(self.mapToItem(roiItem, newPos))
            roiItem.setRect(rect)

            self.polygon.replace(i, newPos)

        # self.update()
        self.initControllers()

    def startResize(self, localPos:QPointF) -> None:
        pass

    def endResize(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()
        # 解决有旋转角度的矩形，拉伸之后，再次旋转，旋转中心该仍然为之前坐标，手动设置为中心，会产生漂移的问题
        rect = self.shapePath.boundingRect()
        angle = math.radians(self.rotation())

        p1 = rect.center()
        origin = self.transformOriginPoint()
        p2 = QPointF(0, 0)

        p2.setX(origin.x() + math.cos(angle)*(p1.x() - origin.x()) - math.sin(angle)*(p1.y() - origin.y()))
        p2.setY(origin.y() + math.sin(angle)*(p1.x() - origin.x()) + math.cos(angle)*(p1.y() - origin.y()))

        diff:QPointF = p1 - p2
        if diff.isNull():
            return

        self.moveRoiItemsBy(diff)
        self.setTransformOriginPoint(p1-diff)

        self.initControllers()
        self.update()

    def startRotate(self, localPos:QPointF) -> None:
        self.originPos = self.boundingRect().center()
        self.setTransformOriginPoint(self.originPos)
        self.m_pressPos = localPos
    
    def endRotate(self, localPos:QPointF) -> None:
        pass