# coding=utf-8
'''
将图片转换为html，用html.js将其渲染出来，以此来实现一个文本选择层
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

# 当前html_widget的实现，会导致外部依赖一个比较大的离线ocr包，当然，也可以直接忽略它们

# https://wang-lu.com/html2htmlEX/doc/tb108wang.html
# 将图片OCR结果导出为一个相同样式的html文件，并且用QWidget渲染出来

# https://blog.csdn.net/qq_41883423/article/details/138305024

# https://segmentfault.com/a/1190000044774930

import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *

class JavaScriptReceiver(QObject):
    htmlRenderEndSlot = pyqtSignal(float, float)
    htmlRenderStartSlot = pyqtSignal()
    escPressedSlot = pyqtSignal(bool)

    @pyqtSlot(float, float)
    def htmlRenderFinished(self, renderWidth, renderHeight):
        self.htmlRenderEndSlot.emit(renderWidth, renderHeight)

    @pyqtSlot(str)
    def hookCopyText(self, text):
        text = text.strip(" \n")
        QApplication.clipboard().setText(text)

    @pyqtSlot(bool)
    def hookEscPressed(self, hasSelectedText):
        self.escPressedSlot.emit(hasSelectedText)

class WebWidget(QWidget):
    '''
    将Web.js封装成一个QWidget，以便被外部调用
    注意：该QWidget的渲染已经被Web.js接管，比如鼠标点击、键盘事件、透明度设置等等
    '''

    class RenderMode(int):
        NormalMode = 0
        '''
        普通渲染模式： 该QWidget大部分都已被Web.js接管，无法直接操作， 
        如果你要修改样式，建议直接改动html.js里的web目录源码，不要在Python侧修改
        '''

        AdvanceMode = 1
        '''
        高级渲染模式： 将Web.js封装成一个QGraphicItem，支持Python侧改动透明度等高级操作
        '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background: transparent; border:0px;")
        self.contentLayout = QHBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        # self.contentLayout.addWidget(QLineEdit("hello world"))

        self.workDir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        self.htmljs_web = f"file:///{self.workDir}/htmljs-3.4.120-legacy-dist/web/viewer.html"
        self.webView = QWebEngineView()
        self.contentLayout.addWidget(self.webView)

        # 创建QWebChannel并注册JavaScriptReceiver
        self.channel = QWebChannel()
        self.receiver = JavaScriptReceiver()
        self.channel.registerObject("receiver", self.receiver)
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
        self.htmlViewerWidget.receiver.htmlRenderEndSlot.connect(self.onWebRenderEnd)

    @property
    def htmlViewerWidget(self):
        return self.containerWidget

    @property
    def receiver(self):
        return self.containerWidget.receiver

    def openFile(self, htmlPath:str):
        self.containerWidget.openFile(htmlPath)

    def onWebRenderEnd(self, renderWidth, renderHeight):
        self.containerWidget.resize(QSize(int(renderWidth), int(renderHeight)))

    def cancelSelectText(self):
        self.containerWidget.cancelSelectText()

class MyGraphicScene(QGraphicsScene):
    '''
    自定义一个QGraphicScene，通过代理Widget来调用WebWidget控件，目的是为了支持透明度设置
    由于在Web.js中，其依附的QWidget的透明度设置失效，无法被正常使用，经过一番摸索之后发现，
    可以借用QGraphicsItem的
    '''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.htmlViewerItem = CanvasWebEngineViewItem()
        self.addItem(self.htmlViewerItem)
        self.htmlViewerWidget.receiver.htmlRenderStartSlot.connect(self.onWebRenderStart)
        self.htmlViewerWidget.receiver.htmlRenderEndSlot.connect(self.onWebRenderEnd)

    @property
    def htmlViewerWidget(self):
        return self.htmlViewerItem.htmlViewerWidget

    def onWebRenderStart(self):
        self.htmlViewerItem.setOpacity(0)

    def onWebRenderEnd(self, _width, _height):
        self.htmlViewerItem.setOpacity(1)

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
            self.__htmlWidget = WebWidget()
        elif self.__renderMode == WebWidget.RenderMode.AdvanceMode:
            self.__graphicScene = MyGraphicScene()
            self.__graphicView = MyGraphicView(self.__graphicScene)

    def openFile(self, filePath):
        '''打开html文件'''
        self.htmlWidget.openFile(filePath)

    def setHtml(self, htmlConent:str):
        '''加载Html内容'''
        self.htmlWidget.setHtml(htmlConent)

    @property
    def htmlWidget(self):
        if self.__renderMode == WebWidget.RenderMode.AdvanceMode:
            return self.__graphicScene.htmlViewerWidget
        else:
            return self.contentView

    @property
    def webView(self):
        return self.htmlWidget.webView

    @property
    def contentView(self):
        if self.__renderMode == WebWidget.RenderMode.AdvanceMode:
            return self.__graphicView
        else:
            return self.__htmlWidget