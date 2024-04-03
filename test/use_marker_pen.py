import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QFocusEvent, QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget

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
        parentItem:UICanvasGlowPathItem = self.parentItem()
        parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        parentItem:UICanvasGlowPathItem = self.parentItem()
        localPos = self.mapToItem(parentItem, self.rect().center())
        parentItem.roiMgr.movePointById(self, localPos)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:UICanvasGlowPathItem = self.parentItem()
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

class UICanvasGlowPathItem(QGraphicsPathItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setDefaultFlag()
        self.initPenStyle()

        self.glowPath = QPainterPath()
        self.points = []

        self.isShowController = False
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

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        # 计算缩放比例
        if event.delta() > 0:
            self.penWidth = self.penWidth + 1
        else:
            self.penWidth = max(1, self.penWidth - 1)

        self.updatePenStyle()

    def rebuild(self):
        # if self.isShowController:
        #     self.buildShape2(self.glowPath, self.roiItemList)
        # else:
        #     self.buildShape(self.glowPath, self.points)

        self.buildShape(self.glowPath, self.points)
        self.setPath(self.glowPath)

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

    def buildShape(self, path:QPainterPath, points:list):
        path.clear()

        for i in range(0, len(points)):
            point = points[i]
            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)

    def buildShape2(self, path:QPainterPath, roiItemList:list):
        path.clear()

        for i in range(0, len(roiItemList)):
            roiItem:CanvasROI = roiItemList[i]
            # targetPos = roiItem.boundingRect().center()
            targetPos = roiItem.sceneBoundingRect().center()
            if i == 0:
                path.moveTo(targetPos)
            else:
                path.lineTo(targetPos)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

    def initPenStyle(self):
        self.usePen = QPen()
        self.penWidth = 32
        self.penColor = QColor(255, 255, 0, 100)
        self.updatePenStyle()

    def updatePenStyle(self):
        self.usePen.setWidth(self.penWidth)
        self.usePen.setCosmetic(True)
        self.usePen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.usePen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.usePen.setColor(self.penColor)
        self.setPen(self.usePen)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            print("添加操作点")
            return
        return super().mouseDoubleClickEvent(event)

    def endResize(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()
        self.rebuild()

        rect = self.glowPath.boundingRect()
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
        rectItem = QGraphicsRectItem(QRectF(-100, -100, 200, 30))
        # rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        rectItem.setAcceptHoverEvents(True)

        # 添加一个线段
        polyonLineItem = UICanvasGlowPathItem()
        polyonLineItem.points.append(QPointF(100, 100))
        polyonLineItem.points.append(QPointF(100, 200))
        polyonLineItem.points.append(QPointF(200, 100))
        polyonLineItem.roiMgr.addPoint(QPointF(100, 100))
        polyonLineItem.roiMgr.addPoint(QPointF(100, 200))
        polyonLineItem.roiMgr.addPoint(QPointF(200, 100))
        polyonLineItem.rebuild()
        self.addItem(polyonLineItem)

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
                    self.pathItem = UICanvasGlowPathItem()
                    self.scene().addItem(self.pathItem)
                    self.pathItem.points = [targetPos, targetPos]
                else:
                    self.pathItem.showControllers()
                    self.pathItem.setFocus(Qt.FocusReason.OtherFocusReason)
                    # self.pathItem.setSelected(True)
                    # self.pathItem.focusInEvent(None)
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
        item = self.itemAt(event.pos())
        if item != None:
            return
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