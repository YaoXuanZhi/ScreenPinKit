# coding=utf-8
'''
将图片转换为html，采用QWebEngineView模块将其加载显示，以此来实现一个纯文本选择层

@Note：
 - 1.直接生成html文件，通过各种span标签组合成结果
 - 2.将结果生成一个svg文件，并且在网页上渲染出来，这里面有个问题，那就是如何判断字体大小和间距，优点是支持无损缩放
 - 3.后面还可以让QGraphicsSvgItem支持一个文本选择机制，从而减少QWebEngine的依赖
 - 4.为啥不采用QTextBrowerwidget控件来实现呢，因为它支持的html特性有限，设置的文本框固定坐标无效
 - 5.文本段落的选中行为没处理好，因为之前ocr识别结果都是基于行来识别的，没有区分到这个粒度，另外，垂直文本这块也没支持

参考资料：
 - [Tesseract.js](https://tesseract.projectnaptha.com/)
   >直接通过浏览器的ocr识别来实现，会不会更省事
   - [在vue项目中本地使用Tesseract.js](https://www.jianshu.com/p/a2ab00692859)
   - [如何直接选中复制图片中的文字：前端OCR实现指南](https://blog.csdn.net/qq_41883423/article/details/138305024)
'''
from .ocr_widget_interface import *

class WebWidget(OcrWidgetInterface):
    def __init__(self, parent=None):
        super().__init__(parent)

    def openFile(self, htmlPath):
        self.receiver.htmlRenderStartSlot.emit()
        htmlPath = htmlPath.replace("\\", "/")
        self.webView.load(QUrl.fromUserInput(f'file:///{htmlPath}'))