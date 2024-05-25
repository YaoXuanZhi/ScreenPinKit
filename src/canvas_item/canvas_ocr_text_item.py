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

        font = QFont("Microsoft YaHei", 10)
        # font = QFont("Arial", 1)
        CanvasUtil.adjustFontSizeToFit(text, font, rect, 1, 100)

        lineEdit = QAutoSizeLineEdit()
        lineEdit.setFont(font)
        lineEdit.setMinimumSize(rect.size().toSize())
        lineEdit.setFixedSize(rect.size().toSize())
        lineEdit.initStyle()
        lineEdit.setTextMargins(0, 0, 0, 0)
        lineEdit.setContentsMargins(0, 0, 0, 0)
        lineEdit.setText(text)
        lineEdit.adjustSize()
        self.layout.addWidget(lineEdit)

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