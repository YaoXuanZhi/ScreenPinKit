from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *

class ColorPickerButtonPlus(QToolButton):
    """ Color picker button """

    colorChanged = pyqtSignal(QColor)

    def __init__(self, color: QColor, title: str, parent=None, enableAlpha=False):
        super().__init__(parent=parent)
        self.title = title
        self.enableAlpha = enableAlpha
        self.setFixedSize(96, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setColor(color)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.__showColorDialog)

    def __showColorDialog(self):
        options = QColorDialog.ColorDialogOption.NoButtons
        if self.enableAlpha:
            options = QColorDialog.ColorDialogOption.ShowAlphaChannel  # 可选，显示Alpha通道
        color:QColor = QColorDialog.getColor(self.color, self, "选择颜色", options)

        if color.isValid():
            self.setColor(color)
            self.colorChanged.emit(color)

    def setColor(self, color):
        """ set color """
        self.color = QColor(color)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pc = QColor(255, 255, 255, 10) if isDarkTheme() else QColor(234, 234, 234)
        painter.setPen(pc)

        color = QColor(self.color)
        if not self.enableAlpha:
            color.setAlpha(255)

        painter.setPen(color)
        # painter.setBrush(color)
        # painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)
        painter.drawEllipse(self.rect())

class ColorPickerButtonEx(TransparentToggleToolButton):
    """ Color picker button """

    colorChanged = pyqtSignal(QColor)

    def __init__(self, color: QColor, title: str, parent=None, enableAlpha=False):
        super().__init__(parent=parent)
        self.title = title
        self.enableAlpha = enableAlpha
        self.setFixedSize(96, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setColor(color)
        self.setCursor(Qt.PointingHandCursor)

        # self.setToolButtonStyle(self.toolButtonStyle())
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.setToolTip("右击选择颜色")

    def __showColorDialog(self):
        options = QColorDialog.ColorDialogOption.NoButtons
        if self.enableAlpha:
            options = QColorDialog.ColorDialogOption.ShowAlphaChannel  # 可选，显示Alpha通道
        color:QColor = QColorDialog.getColor(self.color, self, "选择颜色", options)

        if color.isValid():
            self.setColor(color)
            self.colorChanged.emit(color)

    def setColor(self, color):
        """ set color """
        self.color = QColor(color)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        color = QColor(self.color)
        if not self.enableAlpha:
            color.setAlpha(255)

        # painter.setPen(color)
        # painter.drawEllipse(self.rect())

        painter.setBrush(color)
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 5, 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.__showColorDialog()
            return
        return super().mousePressEvent(event)