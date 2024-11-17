# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys, os
from argparse import ArgumentParser, RawTextHelpFormatter

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from pdf_viewer import *


class MainWindow(QWidget):
    def __init__(self, folderPath: str, parent=None):
        super().__init__(parent)
        self.folderPath = folderPath
        self.defaultFlag()
        self.initUI()

    def defaultFlag(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

    def initUI(self):
        workDir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

        self.pathList = self.getPdfFiles()
        self.currentIndex = 0

        self.contentLayout = QHBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.pdfWidgetWrapper = OcrWidgetWrapper(
            PdfWidget(), OcrWidgetRenderMode.NormalMode
        )
        self.pdfWidgetWrapper.contentView.receiver.htmlRenderEndSlot.connect(
            self.onRenderEnd
        )
        self.contentLayout.addWidget(self.pdfWidgetWrapper.contentView)
        self.pdfWidgetWrapper.openFile(f"{workDir}/resources/animals2_ocr.pdf")

    def getPdfFiles(self):
        result = []
        for fileName in os.listdir(self.folderPath):
            if fileName.endswith(".pdf"):
                result.append(os.path.join(self.folderPath, fileName))
        return result

    # 监听右键双击事件
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.close()
        return super().mouseDoubleClickEvent(event)

    def onRenderEnd(self, width, height):
        self.resize(QSize(int(width), int(height)))


if __name__ == "__main__":
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    pdfPath = os.path.join(os.path.dirname(__file__), "resources")
    mainWindow = MainWindow(pdfPath)
    mainWindow.show()
    sys.exit(app.exec())
