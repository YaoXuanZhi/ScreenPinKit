# coding=utf-8
import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from canvas_item import *


class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)


class DrawingView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

    def initUI(self):
        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(
            -self.scene_width // 2,
            -self.scene_height // 2,
            self.scene_width,
            self.scene_height,
        )

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.RubberBandDrag)

        self.currentItem = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item != None and self.currentItem != item:
            return super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if not self.isCanDrag():
                targetPos = self.mapToScene(event.pos())
                if self.currentItem == None:
                    self.currentItem = CanvasStarItem()
                    self.scene().addItem(self.currentItem)
                    self.currentItem.polygon.append(targetPos)
                    self.currentItem.polygon.append(targetPos)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.currentItem != None and not self.isCanDrag():
            targetPos = self.mapToScene(event.pos())
            self.currentItem.polygon.replace(
                self.currentItem.polygon.count() - 1, targetPos
            )
            self.currentItem.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.currentItem != None:
            self.scene().removeItem(self.currentItem)
            self.currentItem = None
            return
        if event.button() == Qt.LeftButton and self.currentItem != None:
            if self.currentItem.polygon.at(0) == self.currentItem.polygon.at(1):
                self.scene().removeItem(self.currentItem)
            else:
                self.currentItem.completeDraw()
                self.currentItem.setEditableState(True)
            self.currentItem = None
            return
        super().mouseReleaseEvent(event)

    def isCanDrag(self):
        """判断当前是否可以拖曳图元"""
        matchMode = self.dragMode()
        return matchMode | QGraphicsView.RubberBandDrag == matchMode

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        elif event.button() == Qt.LeftButton:
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


if __name__ == "__main__":
    import sys

    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)

    wnd = MainWindow()

    sys.exit(app.exec_())
