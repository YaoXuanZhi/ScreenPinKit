# coding=utf-8
from .canvas_util import *
from PyQt5.QtQuick import *
from PyQt5.QtQuickWidgets import *
from PyQt5.QtQml import *

class CanvasQuickQmlItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, qmlUrl: str, parent: QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QBrush(Qt.NoBrush))

        # 创建一个QWidget来承载QML控件
        self.__contentWidget = QWidget()
        self.__contentLayout = QVBoxLayout()
        self.__contentLayout.setContentsMargins(0, 0, 0, 0)
        self.__contentWidget.setLayout(self.__contentLayout)

        self.quickWidget = QQuickWidget()
        self.quickWidget.setSource(QUrl(qmlUrl))
        self.quickWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.__contentLayout.addWidget(self.quickWidget)

        # 创建一个QGraphicsProxyWidget来显示QWidget 
        self.__proxyContent = QGraphicsProxyWidget(self)
        self.__contentWidget.setGeometry(self.boundingRect().toRect())
        self.__proxyContent.setWidget(self.__contentWidget)