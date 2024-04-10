import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from canvas_util import *
from canvas_editable_rect import CanvasEditablePath
from pencil_polygon import UICanvasPolygonItem

class UICanvasStarItem(UICanvasCommonPathItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setBrush(QBrush(QColor(255, 0, 0, 100)))
        self.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

    def zoomHandle(self, zoomFactor):
        print(f"待实现缩放 {zoomFactor}")

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def rebuildUI(self):
        self.edgetPoints = CanvasUtil.buildStarPath(self.attachPath, self.points)
        self.setPath(self.attachPath)

    def getEdgePoints(self) -> list:
        return self.edgetPoints

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # # 绘制矩形图元
        # rectItem = QGraphicsRectItem(QRectF(-100, -100, 100, 100))
        # rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        # rectItem.setAcceptHoverEvents(True)
        # self.addItem(rectItem)

        # pathItem = CanvasEditablePath()
        # targetRect = QRectF(300, 300, 150, 100)
        # points = [targetRect.topLeft(), targetRect.topRight(), targetRect.bottomRight(), targetRect.bottomLeft()]
        # for point in points:
        #     pathItem.addPoint(point, Qt.CursorShape.PointingHandCursor)

        # pathItem.addPoint(QPointF(500, 150), Qt.CursorShape.SizeAllCursor)
        # self.addItem(pathItem)

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
                    self.pathItem = UICanvasStarItem()
                    self.scene().addItem(self.pathItem)
                    self.pathItem.points = [targetPos, targetPos]
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
            self.scene().removeItem(self.pathItem)
            self.pathItem = None
            return
        if event.button() == Qt.LeftButton and self.pathItem != None:
            if self.pathItem.points[0] == self.pathItem.points[-1]:
                self.scene().removeItem(self.pathItem)
            else:
                self.pathItem.completeDraw()
                self.pathItem.setEditableState(True)

                # 可编辑边缘和操作点
                pathItem = CanvasEditablePath()
                # pathItem.setEditMode(CanvasEditablePath.FrameEditableMode, False)
                # pathItem.setEditMode(CanvasEditablePath.FocusFrameMode, False)
                pathItem.setEditMode(CanvasEditablePath.RoiEditableMode, False)
                # pathItem.setEditMode(CanvasEditablePath.AdvanceSelectMode, False)

                for point in self.pathItem.getEdgePoints():
                    pathItem.addPoint(point, Qt.CursorShape.PointingHandCursor)
                self.scene().addItem(pathItem)

                # 仅编辑操作带你
                # pathItem = UICanvasPolygonItem(None, True)
                # pathItem.points = self.pathItem.getEdgePoints()
                # pathItem.completeDraw()
                # pathItem.setEditableState(True)
                # self.scene().addItem(pathItem)

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