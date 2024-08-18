# coding=utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from abc import abstractmethod

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

class OcrWidgetInterface(QWidget):
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

    @abstractmethod
    def openFile(self, htmlPath):
        # 抛出异常，子类必须实现openFile方法
        raise NotImplementedError("子类必须实现openFile方法")

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

class CanvasOcrViewerItem(QGraphicsWidget):
    def __init__(self, ocrWidget:OcrWidgetInterface, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.containerWidget = ocrWidget
        self.proxyWidget = QGraphicsProxyWidget(self)
        self.proxyWidget.setWidget(self.containerWidget)
        self.viewerWidget.receiver.htmlRenderEndSlot.connect(self.onHtmlRenderEnd)

    @property
    def viewerWidget(self):
        return self.containerWidget

    @property
    def receiver(self):
        return self.containerWidget.receiver

    def openFile(self, path:str):
        self.containerWidget.openFile(path)

    def onHtmlRenderEnd(self, renderWidth, renderHeight):
        self.containerWidget.resize(QSize(int(renderWidth), int(renderHeight)))

    def setHtml(self, htmlConent:str):
        self.containerWidget.setHtml(htmlConent)

    def cancelSelectText(self):
        self.containerWidget.cancelSelectText()

class MyGraphicScene(QGraphicsScene):
    '''
    自定义一个QGraphicScene，通过代理Widget来调用PdfWidget控件，目的是为了支持透明度设置
    由于在Pdf.js中，其依附的QWidget的透明度设置失效，无法被正常使用，经过一番摸索之后发现，
    可以借用QGraphicsItem的
    '''
    def __init__(self, ocrWidget:OcrWidgetInterface, parent=None):
        super().__init__(parent)

        self.ocrViewerItem = CanvasOcrViewerItem(ocrWidget)
        self.addItem(self.ocrViewerItem)
        self.viewerWidget.receiver.htmlRenderStartSlot.connect(self.onHtmlRenderStart)
        self.viewerWidget.receiver.htmlRenderEndSlot.connect(self.onHtmlRenderEnd)

    @property
    def viewerWidget(self):
        return self.ocrViewerItem.viewerWidget

    def onHtmlRenderStart(self):
        self.ocrViewerItem.setOpacity(0)

    def onHtmlRenderEnd(self, _width, _height):
        self.ocrViewerItem.setOpacity(1)

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

class OcrWidgetWrapper(QObject):
    '''
    OcrWidget的包装类，用于支持多种渲染模式
    '''

    def __init__(self, ocrWidget:OcrWidgetInterface, renderMode:int = RenderMode.NormalMode, parent=None):
        super().__init__(parent)
        self.__renderMode = renderMode

        if self.__renderMode == RenderMode.NormalMode:
            self.__ocrWidget = ocrWidget
        elif self.__renderMode == RenderMode.AdvanceMode:
            self.__graphicScene = MyGraphicScene(ocrWidget)
            self.__graphicView = MyGraphicView(self.__graphicScene)

    def openFile(self, filePath):
        '''加载文件'''
        self.viewerWidget.openFile(filePath)

    def setHtml(self, htmlConent:str):
        '''加载Html内容'''
        self.viewerWidget.setHtml(htmlConent)

    @property
    def viewerWidget(self):
        if self.__renderMode == RenderMode.AdvanceMode:
            return self.__graphicScene.viewerWidget
        else:
            return self.contentView

    @property
    def webView(self):
        return self.viewerWidget.webView

    @property
    def contentView(self):
        if self.__renderMode == RenderMode.AdvanceMode:
            return self.__graphicView
        else:
            return self.__ocrWidget