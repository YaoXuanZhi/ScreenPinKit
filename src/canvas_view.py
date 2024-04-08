from PyQt5 import QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from canvas_item.canvas_node_item import *
from ui_canvas_text_item import UICanvasTextItem
from canvas_util import *

class CanvasView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        # self.setStyleSheet("""QGraphicsView { selection-background-color: rgb(255, 255, 255); }""")
        self.initUI()

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)
    
    def zoomHandle(self, zoomFactor):
        self.scale(zoomFactor, zoomFactor)

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonMove(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonMove(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonMove(event)
        else:
            super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # 检查滚轮事件是否在 UICanvasTextItem 上发生
        item = self.itemAt(event.pos())
        if item and isinstance(item, UICanvasTextItem):
            item.wheelEvent(event)
            # 接受事件，防止它被传递到其他处理器
            event.accept()
            return

        self.zoomComponent.TriggerEvent(event.angleDelta().y())

    def middleMouseButtonPress(self, event):
        # releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
        #                            Qt.LeftButton, Qt.NoButton, event.modifiers())
        # super().mouseReleaseEvent(releaseEvent)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        # fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
        #                         Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        # super().mousePressEvent(fakeEvent)
        pass

    def middleMouseButtonRelease(self, event):
        # fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
        #                         Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        # super().mouseReleaseEvent(fakeEvent)
        # self.setDragMode(QGraphicsView.RubberBandDrag)
        pass

    def middleMouseButtonMove(self, event):
        return super().mouseMoveEvent(event)

    def leftMouseButtonPress(self, event):
        item = self.getItemAtClick(event)
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        if type(item) is QDMGraphicsSocket:
            print(f"=======> {item.boundingRect()}")
            return

        return super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)

    def leftMouseButtonMove(self, event):
        return super().mouseMoveEvent(event)

    def rightMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        return super().mousePressEvent(fakeEvent)

    def rightMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def rightMouseButtonMove(self, event):
        return super().mouseMoveEvent(event)

    def getItemAtClick(self, event):
        """ return the object on which we've clicked/release mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj