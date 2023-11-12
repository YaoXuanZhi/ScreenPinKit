from enum import Enum
import math
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QPainterPath, QBrush, QImage, QTransform, QVector2D, QVector3D
from PyQt5.QtCore import Qt, QRect, QSize, QRectF, QPointF, QVariant
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneHoverEvent
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget

class CanvasEditAction(Enum):
    '''编辑行为枚举'''
    DoNothing = "啥都不做"
    Move = "移动"
    Resize = "重置大小"
    Rotate = "旋转"
    EdgeChange = "边缘调整"

class CanvasItemEditor():
    '''图元编辑类'''
    PI = 3.14159265358979

    m_closeIcon = QImage()
    m_resizeIcon = QImage()
    m_rotateIcon = QImage()

    m_isResizeable = True
    m_isRatioScale = False

    m_ratioValue = 1.0

    m_pos = QPointF() # 本地坐标点击的点
    m_pressedPos = QPointF() # 场景坐标点击的点
    m_startPos = QPointF() # Item在场景的起始坐标
    m_transform:QTransform = None # 交换矩阵
    m_rotate = 0.0 # 当前旋转角度
    m_nInterval = 20
    m_nEllipseWidth = 12 # 半径

    m_cPenColor = QColor(255, 0, 0)
    m_nPenWidth = 1
    m_cBrushColor = QColor(200, 100, 100)

    m_itemAction = CanvasEditAction.DoNothing # 当前编辑行为

    def __init__(self, graphicsItem:QGraphicsItem) -> None:
        self.m_closePixmap = QPixmap()
        self.m_resizePixmap = QPixmap()
        self.m_rotatePixmap = QPixmap()
        self.m_size = QSize()
        self.initIcon()

        self.targetItem = graphicsItem
        self.targetItem.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable)

    def initIcon(self):
        if (self.m_closeIcon.isNull()):
            self.m_closeIcon.load("./Images/close.png")
        if (self.m_resizeIcon.isNull()):
            self.m_resizeIcon.load("./Images/resize.png")
        if (self.m_rotateIcon.isNull()):
            self.m_rotateIcon.load("./Images/rotate.png")

        self.m_closePixmap = QPixmap.fromImage(self.m_closeIcon)
        self.m_resizePixmap = QPixmap.fromImage(self.m_resizeIcon)
        self.m_rotatePixmap = QPixmap.fromImage(self.m_rotateIcon)

    def setItemResizeable(self, resizeable:bool):
        self.m_isResizeable = resizeable

    def setItemResizeRatio(self, resizeRation:bool, rationValue:float):
        self.m_isRatioScale = resizeRation
        self.m_ratioValue = rationValue

    def getDistance(self, p1:QPointF, p2:QPointF):
        distance:float = math.sqrt((p1.x() - p2.x()) * (p1.x() - p2.x()) + \
                          (p1.y() - p2.y()) * (p1.y() - p2.y()))
        return distance

    def getCustomRect(self) -> QRectF:
        centerPos = QPointF(0, 0)
        return QRectF(centerPos.x() - self.m_size.width() / 2, centerPos.y() - self.m_size.height() / 2, \
                    self.m_size.width(), self.m_size.height())

    def mouseMoveMoveOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        xInterval:float = scenePos.x() - self.m_pressedPos.x()
        yInterval:float = scenePos.y() - self.m_pressedPos.y()
 
        self.targetItem.setPos(self.m_startPos + QPointF(xInterval, yInterval))
        self.targetItem.update()

    def mouseMoveResizeOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        if (not self.m_isResizeable):
            return
 
        ratio:float = self.m_ratioValue
        itemWidth:float = abs(localPos.x()) * 2 - self.m_nInterval - self.m_nEllipseWidth
        itemHeight:float = abs(localPos.y()) * 2 - self.m_nInterval - self.m_nEllipseWidth
        if (self.m_isRatioScale):
            itemHeight = itemWidth * 1.0 / ratio
 
        # 设置图片的最小大小为10
        if (itemWidth < 10 or itemHeight < 10):
            return
 
        self.m_size = QSize(itemWidth, itemHeight)
        self.targetItem.update()

    def mouseMoveRotateOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        # 获取并设置为单位向量
        startVec = QVector2D(self.m_pos.x() - 0, self.m_pos.y() - 0)
        startVec.normalize()
        endVec = QVector2D(localPos.x() - 0, localPos.y() - 0)
        endVec.normalize()
 
        # 单位向量点乘，计算角度
        dotValue:float = QVector2D.dotProduct(startVec, endVec)
        if (dotValue > 1.0):
            dotValue = 1.0
        elif (dotValue < -1.0):
            dotValue = -1.0
 
        dotValue = math.acos(dotValue)
        if (math.isnan(dotValue)):
            dotValue = 0.0
 
        # 获取角度
        angle:float = dotValue * 1.0 / (self.PI / 180)
 
        # 向量叉乘获取方向
        crossValue:QVector3D = QVector3D.crossProduct(QVector3D(startVec, 1.0),QVector3D(endVec, 1.0))
        if (crossValue.z() < 0):
            angle = -angle
        self.m_rotate += angle
 
        # 设置变化矩阵
        self.m_transform.rotate(self.m_rotate)
        self.targetItem.setTransform(self.m_transform)
 
        self.m_pos = localPos
        self.targetItem.update()

    def boundingRect(self) -> QRectF:
        rectF:QRectF = self.getCustomRect()
        if not self.targetItem.isSelected():
            return rectF

        rectF.adjust(-self.m_nInterval, -self.m_nInterval, self.m_nInterval, self.m_nInterval)
        rectF.adjust(-self.m_nEllipseWidth, -self.m_nEllipseWidth, self.m_nEllipseWidth, self.m_nEllipseWidth)

        return rectF

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.m_transform = self.targetItem.transform()
 
        itemRect:QRectF = self.getCustomRect()
        outLintRect:QRectF = itemRect.adjusted(-self.m_nInterval, -self.m_nInterval, self.m_nInterval, self.m_nInterval)
 
        # 获取当前模式
        pos:QPointF = event.pos()
        scenePos:QPointF = event.scenePos()
        if (self.getDistance(pos, outLintRect.topRight()) <= self.m_nEllipseWidth):
            # self.targetItem.onClickedCopyItem()
            print("复制并粘贴")
        elif (self.getDistance(pos, outLintRect.bottomLeft()) <= self.m_nEllipseWidth):
            self.m_itemAction = CanvasEditAction.Rotate
            self.targetItem.setCursor(Qt.SizeAllCursor)
        elif (self.getDistance(pos, outLintRect.bottomRight()) <= self.m_nEllipseWidth):
            self.m_itemAction = CanvasEditAction.Resize
            self.targetItem.setCursor(Qt.OpenHandCursor)
        elif (self.boundingRect().contains(pos)):
            self.m_itemAction = CanvasEditAction.Move
            self.targetItem.setCursor(Qt.SizeAllCursor)
 
        # 保存当前的一些信息
        self.m_pos = pos
        self.m_pressedPos = scenePos
        self.m_startPos = self.targetItem.pos()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # 获取场景坐标和本地坐标
        scenePos:QPointF = event.scenePos()
        pos:QPointF = event.pos()
 
        if self.m_itemAction == CanvasEditAction.Move:
            # 处理移动
            self.mouseMoveMoveOperator(scenePos, pos)
        elif self.m_itemAction == CanvasEditAction.Resize:
            # 处理更改大小
            self.mouseMoveResizeOperator(scenePos, pos)
        elif self.m_itemAction == CanvasEditAction.Rotate:
            # 处理旋转
            self.mouseMoveRotateOperator(scenePos, pos)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.m_itemAction = CanvasEditAction.DoNothing
        self.targetItem.setCursor(Qt.ArrowCursor)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        if not self.targetItem.isSelected():
            return

        painter.save()

        pen = QPen(self.m_cPenColor, self.m_nPenWidth, Qt.DashLine)
        painter.setPen(pen)

        itemRect:QRectF = self.getCustomRect()

        # 绘制轮廓线
        outLineRect:QRectF = itemRect.adjusted(-self.m_nInterval, -self.m_nInterval, self.m_nInterval, self.m_nInterval)
        painter.drawRect(outLineRect)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.m_cBrushColor)

        # 绘制控制点
        painter.drawEllipse(outLineRect.topRight(), self.m_nEllipseWidth, self.m_nEllipseWidth)

        if not self.m_closePixmap.isNull():
            painter.drawPixmap(QRect(outLineRect.topRight().x() - self.m_nEllipseWidth / 2, \
                                  outLineRect.topRight().y() - self.m_nEllipseWidth / 2, \
                                  self.m_nEllipseWidth, self.m_nEllipseWidth), self.m_closePixmap)

        painter.drawEllipse(outLineRect.bottomLeft(), self.m_nEllipseWidth, self.m_nEllipseWidth)
        if not self.m_rotatePixmap.isNull():
            painter.drawPixmap(QRect(outLineRect.bottomLeft().x() - self.m_nEllipseWidth / 2, \
                                  outLineRect.bottomLeft().y() - self.m_nEllipseWidth / 2, \
                                  self.m_nEllipseWidth, self.m_nEllipseWidth), self.m_rotatePixmap)
 
        painter.drawEllipse(outLineRect.bottomRight(), self.m_nEllipseWidth, self.m_nEllipseWidth)
        if not self.m_resizePixmap.isNull():
            painter.drawPixmap(QRect(outLineRect.bottomRight().x() - self.m_nEllipseWidth / 2, \
                                    outLineRect.bottomRight().y() - self.m_nEllipseWidth / 2, \
                                    self.m_nEllipseWidth, self.m_nEllipseWidth), self.m_resizePixmap)
        painter.restore()