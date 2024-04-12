import sys, math
from enum import Enum
from PyQt5.QtCore import QObject, QVariant
from PyQt5.QtGui import *
from PyQt5.QtGui import QFocusEvent, QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from canvas_util import *
from use_arrow import UICanvasArrowItem
from pencil_polygon_ex import UICanvasPolygonItem
from canvas_editable_rect import CanvasEditablePath
from use_marker_pen import UICanvasMarkerPen

class DrawActionEnum(Enum):
    DrawNone = "无操作"
    DrawText = "编辑文字"
    DrawLine = "使用画笔"
    ApplyErase = "应用橡皮擦"
    DrawRectangle = "绘制矩形"
    DrawArrow = "绘制箭头"
    DrawStar = "绘制五角星"
    DrawPolygonalLine = "绘制多边形"
    DrawMarkerPen = "使用记号笔"

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.currentDrawActionEnum = DrawActionEnum.DrawNone

        self.pathItem = None

        self.itemList:list = []

        self.initNodes()

    def initNodes(self):
        startPos = QPointF(100, 100)
        endPos = QPointF(300, 300)

        arrowStyleMap = {
            "arrowLength" : 32.0,
            "arrowAngle" : 0.5,
            "arrowBodyLength" : 18,
            "arrowBodyAngle" : 0.2,

            "arrowBrush" : QBrush(QColor(255, 0, 0, 100)),
            "arrowPen" : QPen(QColor(255, 0, 0), 2, Qt.SolidLine),
        }
        # finalPoints = CanvasUtil.buildArrowPath(QPainterPath(), QPolygonF([startPos, endPos]), arrowStyleMap)
        finalPoints = CanvasUtil.buildStarPath(QPainterPath(), QPolygonF([startPos, endPos]))
        pathItem1 = UICanvasCommonPathItem(None, False)
        pathItem1.polygon = QPolygonF(finalPoints)
        pathItem1.setEditableState(True)
        pathItem1.completeDraw()
        self.addItem(pathItem1)

        pathItem2 = UICanvasCommonPathItem(None, True)
        pathItem2.polygon = QPolygonF(finalPoints)
        pathItem2.completeDraw()
        pathItem2.setEditableState(True)
        pathItem2.moveBy(300, 0)
        self.addItem(pathItem2)


    def setEditableState(self, isEditable:bool):
        for item0 in self.itemList:
            if issubclass(type(item0), UICanvasCommonPathItem):
                item:UICanvasCommonPathItem = item0
                item.setEditableState(isEditable)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        view:DrawingView = self.views()[0]
        pos = view.mapFromScene(event.scenePos())
        item = view.itemAt(pos)
        if item != None and self.pathItem != item:
            return super().mousePressEvent(event)
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            if event.button() == Qt.LeftButton:

                # if not self.views()[0].isCanDrag() and (not item or self.pathItem == item or not issubclass(type(item), CanvasROI)):
                if not view.isCanDrag() and (not item or self.pathItem == item or not issubclass(type(item), CanvasROI) or issubclass(type(item), UICanvasCommonPathItem)):
                    targetPos = event.scenePos()

                    if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = UICanvasPolygonItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                        else:
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.update()
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = UICanvasArrowItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawMarkerPen:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = UICanvasMarkerPen()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    # return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            if self.pathItem != None and not self.views()[0].isCanDrag():
                targetPos = event.scenePos()

                if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum == DrawActionEnum.DrawMarkerPen:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
                # return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                if event.button() == Qt.RightButton and self.pathItem != None:
                    if self.pathItem.polygon.count() > 1:
                        self.pathItem.polygon.remove(self.pathItem.polygon.count() - 1)
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                    else:
                        self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
            elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:                
                if event.button() == Qt.RightButton and self.pathItem != None:
                    self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                    # return
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                    # return
            elif self.currentDrawActionEnum == DrawActionEnum.DrawMarkerPen:                
                if event.button() == Qt.RightButton and self.pathItem != None:
                    self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                    # return
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                    # return
            # return
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
        if item == None:
            if(event.button() == Qt.RightButton):
                if self.isCanDrag():
                    self.setEnabled(False)
                else:
                    self.setDragMode(QGraphicsView.RubberBandDrag)
            elif (event.button() == Qt.LeftButton):
                self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        return super().mouseDoubleClickEvent(event)


    def switchCanvas(self):
        if self.isCanDrag():
            self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)

