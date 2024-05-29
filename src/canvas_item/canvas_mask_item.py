from .canvas_util import *

class CanvasMaskItem(QGraphicsRectItem):
    '''
    绘图工具-遮罩层
    '''
    def __init__(self, color:QColor, parent = None) -> None:
        super().__init__(parent)
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()
        painter.fillRect(self.rect(), self.color)
        painter.restore()