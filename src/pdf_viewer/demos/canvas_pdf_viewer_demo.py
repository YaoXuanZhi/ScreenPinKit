# coding=utf-8
import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qframelesswindow import FramelessWindow
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))
from pdf_viewer import PdfWidgetWrapper, PdfWidget

class PdfViewerWindow(FramelessWindow):
    def __init__(self, folderPath):
        super().__init__()
        self.folderPath = folderPath
        self.defaultFlag()
        self.initUI()

    def initUI(self):
        self.pathList = self.getPdfFiles()
        self.currentIndex = 0

        # 显示切换UI
        self.isShowSwitchUI = True
        # self.isShowSwitchUI = False

        # 显示Pdf
        self.pdfWidgetWrapper = PdfWidgetWrapper(PdfWidget.RenderMode.AdvanceMode)
        # self.pdfWidgetWrapper = PdfWidgetWrapper(PdfWidget.RenderMode.NormalMode)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        layout.addWidget(self.pdfWidgetWrapper.contentView)

        if self.isShowSwitchUI:
            # 添加pdf文件切换UI
            self.nextButton = QPushButton("前进")
            self.prevButton = QPushButton("后退")

            self.nextButton.clicked.connect(self.showNextPdf)
            self.prevButton.clicked.connect(self.showPreviousPdf)
            layout.addWidget(self.nextButton)
            layout.addWidget(self.prevButton)

            self.tipButton = QPushButton('提示')
            self.tipButton.clicked.connect(self.showWebMessage)
            self.tipButton.resize(200, 200)
            layout.addWidget(self.tipButton)
        else:
            self.pdfWidgetWrapper.pdfWidget.receiver.pdfRenderEndSlot.connect(self.onRenderEnd)

        self.showCurrentPdf()

    def onRenderEnd(self, width, height):
        self.resize(width, height)

    def defaultFlag(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def getPdfFiles(self):
        result = []
        for fileName in os.listdir(self.folderPath):
            if fileName.endswith(".pdf"):
                result.append(os.path.join(self.folderPath, fileName))
        return result

    def openFile(self, filePath):
        self.pdfWidgetWrapper.openFile(filePath)

    def showCurrentPdf(self):
        filePath = self.pathList[self.currentIndex]

        self.openFile(filePath)

    def showNextPdf(self):
        self.currentIndex = (self.currentIndex + 1) % len(self.pathList)
        self.showCurrentPdf()

    def showPreviousPdf(self):
        self.currentIndex = (self.currentIndex - 1) % len(self.pathList)
        self.showCurrentPdf()
    
    def showWebMessage(self):
        self.pdfWidgetWrapper.webView.page().runJavaScript(f"alert('hello world')");

    # 响应键盘按下
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.showPreviousPdf()
        elif event.key() == Qt.Key.Key_Right:
            self.showNextPdf()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication([])
    pdfPath = os.path.join(os.path.dirname(__file__), "resources")
    viewer = PdfViewerWindow(pdfPath)
    viewer.show()
    app.exec()