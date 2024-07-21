# coding=utf-8
from .canvas_util import *

class QAutoSizeLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def initStyle(self):

        # 设置该控件的背景透明
        self.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                border-radius: 0px;
                color: transparent;
                padding: 0px;
                margin: 0px;
                selection-background-color: rgba(68, 107, 150, 100);
                selection-color: transparent;
            }

            QLineEdit:hover {
                border-style: dashed;
                border-width: 0px;
                border-color: transparent
            }

            QLineEdit:focus {
                border-style: solid;
                border-width: 0px;
                border-color: transparent
            }
        """)

class QDMNodeContentWidget(QWidget):
    def __init__(self, rect:QRectF, text:str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        font = QFont("Microsoft YaHei", 2)
        # font = QFont("Arial", 1)

        self.lineEdit = QAutoSizeLineEdit()
        self.lineEdit.setFont(font)
        self.lineEdit.setMinimumSize(rect.size().toSize())
        self.lineEdit.setFixedSize(rect.size().toSize())
        self.lineEdit.initStyle()
        self.lineEdit.setTextMargins(0, 0, 0, 0)
        self.lineEdit.setContentsMargins(0, 0, 0, 0)
        self.lineEdit.setText(text)
        self.layout.addWidget(self.lineEdit)

        # 自适应字体大小和字符间距
        self.adjustFontSizeAndSpacing()

    def adjustFontSizeAndSpacing(self):
        font = self.lineEdit.font()
        rect = self.lineEdit.rect()
        fontSize = 1

        low, high = 1, 100
        while low <= high:
            mid = (low + high) // 2
            font.setPointSize(mid)
            self.lineEdit.setFont(font)

            # 获取文本的渲染大小
            textSize = self.getTextSize(font, -1)

            if textSize.width() <= rect.width() and textSize.height() <= rect.height():
                fontSize = mid
                low = mid + 1
            else:
                high = mid - 1

        # 设置最终的字体大小和字符间距
        font.setPointSize(fontSize)

        if textSize.width() < rect.width():
            finalLetterSpacing = self.findBestLetterSpacing(font, rect)
            font.setLetterSpacing(QFont.AbsoluteSpacing, finalLetterSpacing)
        
        self.lineEdit.setFont(font)

    def findBestLetterSpacing(self, font, rect):
        letterSpacing = 1

        while True:
            # 获取文本的渲染大小
            textSize = self.getTextSize(font, letterSpacing)

            if textSize.width() <= rect.width():
                letterSpacing = letterSpacing + 1
            else:
                break

        return letterSpacing

    def getTextSize(self, font, letterSpacing):
        # 设置字体和字符间距
        if letterSpacing >= 0:
            font.setLetterSpacing(QFont.AbsoluteSpacing, letterSpacing)
            self.lineEdit.setFont(font)

        # 获取文本的渲染大小
        metrics = QFontMetrics(font)
        finalSize = metrics.size(0, self.lineEdit.text())

        return finalSize

class CanvasOcrTextItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, text:str, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        # self.setDefaultFlag()
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QBrush(Qt.NoBrush))
        self.content = QDMNodeContentWidget(rect, text)
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.boundingRect().toRect())
        self.grContent.setWidget(self.content)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable)