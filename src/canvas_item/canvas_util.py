from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math, typing, os
from enum import Enum
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from PyQt5.QtWidgets import QGraphicsSceneWheelEvent

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
    '''
    参考 [qgraphicsitem.cpp](https://codebrowser.dev/qt5/qtbase/src/widgets/graphicsview/qgraphicsitem.cpp.html#742) 实现一个QGraphicsEllipseItem
    '''
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

# class CanvasEllipseItem(CanvasBaseItem):
class CanvasEllipseItem(QGraphicsEllipseItem):
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

    def setSvgCursor(self) -> QCursor:
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            self.setCursor(self.interfaceCursor)
            return
        else:
            svgName = "aero_nwse.svg"
            if self.posType in [EnumPosType.ControllerPosTL, EnumPosType.ControllerPosBR]:
                svgName = "aero_nwse.svg"
            elif self.posType in [EnumPosType.ControllerPosTR, EnumPosType.ControllerPosBL]:
                svgName = "aero_nesw.svg"
            elif self.posType in [EnumPosType.ControllerPosTC, EnumPosType.ControllerPosBC]:
                svgName = "aero_ns.svg"
            elif self.posType in [EnumPosType.ControllerPosLC, EnumPosType.ControllerPosRC]:
                svgName = "aero_ew.svg"

            svgPath = os.path.join(os.path.dirname(__file__), "demos/resources", svgName)
            icon = QIcon(svgPath)
            pixmap = icon.pixmap(QSize(36, 36))

            transform = parentItem.transform()
            transform.rotate(parentItem.rotation())
            finalPixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
            newFinal = QCursor(finalPixmap, -1, -1)
            self.setCursor(newFinal)

   
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        # self.setCursor(self.interfaceCursor)
        self.setSvgCursor()
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
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.mouseMoveRotateOperator(event.scenePos(), event.pos())
            return
        parentItem.updateEdge(self.posType, event.pos().toPoint())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.startRotate(event.pos())
        else:
            parentItem.startResize(event.pos())
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.endRotate(event.pos())
        else:
            parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        parentItem = self.parentItem()
        if parentItem != None:
            parentItem.wheelEvent(event)
        return super().wheelEvent(event)

