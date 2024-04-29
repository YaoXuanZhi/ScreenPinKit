from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *

class PainterToolbar(FlyoutViewBase):
    """ 绘图工具栏 """

    closed = pyqtSignal()

    def __init__(self, title: str, content: str, icon: QIcon = None,
                image: QImage = None, isClosable=False, parent=None):
        super().__init__(parent=parent)
        self.icon = icon
        self.title = title
        self.image = image
        self.content = content
        self.isClosable = isClosable

        self.vBoxLayout = QVBoxLayout(self)
        self.viewLayout = QHBoxLayout()
        self.widgetLayout = QVBoxLayout()

        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(content, self)
        # self.iconWidget = IconWidget(icon, self)
        # self.imageLabel = ImageLabel(self)
        # self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)

        self.__initWidgets()

    def __initWidgets(self):
        # self.imageLabel.setImage(self.image)

        # self.closeButton.setFixedSize(32, 32)
        # self.closeButton.setIconSize(QSize(12, 12))
        # self.closeButton.setVisible(self.isClosable)
        self.titleLabel.setVisible(bool(self.title))
        self.contentLabel.setVisible(bool(self.content))
        # self.iconWidget.setHidden(self.icon is None)

        # self.closeButton.clicked.connect(self.closed)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')
        # FluentStyleSheet.TEACHING_TIP.apply(self)

        self.__initLayout()

    def __initLayout(self):
        self.vBoxLayout.setContentsMargins(1, 1, 1, 1)
        self.widgetLayout.setContentsMargins(0, 8, 0, 8)
        self.viewLayout.setSpacing(4)
        self.widgetLayout.setSpacing(0)
        self.vBoxLayout.setSpacing(0)

        # # add icon widget
        # if not self.title or not self.content:
        #     self.iconWidget.setFixedHeight(36)

        self.vBoxLayout.addLayout(self.viewLayout)
        # self.viewLayout.addWidget(self.iconWidget, 0, Qt.AlignTop)

        # add text
        self._adjustText()
        self.widgetLayout.addWidget(self.titleLabel)
        self.widgetLayout.addWidget(self.contentLabel)
        self.viewLayout.addLayout(self.widgetLayout)

        # add close button
        # self.closeButton.setVisible(self.isClosable)
        # self.viewLayout.addWidget(
        #     self.closeButton, 0, Qt.AlignRight | Qt.AlignTop)

        # adjust content margins
        margins = QMargins(6, 5, 6, 5)
        margins.setLeft(20 if not self.icon else 5)
        margins.setRight(20 if not self.isClosable else 6)
        self.viewLayout.setContentsMargins(margins)

        # add image
        self._adjustImage()
        self._addImageToLayout()

    def addWidget(self, widget: QWidget, stretch=0, align=Qt.AlignLeft):
        """ add widget to view """
        self.widgetLayout.addSpacing(8)
        self.widgetLayout.addWidget(widget, stretch, align)

    def _addImageToLayout(self):
        # self.imageLabel.setBorderRadius(8, 8, 0, 0)
        # self.imageLabel.setHidden(self.imageLabel.isNull())
        # self.vBoxLayout.insertWidget(0, self.imageLabel)

        radioWidget = QWidget()
        radioLayout = QHBoxLayout(radioWidget)
        radioLayout.setContentsMargins(2, 0, 0, 0)
        radioLayout.setSpacing(15)
        radioButton1 = RadioButton(self.tr('Star Platinum'), radioWidget)
        radioButton2 = RadioButton(self.tr('Crazy Diamond'), radioWidget)
        radioButton3 = RadioButton(self.tr('Soft and Wet'), radioWidget)
        buttonGroup = QButtonGroup(radioWidget)
        buttonGroup.addButton(radioButton1)
        buttonGroup.addButton(radioButton2)
        buttonGroup.addButton(radioButton3)
        radioLayout.addWidget(radioButton1)
        radioLayout.addWidget(radioButton2)
        radioLayout.addWidget(radioButton3)
        radioButton1.click()
        # self.vBoxLayout.insertWidget(0, radioWidget)
        self.viewLayout.addWidget(radioWidget)
        pass

    def _adjustText(self):
        w = min(900, QApplication.screenAt(
            QCursor.pos()).geometry().width() - 200)

        # adjust title
        chars = max(min(w / 10, 120), 30)
        self.titleLabel.setText(self.title)

        # adjust content
        chars = max(min(w / 9, 120), 30)
        self.contentLabel.setText(self.content)

    def _adjustImage(self):
        w = self.vBoxLayout.sizeHint().width() - 2
        # self.imageLabel.scaledToWidth(w)

    def showEvent(self, e):
        super().showEvent(e)
        self._adjustImage()
        self.adjustSize()