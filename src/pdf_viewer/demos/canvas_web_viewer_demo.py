# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from qframelesswindow import FramelessWindow

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))
from pdf_viewer import *

class MainWindow(FramelessWindow):
# class MainWindow(QWidget):
    def __init__(self, folderPath:str, parent=None):
        super().__init__(parent)
        self.folderPath = folderPath
        self.defaultFlag()
        self.initUI()

    def defaultFlag(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def initUI(self):
        workDir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

        self.pathList = self.getHtmlFiles()
        self.currentIndex = 0

        self.contentLayout = QHBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.webWidgetWrapper = OcrWidgetWrapper(WebWidget(), OcrWidgetRenderMode.NormalMode)
        self.webWidgetWrapper.contentView.receiver.htmlRenderEndSlot.connect(self.onHtmlRenderEnd)
        self.contentLayout.addWidget(self.webWidgetWrapper.contentView)

        htmlConent = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>示例网页</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: transparent;
            margin: 0;
            padding: 20px;
        }
        h1 {
            color: red;
        }
        p {
            color: green;
            line-height: 1.6;
        }
        a {
            color: blue;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>

    <h1>欢迎来到示例网页</h1>

    <p>这是一个简单的HTML示例，展示了如何创建一个基本的网页。</p>

    <p>你可以点击以下链接访问其他页面：</p>
    <ul>
        <li><a href="https://www.example.com" target="_blank">示例网站</a></li>
        <li><a href="https://www.google.com" target="_blank">Google</a></li>
    </ul>

    <p>以下是一张示例图片：</p>
    <img src="https://via.placeholder.com/600x400" alt="示例图片">

    <p>如果你有任何问题，请随时联系我们。</p>

</body>
</html>
'''
        htmlFile = self.getHtmlFiles()[0]
        # with codecs.open(htmlFile, mode="r", encoding="utf-8", errors='ignore') as f:
        #     htmlConent = f.read()

        # self.webWidgetWrapper.setHtml(htmlConent)
        self.webWidgetWrapper.openFile(htmlFile)

    def onHtmlRenderEnd(self, width, height):
        self.resize(QSize(int(width), int(height)))

    def getHtmlFiles(self):
        result = []
        for fileName in os.listdir(self.folderPath):
            if fileName.endswith(".html"):
                result.append(os.path.join(self.folderPath, fileName))
        return result

    # 监听右键双击事件
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.close()
        return super().mouseDoubleClickEvent(event)
    
    def onRenderEnd(self, width, height):
        self.resize(QSize(int(width), int(height)))

if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    pdfPath = os.path.join(os.path.dirname(__file__), "resources")
    mainWindow = MainWindow(pdfPath)
    mainWindow.show()
    sys.exit(app.exec())
