import sys, math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from canvas_scene import CanvasScene
from canvas_view import CanvasView

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()


    def initUI(self):
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        scene = CanvasScene()
        rectItem = scene.addRect(0, 0, 100, 100)
        rectItem.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        rectItem.setPen(QPen(Qt.red))
        view = CanvasView(scene)
        self.layout.addWidget(view)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
