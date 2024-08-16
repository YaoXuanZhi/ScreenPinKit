# coding=utf-8
'''
将图片转换为html，采用QWebEngineView模块将其加载显示，以此来实现一个纯文本选择层

@Note：
 - 1.直接生成html文件，通过各种span标签组合成结果
 - 2.将结果生成一个svg文件，并且在网页上渲染出来，这里面有个问题，那就是如何判断字体大小和间距，优点是支持无损缩放
 - 3.后面还可以让QGraphicsSvgItem支持一个文本选择机制，从而减少QWebEngine的依赖
 - 4.为啥不采用QTextBrowerwidget控件来实现呢，因为它支持的html特性有限，设置的文本框固定坐标无效
'''
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *

# 直接通过浏览器的ocr识别来实现，这个会更加省事
# https://tesseract.projectnaptha.com/
# https://www.jianshu.com/p/a2ab00692859
# 留意一套Qt wasm技术，感觉可以用来做一些跨平台的功能实现
# 目前怀疑PixPin就是用到类似技术来实现的，然后每个PinWindow本质上就是一个跑着WebEngine的QWidget，
# 然后开启了文本可选择的功能之后，就会执行ocr wasm功能在这个页面上新建一个文本选择层

# 当前pdf_widget的实现，会导致外部依赖一个比较大的离线ocr包，当然，也可以直接忽略它们

# https://wang-lu.com/pdf2htmlEX/doc/tb108wang.html
# 将图片OCR结果导出为一个相同样式的html文件，并且用QWidget渲染出来

# https://blog.csdn.net/qq_41883423/article/details/138305024

# https://segmentfault.com/a/1190000044774930

class JavaScriptReceiver(QObject):
    htmlRenderEndSlot = pyqtSignal(float, float)
    htmlRenderStartSlot = pyqtSignal()
    escPressedSlot = pyqtSignal(bool)

    @pyqtSlot(float, float)
    def htmlRenderFinished(self, renderWidth, renderHeight):
        self.htmlRenderEndSlot.emit(renderWidth, renderHeight)

    @pyqtSlot(str)
    def hookCopyText(self, text):
        QApplication.clipboard().setText(text)

    @pyqtSlot(bool)
    def hookEscPressed(self, hasSelectedText):
        self.escPressedSlot.emit(hasSelectedText)

class WebWidget(QWidget):
    '''
    将Pdf.js封装成一个QWidget，以便被外部调用
    注意：该QWidget的渲染已经被Pdf.js接管，比如鼠标点击、键盘事件、透明度设置等等
    '''

    class RenderMode(int):
        NormalMode = 0
        '''
        普通渲染模式： 该QWidget大部分都已被Pdf.js接管，无法直接操作， 
        如果你要修改样式，建议直接改动pdf.js里的web目录源码，不要在Python侧修改
        '''

        AdvanceMode = 1
        '''
        高级渲染模式： 将Pdf.js封装成一个QGraphicItem，支持Python侧改动透明度等高级操作
        '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background: transparent; border:0px;")
        self.contentLayout = QHBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        # self.contentLayout.addWidget(QLineEdit("hello world"))

        self.webView = QWebEngineView()

        # 开启pdf支持
        self.webView.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        self.contentLayout.addWidget(self.webView)

        # 创建QWebChannel并注册JavaScriptReceiver
        self.channel = QWebChannel()
        self.receiver = JavaScriptReceiver()
        self.channel.registerObject("receiver", self.receiver)
        # 设置透明度
        self.webView.page().setBackgroundColor(Qt.GlobalColor.transparent);
        self.webView.page().setWebChannel(self.channel)

        # 未知原因，这里必须先要加载一次网页，否则openFile()失效
        self.webView.load(QUrl.fromUserInput("http://baidu.com"))

    def openFile(self, htmlPath):
        self.receiver.htmlRenderStartSlot.emit()
        htmlPath = htmlPath.replace("\\", "/")
        self.webView.load(QUrl.fromUserInput(f'file:///{htmlPath}'))

    def setHtml(self, htmlConent:str):
        self.receiver.htmlRenderStartSlot.emit()
        self.webView.setHtml(htmlConent)

    def cancelSelectText(self):
        script = """
        if (window.getSelection) {
            window.getSelection().removeAllRanges();
        } else if (document.selection) {
            document.selection.empty();
        }
        """
        self.webView.page().runJavaScript(script)

class CanvasWebEngineViewItem(QGraphicsWidget):
    def __init__(self, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.containerWidget = WebWidget()
        self.proxyWidget = QGraphicsProxyWidget(self)
        self.proxyWidget.setWidget(self.containerWidget)
        self.receiver.htmlRenderEndSlot.connect(self.onHtmlRenderEnd)

    @property
    def receiver(self):
        return self.containerWidget.receiver

    def openFile(self, htmlPath:str):
        self.containerWidget.openFile(htmlPath)

    def onHtmlRenderEnd(self, renderWidth, renderHeight):
        self.containerWidget.resize(QSize(int(renderWidth), int(renderHeight)))

    def setHtml(self, htmlConent:str):
        self.containerWidget.setHtml(htmlConent)

    def cancelSelectText(self):
        self.containerWidget.cancelSelectText()

class MyGraphicScene(QGraphicsScene):
    '''
    自定义一个QGraphicScene，通过代理Widget来调用WebWidget控件，目的是为了支持透明度设置
    由于在Pdf.js中，其依附的QWidget的透明度设置失效，无法被正常使用，经过一番摸索之后发现，
    可以借用QGraphicsItem的
    '''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.webViewerItem = CanvasWebEngineViewItem()
        self.addItem(self.webViewerItem)

        self.webViewerItem.receiver.htmlRenderStartSlot.connect(self.onHtmlRenderStart)
        self.webViewerItem.receiver.htmlRenderEndSlot.connect(self.onHtmlRenderEnd)

    def onHtmlRenderStart(self):
        self.webViewerItem.setOpacity(0)

    def onHtmlRenderEnd(self, _width, _height):
        self.webViewerItem.setOpacity(1)

class MyGraphicView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.defaultFlag()
        self.initUI()

    def defaultFlag(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def initUI(self):
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scene_width, self.scene_height = self.frameSize().width(), self.frameSize().height()
        self.scene().setSceneRect(0, 0, self.scene_width, self.scene_height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border:0px;")
        self.setRenderHint(QPainter.Antialiasing)

class WebWidgetWrapper(QObject):
    '''
    WebWidget的包装类，用于支持多种渲染模式
    '''

    def __init__(self, renderMode:int = WebWidget.RenderMode.NormalMode, parent=None):
        super().__init__(parent)
        self.__renderMode = renderMode

        if self.__renderMode == WebWidget.RenderMode.NormalMode:
            self.__webWidget = WebWidget()
        elif self.__renderMode == WebWidget.RenderMode.AdvanceMode:
            self.__graphicScene = MyGraphicScene()
            self.__graphicView = MyGraphicView(self.__graphicScene)

    def openFile(self, filePath):
        '''打开html文件'''
        self.proxyWidget.openFile(filePath)

    @property
    def proxyWidget(self):
        if self.__renderMode == WebWidget.RenderMode.AdvanceMode:
            return self.__graphicScene.webViewerItem.containerWidget
        else:
            return self.__webWidget

    @property
    def webView(self):
        return self.proxyWidget.webView

    @property
    def contentView(self):
        if self.__renderMode == WebWidget.RenderMode.AdvanceMode:
            return self.__graphicView
        else:
            return self.__webWidget