class CanvasUtil:
    @staticmethod
    def grabScreens():
        screens = QApplication.screens()
        w = h = p = 0
        screenPixs = []

        #将多显示器的屏幕快照从左往右排序，与实际屏幕摆放位置一致
        screens.sort(key=lambda screen: screen.geometry().x())

        #考虑到需要兼容那种一个横屏、一个竖屏的情况
        for screen in screens:
            pix = screen.grabWindow(0)
            w += pix.width()
            h = max(h, pix.height())
            screenPixs.append(pix)

        finalPixmap = QPixmap(w, h)
        finalPixmap.setDevicePixelRatio(screens[0].devicePixelRatio())
        finalPixmap.fill(Qt.transparent)
        painter = QPainter(finalPixmap)
        for pix in screenPixs:
            painter.drawPixmap(QPoint(p, 0), pix)
            p = p + pix.width()

        # # 拿到最左侧屏幕的左上角坐标
        geometryTopLeft = screens[0].geometry().topLeft()

        finalGeometry = QRect(geometryTopLeft, QSize(w, h))
        return finalPixmap, finalGeometry

    @staticmethod
    def foreachPolygonSegments(polygon:QPolygonF, offsetLength:float, callback:callable):
        count = polygon.count()
        for i in range(0, count):
            points = []
            polygonPath = QPainterPath()
            startIndex = i
            endIndex = i + 1
            endIndex %= count
            startPoint = polygon.at(startIndex)
            endPoint = polygon.at(endIndex)

            offset = CanvasUtil.calcOffset(startPoint, endPoint, offsetLength)

            points.append(startPoint - offset)
            points.append(startPoint + offset)
            points.append(endPoint + offset)
            points.append(endPoint - offset)

            polygonPath.addPolygon(QPolygonF(points))
            polygonPath.closeSubpath()
            if callback(startIndex, endIndex, polygonPath):
                break

            if count < 3:
                break

    @staticmethod
    def buildSegmentsPath(targetPath:QPainterPath, polygon:QPolygonF, isClosePath:bool = False):
        """
        构造连续线段

        Parameters:
        targetPath: 目标路径
        points: 记录点
        """

        targetPath.clear()

        for i in range(0, polygon.count()):
            point = polygon.at(i)
            if i == 0:
                targetPath.moveTo(point)
            else:
                targetPath.lineTo(point)

        if isClosePath:
            targetPath.closeSubpath()

        return []

    @staticmethod
    def calcOffset(startPoint:QPointF, endPoint:QPointF, offsetLength:float) -> QPointF:
        '''计算线段法向量，并且将其长度设为圆的半径，计算它们的偏移量'''
        v = QLineF(startPoint, endPoint)
        n = v.normalVector()
        n.setLength(offsetLength)
        return n.p1() - n.p2()

    @staticmethod
    def buildSegmentsRectPath(targetPath:QPainterPath, polygon:QPolygonF, offsetLength:float, isClosePath:bool = False):
        """
        构造连续矩形线段

        Note:
        将相邻两点加上线条宽度构成的连续矩形合并成一个pathItem
        """

        targetPath.clear()

        def appendShapePath(startIndex, endIndex, polygonPath:QPainterPath):
            if not isClosePath and endIndex == 0: 
                return True

            targetPath.addPath(polygonPath)

            return False

        CanvasUtil.foreachPolygonSegments(polygon, offsetLength, appendShapePath)

        # 添加Roi的操作区域
        for i in range(0, polygon.count()):
            point:QPoint = polygon.at(i)
            rect = QRectF(QPointF(0, 0), QSizeF(offsetLength*2, offsetLength*2))
            rect.moveCenter(point)
            targetPath.addEllipse(rect)

    @staticmethod
    def buildRectanglePath(targetPath:QPainterPath, polygon:QPolygonF) -> typing.Iterable[QPointF]:
        '''构造矩形'''
        targetPath.clear()

        begin = polygon.at(0)
        end = polygon.at(polygon.count() - 1)

        if begin == end:
            return

        targetPath.addRect(QRectF(begin, end).normalized())

        return []

    @staticmethod
    def buildEllipsePath(targetPath:QPainterPath, polygon:QPolygonF) -> typing.Iterable[QPointF]:
        '''构造圆形'''
        targetPath.clear()

        begin = polygon.at(0)
        end = polygon.at(polygon.count() - 1)

        if begin == end:
            return

        targetPath.addEllipse(QRectF(begin, end).normalized())

        return []

    @staticmethod
    def buildArrowPath(targetPath:QPainterPath, polygon:QPolygonF, arrowStyle:map) -> typing.Iterable[QPointF]:
        '''构造箭头'''
        targetPath.clear()

        arrowLength = arrowStyle["arrowLength"]
        arrowAngle = arrowStyle["arrowAngle"]
        arrowBodyLength = arrowStyle["arrowBodyLength"]
        arrowBodyAngle = arrowStyle["arrowBodyAngle"]

        begin = polygon.at(0)
        end = polygon.at(polygon.count() - 1)

        if begin == end:
            return

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

        return [arrowTailPos, arrowBodyLeftPos, arrowHeadLeftPos, arrowHeadPos, arrowHeadRightPos, arrowBodyRightPos]

    @staticmethod
    def buildStarPath(targetPath:QPainterPath, polygon:QPolygonF) -> typing.Iterable[QPointF]:
        ''''构造五角星'''

        targetPath.clear()

        targetBottomLeft = polygon.at(0)
        targetTopRight = polygon.at(polygon.count() - 1)

        if targetBottomLeft == targetTopRight:
            return

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
        # targetPath.moveTo(B)
        targetPath.closeSubpath()

        return [B, F, A, J, E, I, D, H, C, G]

    @staticmethod
    def adjustFontSizeToFit(text, font:QFont, rect:QRectF, minFontSize = 1, maxFontSize = 50):
        '''调整字体适应大小'''

        # 计算给定字体大小下的文本宽度和高度
        def calcFontSize(targetFont):
            font_metrics = QFontMetricsF(targetFont)
            return font_metrics.size(0, text)

        finalFontSize = minFontSize
        offset = 0
        while finalFontSize >= minFontSize and finalFontSize < maxFontSize:
            # 获取当前字体大小下的文本尺寸
            size = calcFontSize(QFont(font.family(), finalFontSize))
            # if size.width() <= rect.width() + offset and size.height() <= rect.height() + offset:
            if size.width() <= rect.width() + offset:
                # 如果文本可以放入矩形区域内，尝试使用更大的字体大小
                finalFontSize += 1
            else:
                # 文本太大，无法放入矩形区域，跳出循环
                break

            font.setPointSize(finalFontSize)

