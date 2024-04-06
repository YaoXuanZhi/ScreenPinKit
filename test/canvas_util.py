from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, math

class CanvasUtil:
    @staticmethod
    def buildSegmentsPath(targetPath:QPainterPath, points:list):
        """
        构造连续线段

        Parameters:
        targetPath: 目标路径
        points: 记录点
        """

        targetPath.clear()

        for i in range(0, len(points)):
            point = points[i]
            if i == 0:
                targetPath.moveTo(point)
            else:
                targetPath.lineTo(point)

    @staticmethod
    def buildArrowPath(targetPath:QPainterPath, points:list, arrowStyle:map):
        """
        构造箭头

        Parameters:
        targetPath: 目标路径
        arrowStyle: 箭头风格
        points: 记录点
        """
        targetPath.clear()

        arrowLength = arrowStyle["arrowLength"]
        arrowAngle = arrowStyle["arrowAngle"]
        arrowBodyLength = arrowStyle["arrowBodyLength"]
        arrowBodyAngle = arrowStyle["arrowBodyAngle"]

        begin = points[0]
        end = points[-1]

        x1 = begin.x()  # 取 points[0] 起点的 x
        y1 = begin.y()  # 取 points[0] 起点的 y  
        x2 = end.x()    # 取 points[count-1] 终点的 x  
        y2 = end.y()    # 取 points[count-1] 终点的 y  
        x3 = x2 - arrowLength * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - arrowAngle) # 计算箭头的终点（x3,y3）  
        y3 = y2 - arrowLength * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - arrowAngle)   
        x4 = x2 - arrowLength * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - arrowAngle) # 计算箭头的终点（x4,y4）  
        y4 = y2 - arrowLength * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - arrowAngle)   

        x5 = x2 - arrowBodyLength * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - arrowBodyAngle) # 计算箭头的终点（x5,y5）  
        y5 = y2 - arrowBodyLength * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - arrowBodyAngle)   
        x6 = x2 - arrowBodyLength * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - arrowBodyAngle) # 计算箭头的终点（x6,y6）  
        y6 = y2 - arrowBodyLength * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - arrowBodyAngle)   

        arrowTailPos = QPointF(x1, y1) # 箭尾位置点
        arrowHeadPos = QPointF(x2, y2) # 箭头位置点
        arrowHeadRightPos = QPointF(x3, y3) # 箭头右侧边缘位置点
        arrowHeadLeftPos = QPointF(x4, y4) # 箭头左侧边缘位置点
        arrowBodyRightPos = QPointF(x5, y5) # 箭身右侧位置点
        arrowBodyLeftPos = QPointF(x6, y6) # 箭身左侧位置点

        targetPath.moveTo(arrowTailPos)
        targetPath.lineTo(arrowBodyLeftPos)
        targetPath.lineTo(arrowHeadLeftPos)
        targetPath.lineTo(arrowHeadPos)
        targetPath.lineTo(arrowHeadRightPos)
        targetPath.lineTo(arrowBodyRightPos)
        targetPath.closeSubpath()

    @staticmethod
    def buildStarPath(targetPath:QPainterPath, points:list):
        """
        构造五角星

        Parameters:
        targetPath: 目标路径
        points: 记录点
        """

        targetPath.clear()

        targetBottomLeft = points[0]
        targetTopRight = points[-1]

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
        targetPath.moveTo(B)
        targetPath.lineTo(F)
        targetPath.lineTo(A)
        targetPath.lineTo(J)
        targetPath.lineTo(E)
        targetPath.lineTo(I)
        targetPath.lineTo(D)
        targetPath.lineTo(H)
        targetPath.lineTo(C)
        targetPath.lineTo(G)
        targetPath.lineTo(B)
        targetPath.closeSubpath()

