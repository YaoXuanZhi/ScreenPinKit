# coding=utf-8
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from qframelesswindow import FramelessWindow
from PyQt5.QtSvg import QSvgWidget
from qfluentwidgets import PrimaryPushButton, SplitTitleBar, PushButton

class SvgImageViewer(FramelessWindow, QWidget):
    def __init__(self, folderPath):
        super().__init__()
        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.folderPath = folderPath
        self.imageList = self.getSvgFiles()
        self.currentIndex = 0

        self.imageLabel = QSvgWidget()
        self.nextButton = PrimaryPushButton("下一张")
        self.prevButton = PrimaryPushButton("上一张")

        self.nextButton.clicked.connect(self.showNextImage)
        self.prevButton.clicked.connect(self.showPreviousImage)

        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.prevButton)

        self.iconButton = PushButton('图标')
        self.iconButton.resize(200, 200)
        layout.addWidget(self.iconButton)

        self.setLayout(layout)
        self.showCurrentImage()

    def getSvgFiles(self):
        result = []
        for fileName in os.listdir(self.folderPath):
            if fileName.endswith(".svg"):
                result.append(os.path.join(self.folderPath, fileName))
        return result

    def showCurrentImage(self):
        imagePath = self.imageList[self.currentIndex]
        self.imageLabel.load(imagePath)

        self.iconButton.setIcon(QIcon(imagePath))

    def showNextImage(self):
        self.currentIndex = (self.currentIndex + 1) % len(self.imageList)
        self.showCurrentImage()

    def showPreviousImage(self):
        self.currentIndex = (self.currentIndex - 1) % len(self.imageList)
        self.showCurrentImage()

if __name__ == "__main__":
    app = QApplication([])
    svgPath = os.path.join(os.path.dirname(__file__), "resources")
    viewer = SvgImageViewer(svgPath)
    viewer.show()
    app.exec_()