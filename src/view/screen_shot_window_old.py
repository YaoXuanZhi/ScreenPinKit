# coding=utf-8
from canvas_item import *
from canvas_item.canvas_util import CanvasUtil
from base import *

class ScreenShotView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initStyle()

    def initStyle(self):
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border:0px;")
        self.setRenderHint(QPainter.Antialiasing)

class ScreenShotScene(QGraphicsScene):
    exitSignal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sceneRectChanged.connect(self.onSceneRectChanged)
        self.maskLayer:QGraphicsItem = None
        self.currentItem:CanvasCommonPathItem = None
        self.lastAddItem:CanvasCommonPathItem = None
        self.isApplyExpandArea:bool = False

    def reset(self):
        if self.lastAddItem != None:
            self.clear()
            self.lastAddItem = None
            self.maskLayer = None
            self.onSceneRectChanged(QRectF())

    def isCapturing(self):
        return self.lastAddItem != None

    def onSceneRectChanged(self, _rect:QRectF):
        rect = self.sceneRect()
        if self.maskLayer == None:
            self.maskLayer = CanvasMaskItem(QColor(0, 0, 0, 150))
            self.addItem(self.maskLayer)
        self.maskLayer.setRect(rect)

    def applyExpandArea(self, pos:QPointF):
        self.isApplyExpandArea = True
        finalPolygon = QPolygonF(self.lastAddItem.polygon)
        finalPolygon.append(pos)
        finalRect = finalPolygon.boundingRect()
        self.lastAddItem.polygon = QPolygonF(finalRect)
        self.update()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self.currentItem != None:
            targetPos = event.scenePos()
            self.currentItem.polygon.replace(self.currentItem.polygon.count() - 1, targetPos)
            self.currentItem.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.cancelScreenShot()
            return

        item = None
        itemList = self.items(event.scenePos())
        if len(itemList) > 0:
            item = itemList[0]

        isSkip = False
        if item == self.lastAddItem and item != None:
            isSkip = True
        if item != None and CanvasUtil.isRoiItem(item):
            isSkip = True
        if self.lastAddItem != None:
            isSkip = True

        if isSkip:
            # if self.lastAddItem != None and event.button() == Qt.LeftButton:
            #     isHit = self.lastAddItem.contains(event.scenePos())
            #     if not isHit:
            #         self.applyExpandArea(event.scenePos())
            return super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            targetPos = event.scenePos()
            if self.currentItem == None:
                self.currentItem = CanvasPasteImageItem(bgBrush=self.backgroundBrush())
                self.currentItem.setEditableState(True)
                self.addItem(self.currentItem)
                self.currentItem.polygon.append(targetPos)
                self.currentItem.polygon.append(targetPos)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if self.currentItem != None:
            if event.button() == Qt.RightButton:
                self.removeItem(self.currentItem)
                self.currentItem = None
            elif event.button() == Qt.LeftButton:
                if self.currentItem.polygon.at(0) == self.currentItem.polygon.at(1):
                    self.removeItem(self.currentItem)
                else:
                    self.currentItem.completeDraw()
                    self.currentItem.setFocus(Qt.FocusReason.OtherFocusReason)
                    self.lastAddItem = self.currentItem
                self.currentItem = None

        if self.isApplyExpandArea:
            self.isApplyExpandArea = False
            self.lastAddItem.refreshTransformOriginPoint()
        super().mouseReleaseEvent(event)

    def cancelScreenShot(self):
        if self.lastAddItem != None:  # 清空已划定的的截图区域
            self.reset()
        else:
            self.exitSignal.emit()

class ScreenShotWindow(QWidget):
    snipedSignal = pyqtSignal(QPoint, QSize, QPixmap)
    closedSignal = pyqtSignal()
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()
        self.painter = QPainter()
        self.registerListen()
        self.setWindowOpacity(0.5)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def initUI(self):
        self.scene = ScreenShotScene()
        self.view = ScreenShotView(self.scene)
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.addWidget(self.view)

    def registerListen(self):
        self.scene.exitSignal.connect(lambda: self.close())

    def initActions(self):
        actions = [
            QAction(parent=self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            QAction(parent=self, triggered=self.snip, shortcut="ctrl+t"),
            QAction(parent=self, triggered=self.cancelScreenShot, shortcut="esc"),
        ]
        self.addActions(actions)

    def toPhysicalRectF(self, rectf:QRectF):
        '''计算划定的截图区域的（缩放倍率1.0的）原始矩形（会变大）
        rectf：划定的截图区域的矩形。可为QRect或QRectF'''
        pixelRatio = self.screenPixmap.devicePixelRatio()
        return QRectF(rectf.x() * pixelRatio, rectf.y() * pixelRatio,
                      rectf.width() * pixelRatio, rectf.height() * pixelRatio)

    def copyToClipboard(self):
        if not self.scene.isCapturing():
            return
        cropRect = self.scene.lastAddItem.sceneBoundingRect()
        realCropRect = self.toPhysicalRectF(cropRect).toRect()
        if realCropRect.size() != QSize(0, 0):
            cropPixmap = self.screenPixmap.copy(realCropRect)
            QApplication.clipboard().setPixmap(cropPixmap)
        self.cancelScreenShot()
        self.close()

    def snip(self):
        if not self.scene.isCapturing():
            return
        cropRect = self.scene.lastAddItem.sceneBoundingRect()
        realCropRect = self.toPhysicalRectF(cropRect).toRect()
        if realCropRect.size() != QSize(0, 0):
            cropPixmap = self.screenPixmap.copy(realCropRect)
            screenPoint = self.mapToGlobal(cropRect.topLeft().toPoint())
            self.snipedSignal.emit(screenPoint, cropRect.size().toSize(), cropPixmap)
        self.cancelScreenShot()
        self.close()

    def cancelScreenShot(self):
        self.scene.cancelScreenShot()

    def reShow(self):
        if self.isActiveWindow():
            return
        finalPixmap, finalGeometry = CanvasUtil.grabScreens()
        self.screenPixmap = finalPixmap
        self.setGeometry(finalGeometry)
        rect = QRectF(0, 0, finalGeometry.width(), finalGeometry.height())
        self.scene.setSceneRect(rect)
        sceneBrush = QBrush(self.screenPixmap.copy())
        transform = QtGui.QTransform()
        transform.scale(1/finalPixmap.devicePixelRatioF(), 1/finalPixmap.devicePixelRatioF())
        sceneBrush.setTransform(transform)
        self.scene.setBackgroundBrush(sceneBrush)
        self.scene.reset()
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.closedSignal.emit()
        return super().closeEvent(a0)