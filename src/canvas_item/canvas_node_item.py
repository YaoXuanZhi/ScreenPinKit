from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4

class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket_type=1, parent:QGraphicsItem = None):
        super().__init__(parent)

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

class QDMNodeContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QTextEdit("foo"))

class CanvasNodeItem(QGraphicsItem):
    def __init__(self, title='Node Graphics Item', parent=None):
        super().__init__(parent)

        self.content = QDMNodeContentWidget()

        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", 10)


        self.width = 180
        self.height = 240
        self.edge_size = 10.0
        self.title_height = 24.0
        self._padding = 4.0

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.socket_spacing = 22

        # init title
        self.initTitle()
        self.title = title

        # init sockets
        self.initSockets()

        # init content
        self.initContent()

        self.initUI()

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)


    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(
            self.width
            - 2 * self._padding
        )


    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size, self.title_height + self.edge_size,
                                 self.width - 2*self.edge_size, self.height - 2*self.edge_size-self.title_height)
        self.grContent.setWidget(self.content)

    def initSockets(self):
        self.socket_type = 1
        socket = QDMGraphicsSocket(self.socket_type, self)
        socket.setPos(*self.getSocketPosition(1, LEFT_BOTTOM))
        pass

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())


        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())


        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def getSocketPosition(self, index, position):
        x = 0 if (position in (LEFT_TOP, LEFT_BOTTOM)) else self.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.height - self.edge_size - self._padding - index * self.socket_spacing
        else :
            # start from top
            y = self.title_height + self._padding + self.edge_size + index * self.socket_spacing

        return [x, y]