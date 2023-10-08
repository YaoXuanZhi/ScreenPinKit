import math
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from canvas_item.canvas_node_item import *
from canvas_item.canvas_node_rect import *
from canvas_item.canvas_editable_rect import *
from canvas_item.canvas_resize_rect import *

class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket, socket_type=1):
        self.socket = socket
        super().__init__(socket.node.grNode)

        self.radius = 6.0
        self.outline_width = 1.0
        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFb54747"),
            QColor("#FFdbe220"),
        ]
        self._color_background = self._colors[socket_type]
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # settings
        self.gridSize = 20
        self.gridSquares = 5

        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

        self.initNodes()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(x, top, x, bottom))
            else: lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(left, y, right, y))
            else: lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)

    def initNodes(self):
        nodeItem = CanvasNodeItem("NodeItem")
        nodeItem.setPos(100, 100)
        self.addItem(nodeItem)

        # rectItem = CanvasNodeRect(QRectF(-100, -100, 100, 100))
        # self.addItem(rectItem)

        # rect = rectItem.sceneBoundingRect()
        # rectItem.roiManager.addROI(rect.topLeft())
        # rectItem.roiManager.addROI(rect.topRight())
        # rectItem.roiManager.addROI(rect.bottomRight())
        # rectItem.roiManager.addROI(rect.bottomLeft())


        rectItem = ResizableRectItem(-100, -100, 100, 100)
        self.addItem(rectItem)

        editableRectItem = CanvasEditableFrame(QRectF(-100, 200, 100, 100))
        # editableRectItem = CanvasEditableFrame(QRectF(-200, 200, 150, 150))
        self.addItem(editableRectItem)