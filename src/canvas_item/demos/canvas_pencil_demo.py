# 优化思路：https://blog.csdn.net/Larry_Yanan/article/details/125935157
import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))
from canvas_item import *

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(DrawingScene, self).__init__(parent)
        self.pathItem = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.pathItem == None:
                self.pathItem = CanvasPencilItem()
                self.addItem(self.pathItem)
                self.pathItem.polygon.append(event.scenePos())
                self.pathItem.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.pathItem.polygon.append(event.scenePos())
            self.pathItem.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pathItem = None

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