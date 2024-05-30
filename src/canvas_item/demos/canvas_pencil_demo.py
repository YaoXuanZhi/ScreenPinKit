# coding=utf-8
import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))
from canvas_item import *

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(DrawingScene, self).__init__(parent)
        self.currentItem = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.currentItem == None:
                self.currentItem = CanvasPencilItem()
                self.addItem(self.currentItem)
                self.currentItem.polygon.append(event.scenePos())
                self.currentItem.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.currentItem.polygon.append(event.scenePos())
            self.currentItem.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.currentItem = None

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

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    scene = DrawingScene()
    view = DrawingView(scene)
    view.show()
    sys.exit(app.exec_())