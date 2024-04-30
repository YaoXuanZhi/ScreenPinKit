from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *

class FontPickerButtonPlus(QToolButton):
    """ Font picker button """

    fontChanged = pyqtSignal(QFont)

    def __init__(self, font: QFont, title: str, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.setFixedSize(96, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setTargetFont(font)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.__showFontDialog)

    def __showFontDialog(self):
        font, ok = QFontDialog.getFont(self.font(), self, "选择字体")

        if ok:
            self.setTargetFont(font)
            self.fontChanged.emit(font)

    def setTargetFont(self, font):
        """ set font """
        self.targetFont = font
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        self.setFont(self.targetFont)
        painter.drawText(self.rect(), Qt.AlignCenter, self.title)

        painter.drawRect(self.rect())