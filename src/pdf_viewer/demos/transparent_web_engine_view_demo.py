import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *

# 设置 HTML 内容
htmlContent = """
<html>
<head>
    <title>Sample HTML</title>
</head>
<body>
    <h1>Hello, PyQt5!</h1>
    <p>This is a sample HTML content displayed using <b>QWebEngineView</b>.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
</body>
</html>
"""

htmlContent2 = """<!DOCTYPE html>
<html lang="en">
<head>
<style>
    body {
        background-color: blue;
    }

    #square {
        width: 200px;
        height: 200px;
        background-color: red;
        position: absolute;
        top: 100px;
        left: 100px;
    }
</style>
</head>
<body>
    <div id="square"></div>
</body>
</html>
"""


class Browser(QWebEngineView):
    def __init__(self, html):
        super().__init__()

        self.url = QUrl.fromLocalFile(os.getcwd() + os.path.sep)
        self.page().setBackgroundColor(Qt.GlobalColor.transparent);
        self.page().setHtml(html, baseUrl=self.url)


class Window(QMainWindow):

    def __init__(self, html):
        super().__init__()
        self.html = html

        self.initWidgets()
        self.initLayouts()
        self.setFixedSize(400, 400)

        self.setStyleSheet("background: transparent; border: transparent;")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(True)

    def initWidgets(self):
        self.browser = Browser(self.html)

    def initLayouts(self):
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)


def main():
    app = QApplication(sys.argv)
    window = Window(htmlContent)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()