class CanvasROI(QGraphicsEllipseItem):
    def __init__(self, hoverCursor:QCursor, id:int, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.hoverCursor = hoverCursor
        self.id = id
        self.initUI()
        self.isMoving = False
        self.setBrush(Qt.GlobalColor.white)
        self.setPen(QPen(Qt.NoPen))
        self.parent = parent

        self.mousePressCallback = None
        self.mouseReleaseCallback = None
        self.mouseMoveCallback = None

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = True
        if self.mousePressCallback != None:
            self.mousePressCallback(self, event)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = False
        if self.mouseReleaseCallback != None:
            self.mouseReleaseCallback(self, event)
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.isMoving:
            if self.mouseMoveCallback != None:
                self.mouseMoveCallback(self, event)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:CanvasCommonPathItem = self.parentItem()
            parentItem.roiMgr.removePoint(self)
        return super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        parentItem = self.parentItem()
        if parentItem != None:
            parentItem.wheelEvent(event)
        return super().wheelEvent(event)

class CanvasROIManager(QObject):
    removeROIAfterSignal = pyqtSignal(int)
    moveROIAfterSignal = pyqtSignal(int, QPointF)
    def __init__(self,parent=None, attachParent:QGraphicsItem=None):
        super().__init__(parent)
        self.attachParent = attachParent

        self.m_instId = 0
        self.canRoiItemEditable = True
        self.roiRadius = 8

        self.roiItemList:list[CanvasROI] = []

    def mousePressHandle(self, roiItem:CanvasROI, event: QGraphicsSceneMouseEvent):
        if not self.attachParent.hasFocus():
            self.attachParent.setFocus(Qt.FocusReason.OtherFocusReason)

    def mouseReleaseHandle(self, roiItem:CanvasROI, event: QGraphicsSceneMouseEvent):
        parentItem:CanvasCommonPathItem = self.attachParent
        parentItem.endResize(event.pos())

    def mouseMoveHandle(self, roiItem:CanvasROI, event: QGraphicsSceneMouseEvent):
        parentItem:CanvasCommonPathItem = self.attachParent
        localPos = roiItem.mapToItem(parentItem, roiItem.rect().center())
        self.movePointById(roiItem, localPos)

    def addPoint(self, point:QPointF, cursor:QCursor = Qt.PointingHandCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId

        if self.canRoiItemEditable:
            roiItem = CanvasROI(cursor, id, self.attachParent)
            roiItem.mousePressCallback = self.mousePressHandle
            roiItem.mouseReleaseCallback = self.mouseReleaseHandle
            roiItem.mouseMoveCallback = self.mouseMoveHandle
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
        roiItem.mousePressCallback = self.mousePressHandle
        roiItem.mouseReleaseCallback = self.mouseReleaseHandle
        roiItem.mouseMoveCallback = self.mouseMoveHandle
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

    def roiItemCount(self):
        return len(self.roiItemList)

    def setShowState(self, isShow:bool):
        for roiItem in self.roiItemList:
            if isShow:
                roiItem.show()
            else:
                roiItem.hide()

    def initRoiItems(self, polygon:QPolygonF):
        if polygon.count() > 0:
            for i in range(0, polygon.count()):
                point:QPoint = polygon.at(i)
                self.addPoint(point)
            self.setShowState(False)

class CanvasCommonPathItem(QGraphicsPathItem):
    '''
    绘图工具-通用Path图元

    Note:
    该图元为PathItem新增了交互式编辑行为
    '''

    RoiPreviewerMode = 1 << 0 # 预览Roi点模式
    RoiEditableMode = 1 << 1 # Roi点可编辑模式
    BorderEditableMode = 1 << 2 # 边界可编辑模式
    HitTestMode = 1 << 3 # 测试点击模式
    AdvanceSelectMode = 1 << 4 # 高级选择模式

    def setEditMode(self, flag, isEnable:bool):
        if isEnable:
            self.editMode = self.editMode | flag
        else:
            self.editMode = self.editMode &~ flag

    def isHitTestMode(self) -> bool:
        return self.editMode | CanvasCommonPathItem.HitTestMode == self.editMode

    def isRoiEditableMode(self) -> bool:
        return self.editMode | CanvasCommonPathItem.RoiEditableMode == self.editMode

    def isBorderEditableMode(self) -> bool:
        return self.editMode | CanvasCommonPathItem.BorderEditableMode == self.editMode

    def isAdvanceSelectMode(self) -> bool:
        return self.editMode | CanvasCommonPathItem.AdvanceSelectMode == self.editMode

    def isRoiPreviewerMode(self) -> bool:
        return self.editMode | CanvasCommonPathItem.RoiPreviewerMode == self.editMode

    def __initEditMode(self):
        self.editMode = CanvasCommonPathItem.RoiEditableMode | CanvasCommonPathItem.BorderEditableMode | CanvasCommonPathItem.HitTestMode | CanvasCommonPathItem.AdvanceSelectMode

    def __init__(self, parent: QWidget = None, isClosePath:bool = False) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.isClosePath = isClosePath
        self.setEditableState(False)

        self.attachPath = QPainterPath()
        self.polygon = QPolygonF()

        self.roiMgr = CanvasROIManager(attachParent=self)

        self.roiMgr.removeROIAfterSignal.connect(self.removeROIAfterCallback)
        self.roiMgr.moveROIAfterSignal.connect(self.moveROIAfterCallback)

        self.radius = 8

        self.m_borderWidth = 1
        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

        self.devicePixelRatio = 1

        self.isPreview = 0

    def removeROIAfterCallback(self, index:int):
        self.polygon.remove(index)
        self.endResize(None)

    def moveROIAfterCallback(self, index:int, localPos:QPointF):
        self.prepareGeometryChange()
        self.polygon.replace(index, localPos)
        self.update()

    def getOffsetLength(self) -> int:
        # 在分段构造的时候，需要传入一个偏移长度
        return self.radius

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        '''构造形状路径'''
        # 封闭曲线没必要针对每段进行细分模拟
        if self.isAdvanceSelectMode() and not self.isClosePath:
            CanvasUtil.buildSegmentsRectPath(targetPath, targetPolygon, self.getOffsetLength(), isClosePath)
        else:
            CanvasUtil.buildSegmentsPath(targetPath, targetPolygon, isClosePath)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.isPreview == 0 and self.isRoiPreviewerMode():
            self.isPreview = 1
            self.roiMgr.setShowState(True)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.isPreview == 1 and self.isRoiPreviewerMode():
            self.isPreview = 0
            self.roiMgr.setShowState(False)
        return super().hoverLeaveEvent(event)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.isPreview = 2
        return super().focusInEvent(event)

    def mouseMoveRotateOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        p1 = QLineF(self.originPos, self.m_pressPos)
        p2 = QLineF(self.originPos, localPos)

        dRotateAngle = p2.angleTo(p1)

        dCurAngle = self.rotation() + dRotateAngle
        while dCurAngle > 360.0:
            dCurAngle -= 360.0
        self.setRotation(dCurAngle)
        self.update()

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect() + QMarginsF(self.radius, self.radius, self.radius, self.radius)

    def excludeControllers(self) -> list:
        return []

    def initControllers(self):
        if not self.isBorderEditableMode():
            return

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
                if info[0] in self.excludeControllers():
                    continue
                controller = CanvasEllipseItem(info[-1], self)
                controller.setRectWrapper(rect, info[0], self.radius, size)
                self.controllers.append(controller)
        else:
            for controller in self.controllers:
                controller.resetPosition(rect, self.radius, size)
                if not controller.isVisible():
                    controller.show()

    def hideControllers(self):
        if not hasattr(self, "controllers"):
            return
        for controller in self.controllers:
            if controller.isVisible():
                controller.hide()

    def setEditableState(self, isEditable:bool):
        '''设置可编辑状态'''
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        if self.hasFocusWrapper() and self.isBorderEditableMode():
            selectPath = QPainterPath()
            region = QRegion()
            rects = [self.attachPath.boundingRect().toRect()]
            for value in self.roiMgr.roiItemList:
                roiItem:CanvasROI = value
                rects.append(roiItem.boundingRect().toRect())
            region.setRects(rects)
            selectPath.addRegion(region)
            return selectPath

        return self.attachPath

    def boundingRect(self) -> QRectF:
        self.attachPath.clear()

        self.buildShapePath(self.attachPath, self.polygon, self.isClosePath)

        return self.attachPath.boundingRect()

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # 绘制路径
        painter.setPen(self.m_penDefault if not self.hasFocusWrapper() or not self.isHitTestMode() else self.m_penSelected)
        painter.drawPath(targetPath)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        self.devicePixelRatio = painter.device().devicePixelRatioF()
        painter.save()
        self.customPaint(painter, self.attachPath)
        painter.restore()

        painter.save()

        # 绘制操作边框
        if self.hasFocusWrapper():
            if self.radius > 3 and self.isHitTestMode():
                painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
                painter.drawRect(self.polygon.boundingRect())

            if self.isBorderEditableMode():
                painter.setPen(QPen(Qt.yellow, 1, Qt.DashLine))
                rect = self.getStretchableRect()
                painter.drawRect(rect)

        painter.restore()

        # 更新边框操作点位置
        if self.isBorderEditableMode():
            if self.hasFocusWrapper():
                self.initControllers()
            else:
                self.hideControllers()

        # 更新Roi状态
        if self.isRoiEditableMode() and self.isPreview > 1:
            if self.hasFocusWrapper():
                self.roiMgr.setShowState(True)
            else:
                self.roiMgr.setShowState(False)
                self.isPreview = 0

    def updateEdge(self, currentPosType, localPos:QPoint):
        offset = -self.radius
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

        xScale = newRect.width() / max(lastRect.width(), 1)
        yScale = newRect.height() / max(lastRect.height(), 1)

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

            if self.roiMgr.roiItemCount() > 0:
                roiItem:CanvasROI = self.roiMgr.roiItemList[i]
                rect = roiItem.rect()
                rect.moveCenter(self.mapToItem(roiItem, newPos))
                roiItem.setRect(rect)

            self.polygon.replace(i, newPos)

        self.update()

    def startRotate(self, localPos:QPointF) -> None:
        self.originPos = self.boundingRect().center()
        self.setTransformOriginPoint(self.originPos)
        self.m_pressPos = localPos
    
    def endRotate(self, localPos:QPointF) -> None:
        pass

    def startResize(self, localPos:QPointF) -> None:
        pass

    def endResize(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()
        self.update()

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

    def hasFocusWrapper(self):
        if self.hasFocus() or self.isSelected():
        # if self.hasFocus():
            return True
        else:
            for value in self.roiMgr.roiItemList:
                roiItem:CanvasROI = value
                if roiItem.hasFocus():
                    return True

            if hasattr(self, 'controllers'):
                for controller in self.controllers:
                    if controller.hasFocus():
                        return True
        return False

    def completeDraw(self):
        if self.isRoiEditableMode():
            self.roiMgr.initRoiItems(self.polygon)

    def wheelEvent(self, event: QWheelEvent) -> None:
        return super().wheelEvent(event)

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

class ZoomComponent(QObject):
    '''缩放组件'''

    signal = pyqtSignal(float)

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

        self.zoomInFactor = 1.25
        self.zoomClamp = False # 是否限制缩放比率
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]

    def TriggerEvent(self, angleDelta):
        '''触发事件'''

        # calculate our zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if angleDelta > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.signal.emit(zoomFactor)