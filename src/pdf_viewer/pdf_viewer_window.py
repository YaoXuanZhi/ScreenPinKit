# coding=utf-8
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

from version import *
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import *

# class PdfViewerWindow(QMainWindow):
class PdfViewerWindow(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()

    def defaultFlag(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def initUI(self):
        pass
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        workDir = os.path.dirname(__file__).replace("\\", "/")
        pdfjs_web = f"file:///{workDir}/pdfjs-3.4.120-legacy-dist/web/viewer.html"
        pdf_path = f"file:///{workDir}/rotated_skew_ocr.pdf"
        self.webView = QWebEngineView()
        self.webView.load(QUrl.fromUserInput(f'{pdfjs_web}?file={pdf_path}'))
        self.webView.page().loadFinished.connect(self.load_finished)
        self.hBoxLayout.addWidget(self.webView)

    def load_finished(self):
        print("文档加载完成")