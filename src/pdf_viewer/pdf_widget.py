# coding=utf-8
'''
将图片转换为pdf，用pdf.js将其渲染出来，以此来实现一个文本选择层

@Note
该版本实现，借助了OcrMyPdf来将图片进行OCR识别后将结果保存成PDF文件，需要提取下载后对应的OCR语言包，OCR识别速度较快
另外，该方案存在一些瑕疵，如下所示：
  1.PDF文档本身不包含透明度支持，无法将这个文本选择层封装成一个纯文本透明层，可以将原图像作文档背景，问题可绕过
  2.QWebEngineView模块加载PDF文档速度相对较慢，这个问题可忽略
  3.OCR所生成的PDF文档与原图像相比，会有一定程度的模糊，算不上无感叠加上文本选择层
  4.有个偶现问题，WebEngineView偶尔会出现卡死主程序的情况，重启程序就会好，得排查

改进建议：
可以fork OcrMyPdf项目，增加一个生成纯透明文本层+原图像背景的PDF文档的功能支持
'''
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *

class JavaScriptReceiver(QObject):
    pdfRenderEndSlot = pyqtSignal(float, float)
    pdfRenderStartSlot = pyqtSignal()
    escPressedSlot = pyqtSignal(bool)

    @pyqtSlot(float, float)
    def pdfRenderEnd(self, renderWidth, renderHeight):
        self.pdfRenderEndSlot.emit(renderWidth, renderHeight)

    @pyqtSlot(str)
    def hookCopyText(self, text):
        text = text.strip(" \n")
        QApplication.clipboard().setText(text)

    @pyqtSlot(bool)
    def hookEscPressed(self, hasSelectedText):
        self.escPressedSlot.emit(hasSelectedText)

class PdfWidget(QWidget):
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

        self.workDir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        self.pdfjs_web = f"file:///{self.workDir}/pdfjs-3.4.120-legacy-dist/web/viewer.html"
        self.webView = QWebEngineView()
        self.contentLayout.addWidget(self.webView)

        # 创建QWebChannel并注册JavaScriptReceiver
        self.channel = QWebChannel()
        self.receiver = JavaScriptReceiver()
        self.channel.registerObject("receiver", self.receiver)
        self.webView.page().setWebChannel(self.channel)

        # 未知原因，这里必须先要加载一次网页，否则openFile()失效
        self.webView.load(QUrl.fromUserInput("http://baidu.com"))

    def openFile(self, pdfPath):
        self.receiver.pdfRenderStartSlot.emit()
        pdfPath = pdfPath.replace("\\", "/")
        self.webView.load(QUrl.fromUserInput(f'{self.pdfjs_web}?file={pdfPath}'))

    def cancelSelectText(self):
        script = """
        if (window.getSelection) {
            window.getSelection().removeAllRanges();
        } else if (document.selection) {
            document.selection.empty();
        }
        """
        self.webView.page().runJavaScript(script)

class CanvasPdfViewerItem(QGraphicsWidget):
    def __init__(self, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.containerWidget = PdfWidget()
        self.proxyWidget = QGraphicsProxyWidget(self)
        self.proxyWidget.setWidget(self.containerWidget)
        self.pdfViewerWidget.receiver.pdfRenderEndSlot.connect(self.onPdfRenderEnd)

    @property
    def pdfViewerWidget(self):
        return self.containerWidget

    @property
    def receiver(self):
        return self.containerWidget.receiver

    def openFile(self, pdfPath:str):
        self.containerWidget.openFile(pdfPath)

    def onPdfRenderEnd(self, renderWidth, renderHeight):
        self.containerWidget.resize(QSize(int(renderWidth), int(renderHeight)))

    def cancelSelectText(self):
        self.containerWidget.cancelSelectText()

class MyGraphicScene(QGraphicsScene):
    '''
    自定义一个QGraphicScene，通过代理Widget来调用PdfWidget控件，目的是为了支持透明度设置
    由于在Pdf.js中，其依附的QWidget的透明度设置失效，无法被正常使用，经过一番摸索之后发现，
    可以借用QGraphicsItem的
    '''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pdfViewerItem = CanvasPdfViewerItem()
        self.addItem(self.pdfViewerItem)
        self.pdfViewerWidget.receiver.pdfRenderStartSlot.connect(self.onPdfRenderStart)
        self.pdfViewerWidget.receiver.pdfRenderEndSlot.connect(self.onPdfRenderEnd)

    @property
    def pdfViewerWidget(self):
        return self.pdfViewerItem.pdfViewerWidget

    def onPdfRenderStart(self):
        self.pdfViewerItem.setOpacity(0)

    def onPdfRenderEnd(self, _width, _height):
        self.pdfViewerItem.setOpacity(1)

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

class PdfWidgetWrapper(QObject):
    '''
    PdfWidget的包装类，用于支持多种渲染模式
    '''

    def __init__(self, renderMode:int = PdfWidget.RenderMode.NormalMode, parent=None):
        super().__init__(parent)
        self.__renderMode = renderMode

        if self.__renderMode == PdfWidget.RenderMode.NormalMode:
            self.__pdfWidget = PdfWidget()
        elif self.__renderMode == PdfWidget.RenderMode.AdvanceMode:
            self.__graphicScene = MyGraphicScene()
            self.__graphicView = MyGraphicView(self.__graphicScene)

    def openFile(self, filePath):
        '''打开pdf文件'''
        self.pdfWidget.openFile(filePath)

    @property
    def pdfWidget(self):
        if self.__renderMode == PdfWidget.RenderMode.AdvanceMode:
            return self.__graphicScene.pdfViewerWidget
        else:
            return self.contentView

    @property
    def webView(self):
        return self.pdfWidget.webView

    @property
    def contentView(self):
        if self.__renderMode == PdfWidget.RenderMode.AdvanceMode:
            return self.__graphicView
        else:
            return self.__pdfWidget