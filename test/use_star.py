import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class CanvasROI(QGraphicsEllipseItem):
    def __init__(self, hoverCursor:QCursor, id:int, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.hoverCursor = hoverCursor
        self.id = id
        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = False
        parentItem:UICanvasArrowItem = self.parentItem()
        parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.isMoving:
            parentItem:UICanvasArrowItem = self.parentItem()
            localPos = self.mapToItem(parentItem, self.rect().center())
            parentItem.roiMgr.movePointById(self, localPos)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:UICanvasArrowItem = self.parentItem()
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

class UICanvasArrowItem(QGraphicsPathItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.setBrush(QBrush(QColor(255, 0, 0, 100)))
        self.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))

        self.arrowPath = QPainterPath()
        self.points = []

        self.zoomInFactor = 1.25
        self.zoomClamp = True # 是否限制缩放比率
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        self.roiMgr = CanvasROIManager(attachParent=self)

        self.roiMgr.removeROIAfterSignal.connect(self.removeROIAfterCallback)
        self.roiMgr.moveROIAfterSignal.connect(self.moveROIAfterCallback)

    def removeROIAfterCallback(self, index:int):
        self.points.remove(self.points[index])
        self.endResize(None)

    def moveROIAfterCallback(self, index:int, localPos:QPointF):
        self.prepareGeometryChange()
        self.points[index] = localPos
        self.rebuild()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        zoomOutFactor = 1 / self.zoomInFactor

        # 计算缩放比例
        if event.delta() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.zoomClamp is False:
            print("待实现缩放")

        self.rebuild()

    def rebuild(self):
        self.buildStar(self.arrowPath, self.points)
        self.setPath(self.arrowPath)

    def showControllers(self):
        '''生成操作点'''

        for i in range(0, len(self.points)):
            point:QPoint = self.points[i]
            self.roiMgr.addPoint(point)

        self.isShowController = True
        self.rebuild()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        for roiItem in self.roiMgr.roiItemList:
            roiItem.show()
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        for roiItem in self.roiMgr.roiItemList:
            roiItem.hide()
        return super().hoverLeaveEvent(event)

    def buildStar(self, path:QPainterPath, points:list):
        path.clear()

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
        path.moveTo(B)
        path.lineTo(F)
        path.lineTo(A)
        path.lineTo(J)
        path.lineTo(E)
        path.lineTo(I)
        path.lineTo(D)
        path.lineTo(H)
        path.lineTo(C)
        path.lineTo(G)
        path.lineTo(B)
        path.closeSubpath()

    def endResize(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()
        self.rebuild()

        rect = self.arrowPath.boundingRect()
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

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 绘制矩形图元
        rectItem = QGraphicsRectItem(QRectF(-100, -100, 100, 100))
        rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        rectItem.setAcceptHoverEvents(True)
        self.addItem(rectItem)

class DrawingView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.RubberBandDrag)

        self.pathItem = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.isCanDrag():
                targetPos = self.mapToScene(event.pos())
                if self.pathItem == None:
                    self.pathItem = UICanvasArrowItem()
                    self.scene().addItem(self.pathItem)
                    self.pathItem.points = [targetPos, targetPos]
                else:
                    self.pathItem.showControllers()
                    self.pathItem = None
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pathItem != None and not self.isCanDrag():
            targetPos = self.mapToScene(event.pos())
            self.pathItem.points[-1] = targetPos
            self.pathItem.rebuild()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.pathItem != None:
            self.scene().removeItem(self.pathItem)
            self.pathItem = None
            return
        super().mouseReleaseEvent(event)

    def isCanDrag(self):
        '''判断当前是否可以拖曳图元'''
        matchMode = self.dragMode()
        return (matchMode | QGraphicsView.RubberBandDrag == matchMode)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if(event.button() == Qt.RightButton):
            self.setDragMode(QGraphicsView.RubberBandDrag)
        elif (event.button() == Qt.LeftButton):
            self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        return super().mouseDoubleClickEvent(event)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.show()

    def initUI(self):
        self.setStyleSheet("QWidget { background-color: #E3212121; }")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.scene = DrawingScene()
        view = DrawingView(self.scene)
        self.layout.addWidget(view)

    def paintEvent(self, a0: QPaintEvent) -> None:
        backgroundPath = QPainterPath()
        backgroundPath.setFillRule(Qt.WindingFill)

        return super().paintEvent(a0)

if __name__ == '__main__':
    import sys
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)

    wnd = MainWindow()

    sys.exit(app.exec_())