# 拖曳移动窗口类
class QDragWindow(QLabel):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.drag = False

    def isAllowDrag(self):
        return False

    def startDrag(self):
        pass

    def endDrag(self):
        pass

    def mousePressEvent(self, event):
        if not self.isAllowDrag():
            return super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = True
            self.posX, self.posY = event.x(), event.y()
            self.startDrag()

    def mouseReleaseEvent(self, event):
        if not self.isAllowDrag():
            return super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.endDrag()

    def mouseMoveEvent(self, event):
        if not self.isAllowDrag():
            return super().mouseMoveEvent(event)
        if self.isVisible():
            if self.drag:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                self.move(event.x() + self.x() - self.posX, event.y() + self.y() - self.posY)

class MainWindow(QDragWindow):
# class MainWindow(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()
        self.show()
        self.painter = QPainter()
        self.focusColor = QColor(255, 0, 255, 50)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)

    def initActions(self):
        actions = [
            QAction("退出", self, triggered=self.quitDraw, shortcut="esc"),
            QAction("切到画板但无操作", self, triggered=self.showTest, shortcut="ctrl+t"),
            QAction("切换到铅笔", self, triggered=self.drawArrow, shortcut="ctrl+a"),
            QAction("切换到折线", self, triggered=self.usePolygon, shortcut="ctrl+b"),
            QAction("切换到记号笔", self, triggered=self.useMarkerPen, shortcut="ctrl+c"),
            QAction("切换视图操作", self, triggered=self.switchCanvas, shortcut="ctrl+z"),
        ]
        self.addActions(actions)

    def quitDraw(self):
        print("退出绘画模式")
        self.view.setEnabled(False)
        for item in self.view.scene().items():
            if hasattr(item, "roiMgr"):
                roiMgr:CanvasROIManager = item.roiMgr
                roiMgr.setShowState(False)

    def showTest(self):
        print("开启绘画模式")
        self.view.setEnabled(True)

    def switchCanvas(self):
        self.view.switchCanvas()

    def drawArrow(self):
        self.scene.currentDrawActionEnum = DrawActionEnum.DrawArrow
        self.scene.pathItem = None
        self.view.setEnabled(True)

    def usePolygon(self):
        self.scene.currentDrawActionEnum = DrawActionEnum.DrawPolygonalLine
        self.scene.pathItem = None
        self.view.setEnabled(True)

    def useMarkerPen(self):
        self.scene.currentDrawActionEnum = DrawActionEnum.DrawMarkerPen
        self.scene.pathItem = None
        self.view.setEnabled(True)

    def initUI(self):
        self.setStyleSheet("QWidget { background-color: #E3212121; }")
        self.physicalPixmap = QPixmap("screen 300-107.png")
        # self.setPixmap(self.physicalPixmap)

        self.shadowWidth = 20

        finalSize = self.physicalPixmap.size()
        finalSize.setWidth(finalSize.width() + self.shadowWidth)
        finalSize.setHeight(finalSize.height() + self.shadowWidth)
        self.resize(finalSize)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.scene = DrawingScene()
        self.view = DrawingView(self.scene)
        self.layout.addWidget(self.view)

    def isAllowDrag(self):
        return not self.view.isEnabled()

    def paintEvent(self, a0: QPaintEvent) -> None:
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

    	# 阴影
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        self.painter.fillPath(path, QBrush(Qt.white))
        color = self.focusColor

        for i in range(10):
            i_path = QPainterPath()
            i_path.setFillRule(Qt.WindingFill)
            ref = QRectF(self.shadowWidth-i, self.shadowWidth-i, self.width()-(self.shadowWidth-i)*2, self.height()-(self.shadowWidth-i)*2)
            # i_path.addRect(ref)
            i_path.addRoundedRect(ref, 5, 5)
            color.setAlpha(int(150 - i**0.5*50))
            # color.setAlpha(150 - math.sqrt(i) * 50)
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        self.painter.end()

        self.painter.begin(self)
        frameRect = self.rect() - QMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        clipPath = QPainterPath()
        clipPath.addRoundedRect(QRectF(self.rect()), 5, 5)
        self.painter.setClipPath(clipPath)
        self.painter.drawPixmap(frameRect, self.physicalPixmap)
        self.painter.end()

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