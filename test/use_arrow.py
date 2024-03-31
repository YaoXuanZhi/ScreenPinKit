import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class UICanvasArrowItem(QGraphicsPathItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self.setBrush(QBrush(QColor(255, 0, 0, 100)))
        self.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))

        self.arrowPath = QPainterPath()
        self.points = []

        #箭头的长度
        self.arrowLength = 32.0
        #箭头与线段角度
        self.arrowAngle = 0.5
        #箭身的长度
        self.arrowBodyLength = 18
        #箭身与线段角度
        self.arrowBodyAngle = 0.2  

        self.zoomInFactor = 1.25
        self.zoomClamp = True # 是否限制缩放比率
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]

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
            self.arrowLength = self.arrowLength * zoomFactor
            self.arrowBodyLength = self.arrowBodyLength * zoomFactor

        self.rebuild()

    def rebuild(self):
        self.buildArrow(self.arrowPath, self.points)
        self.setPath(self.arrowPath)

    def buildArrow(self, path:QPainterPath, points:list):
        path.clear()

        begin = points[0]
        end = points[-1]

        x1 = begin.x()                                      # 取 points[0] 起点的 x
        y1 = begin.y()                                      # 取 points[0] 起点的 y  
        x2 = end.x()                                        # 取 points[count-1] 终点的 x  
        y2 = end.y()                                        # 取 points[count-1] 终点的 y  
        # self.arrowLength = 32.0                                            # 箭头的长度  
        # self.arrowAngle = 0.5                                             # 箭头与线段角度  
        x3 = x2 - self.arrowLength * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - self.arrowAngle) # 计算箭头的终点（x3,y3）  
        y3 = y2 - self.arrowLength * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - self.arrowAngle)   
        x4 = x2 - self.arrowLength * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - self.arrowAngle) # 计算箭头的终点（x4,y4）  
        y4 = y2 - self.arrowLength * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - self.arrowAngle)   

        # self.arrowBodyLength = 18                                              # 箭身的长度
        # self.arrowBodyAngle = 0.2                                             # 箭身与线段角度  
        x5 = x2 - self.arrowBodyLength * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - self.arrowBodyAngle) # 计算箭头的终点（x5,y5）  
        y5 = y2 - self.arrowBodyLength * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - self.arrowBodyAngle)   
        x6 = x2 - self.arrowBodyLength * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - self.arrowBodyAngle) # 计算箭头的终点（x6,y6）  
        y6 = y2 - self.arrowBodyLength * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - self.arrowBodyAngle)   

        arrowTailPos = QPointF(x1, y1) # 箭尾位置点
        arrowHeadPos = QPointF(x2, y2) # 箭头位置点
        arrowHeadRightPos = QPointF(x3, y3) # 箭头右侧边缘位置点
        arrowHeadLeftPos = QPointF(x4, y4) # 箭头左侧边缘位置点
        arrowBodyRightPos = QPointF(x5, y5) # 箭身右侧位置点
        arrowBodyLeftPos = QPointF(x6, y6) # 箭身左侧位置点

        path.moveTo(arrowTailPos)
        path.lineTo(arrowBodyLeftPos)
        path.lineTo(arrowHeadLeftPos)
        path.lineTo(arrowHeadPos)
        path.lineTo(arrowHeadRightPos)
        path.lineTo(arrowBodyRightPos)
        path.closeSubpath()

    def buildShape(self, path:QPainterPath, points:list):
        path.clear()

        for i in range(0, len(points)):
            point = points[i]
            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)

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
                    self.pathItem.points.append(targetPos)
                    self.pathItem.rebuild()
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