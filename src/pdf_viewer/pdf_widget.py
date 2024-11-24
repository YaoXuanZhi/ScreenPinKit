# coding=utf-8
"""
将图片转换为pdf，用pdf.js将其渲染出来，以此来实现一个文本选择层

@Note
该版本实现，借助了OcrMyPdf来将图片进行OCR识别后将结果保存成PDF文件，需要提取下载后对应的OCR语言包，OCR识别速度较快
另外，该方案存在一些瑕疵，如下所示：
  1.PDF文档本身不包含透明度支持，无法将这个文本选择层封装成一个纯文本透明层，可以将原图像作文档背景，问题可绕过
  2.QWebEngineView模块加载PDF文档速度相对较慢，这个问题可忽略
  3.OCR所生成的PDF文档与原图像相比，会有一定程度的模糊，算不上无感叠加上文本选择层

改进建议：
可以fork OcrMyPdf项目，增加一个生成纯透明文本层+原图像背景的PDF文档的功能支持
"""

import os
from .ocr_widget_interface import *
from misc import *

class PdfWidget(OcrWidgetInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workDir = os.path.join(OsHelper.getInternalPath(), "internal_deps").replace("\\", "/")
        self.pdfjsWebUrl = (
            f"file:///{self.workDir}/pdfjs-3.4.120-legacy-dist/web/viewer.html"
        )

    def openFile(self, pdfPath):
        self.receiver.htmlRenderStartSlot.emit()
        pdfPath = pdfPath.replace("\\", "/")
        self.webView.load(QUrl.fromUserInput(f"{self.pdfjsWebUrl}?file={pdfPath}"))
