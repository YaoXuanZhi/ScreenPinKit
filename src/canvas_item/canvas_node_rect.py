import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget

class CanvasNodeRect(QGraphicsRectItem):
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.edge_size = 10.0
        self._padding = 4.0

        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(self.boundingRect(), self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())