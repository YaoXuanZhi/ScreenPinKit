import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
from canvas_util import *

class UICanvasPolygonItem(UICanvasCommonPathItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.initPenStyle()

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        # 计算缩放比例
        if event.delta() > 0:
            self.penWidth = self.penWidth + 1
        else:
            self.penWidth = max(1, self.penWidth - 1)

        self.updatePenStyle()

    def rebuildUI(self):
        CanvasUtil.buildSegmentsPath(self.attachPath, self.points)
        self.setPath(self.attachPath)

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

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            print("添加操作点")
            return
        return super().mouseDoubleClickEvent(event)

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 绘制矩形图元
        rectItem = QGraphicsRectItem(QRectF(-100, -100, 200, 30))
        rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        # rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        rectItem.setAcceptHoverEvents(True)

        # 添加一个线段
        polyonLineItem = UICanvasPolygonItem()
        polyonLineItem.points.append(QPointF(100, 100))
        polyonLineItem.points.append(QPointF(100, 200))
        polyonLineItem.points.append(QPointF(200, 100))
        polyonLineItem.roiMgr.addPoint(QPointF(100, 100))
        polyonLineItem.roiMgr.addPoint(QPointF(100, 200))
        polyonLineItem.roiMgr.addPoint(QPointF(200, 100))
        polyonLineItem.rebuildUI()
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
                    self.pathItem = UICanvasPolygonItem()
                    self.scene().addItem(self.pathItem)
                    self.pathItem.points = [targetPos, targetPos]
                else:
                    self.pathItem.points.append(targetPos)
                    self.pathItem.rebuildUI()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pathItem != None and not self.isCanDrag():
            targetPos = self.mapToScene(event.pos())
            self.pathItem.points[-1] = targetPos
            self.pathItem.rebuildUI()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.pathItem != None:
            if len(self.pathItem.points) > 2:
                self.pathItem.points = self.pathItem.points[0:-1]
                self.pathItem.showControllers()
            else:
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