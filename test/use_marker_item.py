import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, QStyleOptionGraphicsItem, QWidget
from PyQt5.QtSvg import QSvgWidget

class UICanvasTextItem(QGraphicsTextItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

        self.setDefaultFlag()
        self.setDefaultTextColor(Qt.white)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        # outline
        # path_outline = QPainterPath()
        # path_outline.addRoundedRect(self.boundingRect(), self.edge_size, self.edge_size)
        # painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        # painter.setBrush(Qt.NoBrush)
        # painter.drawPath(path_outline.simplified())
        # self.pathItem.setBrush(QBrush(QColor(255, 255, 0, 50)))  # Yellow fill with alpha 50
        # painter.fillRect(self.boundingRect(), Qt.yellow)
        painter.fillRect(self.boundingRect(), QBrush(QColor(255, 255, 0, 50)))

        painter.restore()
        return super().paint(painter, option, widget)

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 绘制矩形图元
        rectItem = QGraphicsRectItem(QRectF(-100, -100, 100, 100))
        rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        rectItem.setAcceptHoverEvents(True)
        self.addItem(rectItem)

        # 绘制箭头图元
        self.addArrow(QPoint(120, 120), QPoint(200, 200))

    def addArrow(self, begin:QPoint, end:QPoint):
        x1 = begin.x()                                      # 取 points[0] 起点的 x
        y1 = begin.y()                                      # 取 points[0] 起点的 y  
        x2 = end.x()                                        # 取 points[count-1] 终点的 x  
        y2 = end.y()                                        # 取 points[count-1] 终点的 y  
        l = 32.0                                            # 箭头的长度  
        a = 0.5                                             # 箭头与线段角度  
        x3 = x2 - l * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - a) # 计算箭头的终点（x3,y3）  
        y3 = y2 - l * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - a)   
        x4 = x2 - l * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - a) # 计算箭头的终点（x4,y4）  
        y4 = y2 - l * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - a)   

        i = 18                                              # 箭身的长度
        b = 0.2                                             # 箭身与线段角度  
        x5 = x2 - i * math.cos(math.atan2((y2 - y1) , (x2 - x1)) - b) # 计算箭头的终点（x5,y5）  
        y5 = y2 - i * math.sin(math.atan2((y2 - y1) , (x2 - x1)) - b)   
        x6 = x2 - i * math.sin(math.atan2((x2 - x1) , (y2 - y1)) - b) # 计算箭头的终点（x6,y6）  
        y6 = y2 - i * math.cos(math.atan2((x2 - x1) , (y2 - y1)) - b)   

        arrowTailPos = QPointF(x1, y1) # 箭尾位置点
        arrowHeadPos = QPointF(x2, y2) # 箭头位置点
        arrowHeadRightPos = QPointF(x3, y3) # 箭头右侧边缘位置点
        arrowHeadLeftPos = QPointF(x4, y4) # 箭头左侧边缘位置点
        arrowBodyRightPos = QPointF(x5, y5) # 箭身右侧位置点
        arrowBodyLeftPos = QPointF(x6, y6) # 箭身左侧位置点

        fullPath = QPainterPath()
        fullPath.moveTo(arrowTailPos)
        fullPath.lineTo(arrowBodyLeftPos)
        fullPath.lineTo(arrowHeadLeftPos)
        fullPath.lineTo(arrowHeadPos)
        fullPath.lineTo(arrowHeadRightPos)
        fullPath.lineTo(arrowBodyRightPos)
        fullPath.closeSubpath()

        pathItem = QGraphicsPathItem(fullPath)
        pathItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        pathItem.setAcceptHoverEvents(True)
        self.addItem(pathItem)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        # 检查滚轮事件是否在 UICanvasTextItem 上发生
        # item = self.itemAt(event.scenePos(), Qt.NoModifier)
        if len(self.selectedItems()) < 1:
            return super().wheelEvent(event)
        else:
            selectItem = self.selectedItems()[0]
            return
        # if item and isinstance(item, UICanvasTextItem):
        #     item.wheelEvent(event)
        #     # 接受事件，防止它被传递到其他处理器
        #     event.accept()
        # else:
        #     # 如果不是在 QGraphicsTextItem 上，调用默认的处理方法
        #     # self.wheelEventView(event)
        #     return super().wheelEvent(event)


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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if not self.isCanDrag():
                item = self.itemAt(event.pos())
                if item == None:
                    self.currentItem = UICanvasTextItem()
                    self.currentItem.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
                    self.currentItem.setAcceptHoverEvents(True)
                    self.currentItem.setPlainText("1")
                    self.scene().addItem(self.currentItem)

                    targetPos = self.mapToScene(event.pos())
                    targetPos.setX(targetPos.x() - self.currentItem.boundingRect().width() / 2)
                    targetPos.setY(targetPos.y() - self.currentItem.boundingRect().height() / 2)
                    self.currentItem.setPos(targetPos)

        return super().mousePressEvent(event)

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

    # def wheelEvent(self, event:QWheelEvent):
    #     # 检查滚轮事件是否在 UICanvasTextItem 上发生
    #     # item = self.itemAt(event.pos())
    #     # if item and isinstance(item, UICanvasTextItem):
    #     #     item.wheelEventHandle(event)
    #     #     # 接受事件，防止它被传递到其他处理器
    #     #     event.accept()
    #     # else:
    #         # 如果不是在 QGraphicsTextItem 上，调用默认的处理方法
    #     super().wheelEvent(event)    

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