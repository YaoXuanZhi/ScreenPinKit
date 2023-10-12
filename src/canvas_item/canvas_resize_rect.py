import math
from enum import Enum
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
from collections import OrderedDict

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

class CanvasROIItem(QGraphicsWidget):
    def __init__(self, id:int, hoverCursor:QCursor = None, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.id = id
        self.lastCursor = None
        if hoverCursor == None:
            hoverCursor = Qt.CursorShape.SizeAllCursor
        self.hoverCursor = hoverCursor
        self.setPreferredSize(10, 10)

    def initAttribute(self, posType:EnumPosType, hoverCursor:QCursor):
        self.posType = posType
        self.hoverCursor = hoverCursor
   
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def hasFocusWrapper(self):
        if self.hasFocus() or self.isSelected():
            return True
        else:
            return False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        painter.fillRect(self.rect(), Qt.yellow)

        painter.restore()

    def focusInEvent(self, event: QFocusEvent) -> None:
        parentItem:ResizableRectItem = self.parentItem()
        parentItem.focusInEvent(event)
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        parentItem:ResizableRectItem = self.parentItem()
        parentItem.focusOutEvent(event)
        return super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:ResizableRectItem = self.parentItem()
            parentItem.roiMgr.removeROI(self.id)
        return super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:ResizableRectItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.mouseMoveRotateOperator(event.pos())
            return
        parentItem.updateEdge(self.posType, event.scenePos())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:ResizableRectItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.startRotate(event.pos())
        else:
            parentItem.startResize(event.pos())
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:ResizableRectItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.endRotate(event.pos())
        else:
            parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

class CanvasROIManager():
    def __init__(self, parent: QGraphicsItem) -> None:
        self.parent = parent
        self.itemsOrderDict = OrderedDict()
        self.lastId = 0

    def addROI(self, pos:QPointF, hoverCursor:QCursor = None) -> CanvasROIItem:
        ''''添加操作点'''
        self.lastId += 1
        id = self.lastId
        roiItem = CanvasROIItem(id, hoverCursor, self.parent)
        self.itemsOrderDict[id] = roiItem
        roiItem.setPos(pos)
        return roiItem

    def removeROI(self, id:int):
        ''''移除操作点'''
        roiItem = self.itemsOrderDict.pop(id)
        self.parent.scene().removeItem(roiItem)

    def show(self):
        if len(self.itemsOrderDict) == 0:
            parent:ResizableRectItem = self.parent
            parent.createResizeHandles()
            return

        for value in self.itemsOrderDict.values():
            roi:CanvasROIItem = value
            if not roi.isVisible():
                roi.show()

    def hide(self):
        for value in self.itemsOrderDict.values():
            roi:CanvasROIItem = value
            if roi.isVisible():
                roi.hide()

class ResizableRectItem(QGraphicsWidget):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setGeometry(x, y, w, h)

        self.m_borderWidth = 1
        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.lastCursor = None
        self.shapePath = QPainterPath()

        self.m_pressPos = QPointF() # 本地坐标点击的点

        self.roiMgr = CanvasROIManager(self)

    def createResizeHandlesBak(self):
        self.roiMgr = CanvasROIManager(self)
        self.roiMgr.addROI(self.rect().topLeft())
        self.roiMgr.addROI(self.rect().topRight())
        self.roiMgr.addROI(self.rect().bottomLeft())
        self.roiMgr.addROI(self.rect().bottomRight())

    def createResizeHandles(self):
        layout = QGraphicsAnchorLayout()
        # 去除布局边距，以便同边框点对齐
        layout.setContentsMargins(0, 0, 0, 0)

        topLeftCorner = self.roiMgr.addROI(QPointF(0, 0))
        topLeftCorner.initAttribute(EnumPosType.ControllerPosTL, Qt.SizeFDiagCursor)

        topCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        topCenterCorner.initAttribute(EnumPosType.ControllerPosTC, Qt.SizeVerCursor)

        topRightCorner = self.roiMgr.addROI(QPointF(0, 0))
        topRightCorner.initAttribute(EnumPosType.ControllerPosTR, Qt.SizeBDiagCursor)

        rightCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        rightCenterCorner.initAttribute(EnumPosType.ControllerPosRC, Qt.SizeHorCursor)

        bottomRightCorner = self.roiMgr.addROI(QPointF(0, 0))
        bottomRightCorner.initAttribute(EnumPosType.ControllerPosBR, Qt.SizeFDiagCursor)

        bottomCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        bottomCenterCorner.initAttribute(EnumPosType.ControllerPosBC, Qt.SizeVerCursor)

        bottomLeftCorner = self.roiMgr.addROI(QPointF(0, 0))
        bottomLeftCorner.initAttribute(EnumPosType.ControllerPosBL, Qt.SizeBDiagCursor)

        leftCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        leftCenterCorner.initAttribute(EnumPosType.ControllerPosLC, Qt.SizeHorCursor)

        topTipCorner = self.roiMgr.addROI(QPointF(0, 0))
        topTipCorner.initAttribute(EnumPosType.ControllerPosTT, Qt.PointingHandCursor)

        # 操作点中心锚定父边框左上角
        layout.addAnchor(topLeftCorner, Qt.AnchorVerticalCenter, layout, Qt.AnchorTop)
        layout.addAnchor(topLeftCorner, Qt.AnchorHorizontalCenter, layout, Qt.AnchorLeft)

        # 操作点中心锚定父边框顶部中间
        layout.addAnchor(layout, Qt.AnchorTop, topCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorHorizontalCenter, topCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框右上角
        layout.addAnchor(layout, Qt.AnchorTop, topRightCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorRight, topRightCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框右侧中间
        layout.addAnchor(layout, Qt.AnchorVerticalCenter, rightCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorRight, rightCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框右下角
        layout.addAnchor(layout, Qt.AnchorBottom, bottomRightCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorRight, bottomRightCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框底部中间
        layout.addAnchor(layout, Qt.AnchorBottom, bottomCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorHorizontalCenter, bottomCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框左下角
        layout.addAnchor(layout, Qt.AnchorBottom, bottomLeftCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorLeft, bottomLeftCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框左侧中间
        layout.addAnchor(layout, Qt.AnchorVerticalCenter, leftCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorLeft, leftCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框顶部中间
        layout.addAnchor(topCenterCorner, Qt.AnchorTop, topTipCorner, Qt.AnchorBottom)
        layout.addAnchor(topCenterCorner, Qt.AnchorHorizontalCenter, topTipCorner, Qt.AnchorHorizontalCenter)

        self.setLayout(layout)

    def gtCurrentScenePos(self):
        screenPos = self.cursor().pos()
        view = self.scene().views()[0]
        widgetPos = view.mapFromGlobal(screenPos)
        scenePos = view.mapToScene(widgetPos)
        return scenePos.toPoint()

    def focusInEvent(self, event: QFocusEvent) -> None:
        print("=========>")
        if self.hasFocusWrapper():
            self.roiMgr.show()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        print("=========<")
        scenePos = self.gtCurrentScenePos()

        # 计算绘图区和工具区的并集
        rects = [self.sceneBoundingRect().toRect()]
        for value in self.roiMgr.itemsOrderDict.values():
            roi:CanvasROIItem = value
            rects.append(roi.sceneBoundingRect().toRect())
        region = QRegion()
        region.setRects(rects)

        # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
        if not region.contains(scenePos):
            self.roiMgr.hide()

    def updateEdge(self, currentPosType, scenePos:QPointF):
        offset = 0
        lastRect = self.geometry()
        newRect = lastRect.adjusted(0, 0, 0, 0)
        if currentPosType == EnumPosType.ControllerPosTL:
            scenePos += QPointF(-offset, -offset)
            newRect.setTopLeft(scenePos)
        elif currentPosType == EnumPosType.ControllerPosTC:
            scenePos += QPointF(0, -offset)
            newRect.setTop(scenePos.y())
        elif currentPosType == EnumPosType.ControllerPosTR:
            scenePos += QPointF(offset, -offset)
            newRect.setTopRight(scenePos)
        elif currentPosType == EnumPosType.ControllerPosRC:
            scenePos += QPointF(offset, 0)
            newRect.setRight(scenePos.x())
        elif currentPosType == EnumPosType.ControllerPosBR:
            scenePos += QPointF(offset, offset)
            newRect.setBottomRight(scenePos)
        elif currentPosType == EnumPosType.ControllerPosBC:
            scenePos += QPointF(0, offset)
            newRect.setBottom(scenePos.y())
        elif currentPosType == EnumPosType.ControllerPosBL:
            scenePos += QPointF(-offset, offset)
            newRect.setBottomLeft(scenePos)
        elif currentPosType == EnumPosType.ControllerPosLC:
            scenePos = scenePos - QPointF(offset, offset)
            newRect.setLeft(scenePos.x())

        self.setGeometry(newRect)

    def startResize(self, localPos:QPointF) -> None:
        pass

    def endResize(self, localPos:QPointF) -> None:
        # 解决有旋转角度的矩形，拉伸之后，再次旋转，旋转中心该仍然为之前坐标，手动设置为中心，会产生漂移的问题
        rect = self.geometry()
        angle = math.radians(self.rotation())

        p1 = self.rect().center()
        origin = self.transformOriginPoint()
        p2 = QPointF(0, 0)

        p2.setX(origin.x() + math.cos(angle)*(p1.x() - origin.x()) - math.sin(angle)*(p1.y() - origin.y()))
        p2.setY(origin.y() + math.sin(angle)*(p1.x() - origin.x()) + math.cos(angle)*(p1.y() - origin.y()))

        diff:QPointF = p1 - p2

        self.setGeometry(rect.adjusted(-diff.x(), -diff.y(), -diff.x(), -diff.y()))
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
        self.lastCursor = self.cursor()
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def hasFocusWrapper(self):
        if self.hasFocus() or self.isSelected():
            return True
        else:
            for value in self.roiMgr.itemsOrderDict.values():
                roi:CanvasROIItem = value
                if roi.hasFocusWrapper():
                    return True
        return False

    def boundingRect(self) -> QRectF:
        # if self.shapePath.isEmpty():
        #     return super().boundingRect()
        # else:
        #     return self.shapePath.boundingRect()
        return self.rect()

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        self.shapePath.clear()
        if self.hasFocusWrapper():
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            for value in self.roiMgr.itemsOrderDict.values():
                roi:CanvasROIItem = value
                rects.append(roi.boundingRect().toRect())
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

    def startRotate(self, localPos:QPointF) -> None:
        self.originPos = self.rect().center()
        self.setTransformOriginPoint(self.originPos)
        self.m_pressPos = localPos

    def endRotate(self, localPos:QPointF) -> None:
        pass
