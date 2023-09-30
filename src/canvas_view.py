from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

class CanvasView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        pass

    def initUI(self):
        pass