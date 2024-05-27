from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from canvas_item.canvas_util import *

class FontPickerButtonPlus(QToolButton):
    """ Font picker button """

    fontChanged = pyqtSignal(QFont)

    def __init__(self, defaultFont: QFont, title: str, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.setFixedSize(96, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setTargetFont(defaultFont)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.__showFontDialog)

    def __showFontDialog(self):
        font, ok = QFontDialog.getFont(self.targetFont, self, "选择字体")
        font.setBold(self.targetFont.bold())
        font.setItalic(self.targetFont.italic())

        if ok:
            self.setTargetFont(font)
            self.fontChanged.emit(font)

    def setTargetFont(self, font:QFont):
        """ set font """
        self.targetFont = font
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        tempFont = QFont(self.targetFont)
        text = tempFont.family()
        showRect = self.rect()
        showRect = showRect - QMargins(6, 0, 6, 0)
        FontPickerButtonPlus.adjustFontSizeToFit(text, tempFont, showRect)
        self.setFont(tempFont)
        painter.drawText(self.rect(), Qt.AlignCenter, text)

        painter.drawRect(self.rect())

    @staticmethod
    def adjustFontSizeToFit(text, font:QFont, rect:QRectF):
        '''调整字体适应大小'''

        minFontSize = 1
        maxFontSize = 50

        # 计算给定字体大小下的文本宽度和高度
        def calcFontSize(targetFont):
            font_metrics = QFontMetricsF(targetFont)
            return font_metrics.size(0, text)

        finalFontSize = minFontSize
        while finalFontSize >= minFontSize and finalFontSize < maxFontSize:
            # 获取当前字体大小下的文本尺寸
            tempFont = QFont(font)
            tempFont.setPointSizeF(finalFontSize)
            size = calcFontSize(tempFont)
            if size.width() <= rect.width() and size.height() <= rect.height():
            # if size.width() <= rect.width() + offset:
                # 如果文本可以放入矩形区域内，尝试使用更大的字体大小
                finalFontSize += 0.1
            else:
                # 文本太大，无法放入矩形区域，跳出循环
                break

        font.setPointSizeF(finalFontSize)