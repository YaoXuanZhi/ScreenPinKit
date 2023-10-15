import math
from enum import Enum
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
from collections import OrderedDict, deque

# 采用GObject的机制来包裹住这个操作点，让一个独立的位置点跟随它而自动调整，总体而言，这种方式的鲁棒性会更好一点

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

class ResizableRectItem2(QGraphicsRectItem):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setRect(x, y, w, h)

        self.m_radius = 8
        self.m_borderWidth = 1
        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

        self.m_outsideDistance = 30
        self.selectedMargin = QMarginsF(self.m_radius, self.m_radius - self.m_outsideDistance, self.m_radius, self.m_radius)
        self.normalMargin = QMarginsF(self.m_radius, self.m_radius, self.m_radius, self.m_radius)

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.lastCursorCache = deque()
        self.shapePath = QPainterPath()

        self.m_pressPos = QPointF() # 本地坐标点击的点

    def updateHandlers(self):
        self.handlerRects = []
        targetRect = self.rect()

        points = [
            targetRect.topLeft(), 
            (targetRect.topLeft() + targetRect.topRight()) / 2,
            targetRect.topRight(), 
            (targetRect.topRight() + targetRect.bottomRight()) / 2,
            targetRect.bottomRight(),
            (targetRect.bottomRight() + targetRect.bottomLeft()) / 2,
            targetRect.bottomLeft(), 
            (targetRect.topLeft() + targetRect.bottomLeft()) / 2,

            (targetRect.topLeft() + targetRect.topRight()) / 2 + QPoint(0, -self.m_outsideDistance),
            ]

        for pos in points:
            rect = QRectF(0, 0, self.m_radius*2, self.m_radius*2)
            rect.moveCenter(pos)
            self.handlerRects.append(rect.toRect())

    def boundingRect(self) -> QRectF:
        self.updateHandlers()
        if self.isSelected():
            return self.rect() + self.selectedMargin
        else:
            return self.rect() + self.normalMargin

    def shape(self) -> QPainterPath:
        self.shapePath = QPainterPath()

        if self.isSelected():
            normalBoundingRect:QRectF = self.rect() + self.normalMargin
            handlerRegion = QRegion()
            handlerRegion.setRects(self.handlerRects)
            finalRegion = handlerRegion.united(normalBoundingRect.toRect())
            self.shapePath.addRegion(finalRegion)
        else:
            outsideRect = self.boundingRect().toRect()
            selectRegion = QRegion(outsideRect)
            insideRect:QRectF = self.rect() - self.normalMargin
            subRegion = QRegion(insideRect.toRect())
            finalRegion = selectRegion.subtracted(subRegion)
            self.shapePath.addRegion(finalRegion)
        return self.shapePath

    def paintHandlers(self, painter:QPainter):
        painter.setPen(Qt.green)
        for rect in self.handlerRects:
            # painter.drawRect(rect)
            painter.drawEllipse(rect)

    def gtCurrentScenePos(self):
        screenPos = self.cursor().pos()
        view = self.scene().views()[0]
        widgetPos = view.mapFromGlobal(screenPos)
        scenePos = view.mapToScene(widgetPos)
        return scenePos.toPoint()

    def startResize(self, localPos:QPointF) -> None:
        pass

    def endResize(self, localPos:QPointF) -> None:
        # 解决有旋转角度的矩形，拉伸之后，再次旋转，旋转中心该仍然为之前坐标，手动设置为中心，会产生漂移的问题
        rect = self.rect()
        angle = math.radians(self.rotation())

        p1 = self.rect().center()
        origin = self.transformOriginPoint()
        p2 = QPointF(0, 0)

        p2.setX(origin.x() + math.cos(angle)*(p1.x() - origin.x()) - math.sin(angle)*(p1.y() - origin.y()))
        p2.setY(origin.y() + math.sin(angle)*(p1.x() - origin.x()) + math.cos(angle)*(p1.y() - origin.y()))

        diff:QPointF = p1 - p2

        self.setRect(rect.adjusted(-diff.x(), -diff.y(), -diff.x(), -diff.y()).normalized())
        self.setTransformOriginPoint(self.rect().center())

    def mouseMoveRotateOperator(self, localPos:QPointF) -> None:
        p1 = QLineF(self.originPos, self.m_pressPos)
        p2 = QLineF(self.originPos, localPos)

        dRotateAngle = p2.angleTo(p1)

        dCurAngle = self.rotation() + dRotateAngle
        while dCurAngle > 360.0:
            dCurAngle -= 360.0
        self.setRotation(dCurAngle)
        self.update()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursorCache.append(self.cursor())
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if len(self.lastCursorCache) > 0:
            self.setCursor(self.lastCursorCache.pop())
        return super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        return super().hoverMoveEvent(event)

    def hasFocusWrapper(self):
        if self.hasFocus() or self.isSelected():
            return True
        return False

    def boundingRect(self) -> QRectF:
        self.updateHandlers()
        if self.shapePath.isEmpty():
            return super().boundingRect()
        else:
            return self.shapePath.boundingRect()

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        self.shapePath.clear()
        if self.hasFocusWrapper():
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            for value in self.handlerRects:
                handleRect = value
                rects.append(handleRect)
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

        if self.hasFocusWrapper():
            self.paintHandlers(painter)

        painter.restore()

    def startRotate(self, localPos:QPointF) -> None:
        self.originPos = self.rect().center()
        self.setTransformOriginPoint(self.originPos)
        self.m_pressPos = localPos

    def endRotate(self, localPos:QPointF) -> None:
        pass
