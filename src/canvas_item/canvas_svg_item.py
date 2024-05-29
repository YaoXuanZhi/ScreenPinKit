from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from .canvas_util import *
# 使用https://svgco.de/工具来将位图转换为矢量图
# https://editor.method.ac/
# https://svgedit.netlify.app/editor/index.html
# https://yqnn.github.io/svg-path-editor/

class QSvgContentWidget(QSvgWidget):
    def __init__(self, svgPath:str, parent=None):
        super().__init__(parent)

        # 设置该控件的背景透明
        self.setStyleSheet("""
            QSvgWidget {
                background-color: transparent;
            }
        """)

        self.load(svgPath)

class CanvasSvgItem(QGraphicsRectItem):
    '''
    绘图工具-Svg
    '''
    def __init__(self, rect: QRectF, svgPath:str, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.setDefaultFlag()
        # 去除边框
        self.setPen(QPen(Qt.NoPen))

        self.content = QSvgContentWidget(svgPath)
        self.proxyWidget = QGraphicsProxyWidget(self)
        self.proxyWidget.setWidget(self.content)
        if self.rect().isEmpty():
            self.adjustWidgetSizeToFit()
        else:
            self.adjustSvgSizeToFit()

    def type(self) -> int:
        return EnumCanvasItemType.CanvasSvgItem.value

    def adjustWidgetSizeToFit(self):
        '''控件尺寸适配svg图片'''
        svgBoundRect = QRect(QPoint(0, 0), self.content.renderer().defaultSize())
        self.setRect(QRectF(svgBoundRect))
        self.content.setGeometry(svgBoundRect)

    def adjustSvgSizeToFit(self):
        '''svg图片适配控件尺寸'''
        self.content.setGeometry(self.boundingRect().toRect())

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def setEditableState(self, isEditable:bool):
        '''设置可编辑状态'''
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    def completeDraw(self):
        pass