# coding:utf-8
import os, math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *

class ColorCircleItem(QGraphicsEllipseItem):
    """颜色小圆圈图元"""

    def __init__(self, id: int, color: QColor, parent=None):
        super().__init__(parent)
        self.id = id
        self.color = color
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        color.setAlpha(150)
        self.setBrush(QBrush(color))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene: ColorPreviewerScene = self.scene()
        scene.itemClicked.emit(self.id, self.color)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, widget)

class ColorPreviewerScene(QGraphicsScene):
    """
    reference from: https://github.com/flameshot-org/flameshot/blob/master/src/widgets/colorpickerwidget.cpp
    """
    itemClicked = pyqtSignal(int, QColor)

    def __init__(self, colors: list, parent=None):
        super().__init__(parent)
        self.colors = colors

    def initItems(self, size: QSizeF):
        self.radius = min(min(size.width(), size.height()) / 2, 150)
        self.items = []
        num_items = len(self.colors)
        angleStep = 360 / num_items
        for i in range(num_items):
            start_angle = i * angleStep
            span_angle = angleStep

            item = ColorCircleItem(i, self.colors[i])
            item.setRect(QRectF(0, 0, 20, 20))
            self.items.append(item)
            self.addItem(item)

            text_angle = start_angle + span_angle / 2
            text_radius = self.radius * 0.7
            text_point = self.calculatePoint(text_angle, text_radius)
            item.setPos(text_point)

    def calculatePoint(self, angle, radius):
        angle_rad = math.radians(angle)
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        return QPointF(x, y)


class ColorPreviewerView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

    def initUI(self):
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border:0px;")
        self.setRenderHint(QPainter.Antialiasing)
        self.setContentsMargins(0, 0, 0, 0)


class RingColorSelectorDialog(MaskDialogBase):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, color: QColor, parent=None, enableAlpha=False):
        super().__init__(parent)
        self.color = color
        self.enableAlpha = enableAlpha

        colors = [
            QColor(Qt.GlobalColor.yellow),
            QColor(Qt.GlobalColor.blue),
            QColor(Qt.GlobalColor.red),
            QColor(Qt.GlobalColor.green),
            QColor(Qt.GlobalColor.gray),
            QColor(Qt.GlobalColor.white),
            QColor(Qt.GlobalColor.black),
        ]
        self.scene = ColorPreviewerScene(colors)
        self.scene.itemClicked.connect(self.onItemClicked)
        self.view = ColorPreviewerView(self.scene)

        self.contentLayout = QVBoxLayout(self.widget)
        self.__initWidget()
        self.scene.initItems(self.rect().size())

    def onItemClicked(self, id: int, color: QColor):
        self.colorChanged.emit(color)

    def __initWidget(self):
        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 80))
        # self.setMaskColor(QColor(0, 0, 0, 2)) # 几乎透明
        self.setMaskColor(QColor(0, 0, 0, 30)) # 半透明
        self.__initLayout()

    def __initLayout(self):
        self._hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.addWidget(self.view)
