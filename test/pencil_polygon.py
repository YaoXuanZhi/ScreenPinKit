import sys, math
from PyQt5.QtCore import QObject, QVariant
from PyQt5.QtGui import *
from PyQt5.QtGui import QFocusEvent, QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from canvas_util import *

class UICanvasPolygonItem(UICanvasCommonPathItem):
    def __init__(self, parent: QWidget = None, isClosePath:bool = False) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle()
        self.isClosePath = isClosePath

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        finalStyleMap = self.styleAttribute.getValue().value()
        finalPen:QPen = finalStyleMap["pen"]

        # 计算缩放比例
        if event.delta() > 0:
            newPenWidth = finalPen.width() + 1
        else:
            newPenWidth = max(1, finalPen.width() - 1)

        finalPen.setWidth(newPenWidth)

        finalStyleMap["pen"] = finalPen
        self.styleAttribute.setValue(QVariant(finalStyleMap))

    def __initStyle(self):
        initPen = QPen(QColor(255, 255, 0, 100))
        initPen.setWidth(32)
        initPen.setCosmetic(True)
        initPen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        initPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrowStyleMap = {
            "pen" : initPen,
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(arrowStyleMap))
        self.styleAttribute.valueChangedSignal.connect(self.update)

    def __initEditMode(self):
        '''仅保Roi操作点'''
        # self.setEditMode(UICanvasCommonPathItem.FrameEditableMode, False)

    # def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
    #     styleMap = self.styleAttribute.getValue().value()
    #     painter.setPen(styleMap["pen"])
    #     painter.drawPath(targetPath)

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pathItem = None

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            if not self.views()[0].isCanDrag():
                targetPos = event.scenePos()
                if self.pathItem == None:
                    self.pathItem = UICanvasPolygonItem()
                    self.addItem(self.pathItem)
                    self.pathItem.points = [targetPos, targetPos]
                else:
                    self.pathItem.points.append(targetPos)
                    self.pathItem.update()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pathItem != None and not self.views()[0].isCanDrag():
            targetPos = event.scenePos()
            self.pathItem.points[-1] = targetPos
            self.pathItem.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.pathItem != None:
            if len(self.pathItem.points) > 2:
                self.pathItem.points = self.pathItem.points[0:-1]
                self.pathItem.completeDraw()
                self.pathItem.setEditableState(True)
            else:
                self.removeItem(self.pathItem)
            self.pathItem = None
            return
        super().mouseReleaseEvent(event)

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

    # def mousePressEvent(self, event: QMouseEvent) -> None:
    #     if event.button() == Qt.LeftButton:
    #         if not self.isCanDrag():
    #             targetPos = self.mapToScene(event.pos())
    #             print(f"------> view {targetPos}")
    #     return super().mousePressEvent(event)

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