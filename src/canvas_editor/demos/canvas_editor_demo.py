import sys, os
from enum import Enum
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from canvas_item import *

class DrawActionEnum(Enum):
    DrawNone = "无操作"
    EditText = "编辑文字"
    UsePencil = "使用画笔"
    UseEraser = "使用橡皮擦"
    UseMarkerPen = "使用记号笔"
    UseMarkerItem = "使用标记"
    PasteSvg = "粘贴图案"

    DrawRectangle = "绘制矩形"
    DrawEllipse = "绘制椭圆"
    DrawArrow = "绘制箭头"
    DrawStar = "绘制五角星"
    DrawPolygonalLine = "绘制折线"

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.currentDrawActionEnum = DrawActionEnum.DrawNone

        self.pathItem = None

        self.itemList:list = []

    def initNodes(self):
        targetRect = QRectF(QPointF(0, 0), QSizeF(100, 100))
        targetPoint = self.views()[0].rect().center()
        targetRect.moveCenter(targetPoint/-2)

        arrowStyleMap = {
            "arrowLength" : 32.0,
            "arrowAngle" : 0.5,
            "arrowBodyLength" : 18,
            "arrowBodyAngle" : 0.2,

            "arrowBrush" : QBrush(QColor(255, 0, 0, 100)),
            "arrowPen" : QPen(QColor(255, 0, 0), 2, Qt.SolidLine),
        }
        # finalPoints = CanvasUtil.buildArrowPath(QPainterPath(), QPolygonF([targetRect.topLeft(), targetRect.bottomRight()]), arrowStyleMap)
        finalPoints = CanvasUtil.buildStarPath(QPainterPath(), QPolygonF([targetRect.topLeft(), targetRect.bottomRight()]))
        pathItem1 = CanvasCommonPathItem(None, False)
        pathItem1.polygon = QPolygonF(finalPoints)
        pathItem1.setEditableState(True)
        pathItem1.completeDraw()
        self.addItem(pathItem1)

        pathItem2 = CanvasCommonPathItem(None, True)
        pathItem2.polygon = QPolygonF(finalPoints)
        pathItem2.completeDraw()
        pathItem2.setEditableState(True)
        pathItem2.moveBy(300, 0)
        self.addItem(pathItem2)

        pathItem3 = CanvasEditablePath(None, False)
        pathItem3.addPoint(QPointF(0, 0), Qt.SizeAllCursor)
        pathItem3.addPoint(QPointF(50, 50), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(200, 200), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(0, 380), Qt.SizeAllCursor)
        pathItem3.update()
        pathItem3.setPos(targetPoint/-2)
        self.addItem(pathItem3)

    def setEditableState(self, isEditable:bool):
        for item0 in self.itemList:
            if issubclass(type(item0), CanvasCommonPathItem):
                item:CanvasCommonPathItem = item0
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
                if not view.isCanDrag() and (not item or self.pathItem == item or not issubclass(type(item), CanvasROI) or issubclass(type(item), CanvasCommonPathItem)):
                    targetPos = event.scenePos()

                    if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasLineStripItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                        else:
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.update()
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasArrowItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasMarkerPen()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
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
                elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
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
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
            elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:                
                if event.button() == Qt.RightButton and self.pathItem != None:
                    self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
        super().mouseReleaseEvent(event)

class DrawingView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = True
        self.zoomComponent.signal.connect(self.zoomHandle)

    def zoomHandle(self, zoomFactor):
        self.scale(zoomFactor, zoomFactor)

    def initUI(self):
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border:0px;")
        self.setRenderHint(QPainter.Antialiasing)

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
                self.switchCanvas()
            return
        return super().mouseDoubleClickEvent(event)

    def switchCanvas(self):
        if self.isCanDrag():
            self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event: QWheelEvent):
        # 检查滚轮事件是否在某个GraphicsItem上发生
        item = self.itemAt(event.pos())
        if item == None or not item.isSelected():
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        return super().wheelEvent(event)

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
            QAction("切到画板但无操作", self, triggered=self.swtichOption, shortcut="ctrl+w"),
            QAction("切换到演示模式", self, triggered=self.swtichShow, shortcut="alt+w"),
            QAction("切到画板但无操作", self, triggered=self.startDraw, shortcut="ctrl+t"),
            QAction("切换到箭头", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow), shortcut="alt+1"),
            QAction("切换到折线", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawPolygonalLine), shortcut="alt+2"),
            QAction("切换到记号笔", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.UseMarkerPen), shortcut="alt+3"),
            QAction("切换多选操作", self, triggered=self.switchCanvas, shortcut="alt+4"),
        ]
        self.addActions(actions)

    def quitDraw(self):
        if self.view.isEnabled():
            self.view.setEnabled(False)
            for item in self.view.scene().items():
                if hasattr(item, "roiMgr"):
                    roiMgr:CanvasROIManager = item.roiMgr
                    roiMgr.setShowState(False)
        else:
            sys.exit(0)

    def swtichOption(self):
        color = QColor(Qt.GlobalColor.yellow)
        color.setAlpha(1)
        self.scene.setBackgroundBrush(QBrush(color))

    def swtichShow(self):
        self.scene.setBackgroundBrush(QBrush(Qt.NoBrush))

    def startDraw(self):
        self.view.setEnabled(True)

    def switchCanvas(self):
        self.view.switchCanvas()

    def switchDrawTool(self, drawActionEnum:DrawActionEnum):
        self.scene.currentDrawActionEnum = drawActionEnum
        self.scene.pathItem = None
        self.view.setEnabled(drawActionEnum != DrawActionEnum.DrawNone)

    def initUI(self):
        self.contentLayout = QVBoxLayout(self)
        self.shadowWidth = 10

        # # 桌面标注模式
        # self.physicalPixmap = QPixmap()

        # 截图标注模式
        imagePath = os.path.join(os.path.dirname(__file__), "screen 143-313.png")
        self.physicalPixmap = QPixmap(imagePath)

        if self.physicalPixmap.isNull():
            finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
            self.screenPixmap = finalPixmap
            self.setGeometry(finalGeometry)
            self.contentLayout.setContentsMargins(0, 0, 0, 0)
        else:
            self.setPixmap(self.physicalPixmap)

            finalSize = self.physicalPixmap.size()
            finalSize.setWidth(finalSize.width() + self.shadowWidth)
            finalSize.setHeight(finalSize.height() + self.shadowWidth)
            self.resize(finalSize)
            self.contentLayout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

        self.scene = DrawingScene()
        if self.physicalPixmap.isNull():
            color = QColor(Qt.GlobalColor.yellow)
            color.setAlpha(1)
            self.scene.setBackgroundBrush(QBrush(color))
        self.view = DrawingView(self.scene)
        self.contentLayout.addWidget(self.view)

        self.scene.initNodes()

    def isAllowDrag(self):
        return not self.view.isEnabled()

    def paintEvent(self, a0: QPaintEvent) -> None:
        if self.physicalPixmap.isNull():
            return super().paintEvent(a0)

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