class CanvasROI(QGraphicsEllipseItem):
    def __init__(self, hoverCursor:QCursor, id:int, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.hoverCursor = hoverCursor
        self.id = id
        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:UICanvasCommonPathItem = self.parentItem()
        parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:UICanvasCommonPathItem = self.parentItem()
        localPos = self.mapToItem(parentItem, self.rect().center())
        parentItem.roiMgr.movePointById(self, localPos)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:UICanvasCommonPathItem = self.parentItem()
            parentItem.roiMgr.removePoint(self)
        return super().mouseDoubleClickEvent(event)

class CanvasROIManager(QObject):
    removeROIAfterSignal = pyqtSignal(int)
    moveROIAfterSignal = pyqtSignal(int, QPointF)
    def __init__(self,parent=None, attachParent:QGraphicsItem=None):
        super().__init__(parent)
        self.attachParent = attachParent

        self.roiItemList:list[CanvasROI] = []

        self.m_instId = 0
        self.canRoiItemEditable = True
        self.radius = 8
        # self.roiRadius = 14
        self.m_borderWidth = 4
        self.roiRadius = self.m_borderWidth + 3

    def addPoint(self, point:QPointF, cursor:QCursor = Qt.PointingHandCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId

        if self.canRoiItemEditable:
            roiItem = CanvasROI(cursor, id, self.attachParent)
            rect = QRectF(QPointF(0, 0), QSizeF(self.roiRadius*2, self.roiRadius*2))
            rect.moveCenter(point)
            roiItem.setRect(rect)

            self.roiItemList.append(roiItem)
            return roiItem
        return None

    def insertPoint(self, insertIndex:int, point:QPointF, cursor:QCursor = Qt.SizeAllCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId

        roiItem = CanvasROI(cursor, id, self)
        rect = QRectF(QPointF(0, 0), QSizeF(self.roiRadius*2, self.roiRadius*2))
        rect.moveCenter(point)
        roiItem.setRect(rect)

        self.roiItemList.insert(insertIndex, roiItem)
        return roiItem

    def removePoint(self, roiItem:CanvasROI):
        if not self.canRoiItemEditable:
            return

        # 如果是移除最后一个操作点，说明该路径将被移除
        if len(self.roiItemList) == 1:
            scene = self.attachParent.scene()
            scene.removeItem(self)
            return

        index = self.roiItemList.index(roiItem)
        self.roiItemList.remove(roiItem)
        self.attachParent.scene().removeItem(roiItem)

        self.removeROIAfterSignal.emit(index)

    def movePointById(self, roiItem:CanvasROI, localPos:QPointF):
        index = self.roiItemList.index(roiItem)
        self.moveROIAfterSignal.emit(index, localPos)

class UICanvasCommonPathItem(QGraphicsPathItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setDefaultFlag()

        self.attachPath = QPainterPath()
        self.points = []

        self.roiMgr = CanvasROIManager(attachParent=self)

        self.roiMgr.removeROIAfterSignal.connect(self.removeROIAfterCallback)
        self.roiMgr.moveROIAfterSignal.connect(self.moveROIAfterCallback)

    def removeROIAfterCallback(self, index:int):
        self.points.remove(self.points[index])
        self.endResize(None)

    def moveROIAfterCallback(self, index:int, localPos:QPointF):
        self.prepareGeometryChange()
        self.points[index] = localPos
        self.rebuildUI()

    def rebuildUI(self):
        """
        重建UI

        Raises:
        NotImplementedError: 子类需要重写该函数

        Examples:
        ```python
        # 构造连续线段
        CanvasUtil.buildSegmentsPath(self.path, self.points)
        self.setPath(self.path)
        ```
        """
        raise NotImplementedError("子类需要重写该函数")

    def showControllers(self):
        '''生成操作点'''

        for i in range(0, len(self.points)):
            point:QPoint = self.points[i]
            self.roiMgr.addPoint(point)

        self.rebuildUI()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        for roiItem in self.roiMgr.roiItemList:
            roiItem.show()
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        for roiItem in self.roiMgr.roiItemList:
            roiItem.hide()
        return super().hoverLeaveEvent(event)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        '''去掉虚线'''
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def endResize(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()
        self.rebuildUI()

        rect = self.attachPath.boundingRect()
        # 计算正常旋转角度（0度）下，中心的的坐标
        oldCenter = QPointF(self.x()+rect.x()+rect.width()/2, self.y()+rect.y()+rect.height()/2)
        # 计算旋转后，中心坐标在view中的位置
        newCenter = self.mapToScene(rect.center())
        # 设置正常坐标减去两个坐标的差
        difference = oldCenter-newCenter
        self.setPos(self.x()-difference.x(), self.y()-difference.y())
        # 最后设置旋转中心
        self.setTransformOriginPoint(rect.center())

        self.update()

class CanvasAttribute(QObject):
    valueChangedSignal = pyqtSignal(QVariant)
    displayName:str

    isFirstSetValue = True

    lastValue:QVariant = None
    currentValue:QVariant = None

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def getType(self) -> QVariant.Type:
        value:QVariant = self.currentValue
        return value.type()

    def setDisplayName(self, name:str) -> None:
        self.displayName = name

    def getLastValue(self) -> QVariant:
        return self.lastValue

    def getValue(self) -> QVariant:
        return self.currentValue

    def setValue(self, value:QVariant) -> None:
        if self.isFirstSetValue:
            self.lastValue = value
            self.isFirstSetValue = False

        if self.currentValue == value:
            return

        self.lastValue = self.currentValue
        self.currentValue = value

        self.valueChangedSignal.emit(value)