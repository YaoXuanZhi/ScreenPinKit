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
    '''
    绘图工具-五角星图元
    '''
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle()

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

    def __initStyle(self):
        self.defaultPenWidth = 3
        styleMap = {
            "brush" : QBrush(QColor(255, 0, 0, 100)),
            "pen" : QPen(QColor(255, 0, 0), self.defaultPenWidth, Qt.SolidLine),
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.update)

    def __initEditMode(self):
        '''仅保留边框操作点'''
        self.setEditMode(UICanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(UICanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(UICanvasCommonPathItem.AdvanceSelectMode, False)

    def zoomHandle(self, zoomFactor):
        finalStyleMap = self.styleAttribute.getValue().value()

        finalBrush:QBrush = finalStyleMap["brush"]
        finalBrushColor = finalBrush.color()
        finalBrushColor.setAlpha(int(100 * zoomFactor * 1.2))
        finalBrush.setColor(finalBrushColor)
        finalStyleMap["brush"] = finalBrush

        finalPen:QPen = finalStyleMap["pen"]
        finalPenColor = finalPen.color()
        finalPenColor.setAlpha(int(100 * zoomFactor * 1.4))
        finalPen.setColor(finalPenColor)
        finalPenWidth = finalPen.width()
        finalPenWidth = int(self.defaultPenWidth * zoomFactor)
        finalPen.setWidth(finalPenWidth)
        finalStyleMap["pen"] = finalPen

        self.styleAttribute.setValue(QVariant(finalStyleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        arrowStyleMap = self.styleAttribute.getValue().value()
        painter.setBrush(arrowStyleMap["brush"])
        painter.setPen(arrowStyleMap["pen"])
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildStarPath(targetPath, targetPolygon)

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

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
                    self.pathItem.polygon.append(targetPos)
                    self.pathItem.polygon.append(targetPos)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pathItem != None and not self.isCanDrag():
            targetPos = self.mapToScene(event.pos())
            self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
            self.pathItem.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.pathItem != None:
            self.scene().removeItem(self.pathItem)
            self.pathItem = None
            return
        if event.button() == Qt.LeftButton and self.pathItem != None:
            if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                self.scene().removeItem(self.pathItem)
            else:
                self.pathItem.completeDraw()
                self.pathItem.setEditableState(True)
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