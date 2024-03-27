import math
from enum import Enum
import typing
from PyQt5 import QtCore, QtGui
# from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF

# from PyQt5.QtGui import QFocusEvent, QTextCursor, QPainter, QStyleHints, QPen, QFont, QPainterPath, QFontMetrics
# from PyQt5.QtWidgets import QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget, QApplication, QGraphicsLayoutItem, QGraphicsWidget
# from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsTextItem, QStyle

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui_canvas_editor import CanvasItemEditor, CanvasEditAction

from collections import OrderedDict

class EnumPosType(Enum):
    ControllerPosTL = "左上角"
    ControllerPosTC = "顶部居中"
    ControllerPosTR = "右上角"
    ControllerPosRC = "右侧居中"
    ControllerPosBR = "右下角"
    ControllerPosBC = "底部居中"
    ControllerPosBL = "左下角"
    ControllerPosLC = "左侧居中"
    ControllerPosTT = "顶部悬浮"

class CanvasROIItem(QGraphicsWidget):
    def __init__(self, id:int, hoverCursor:QCursor = None, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.id = id
        self.lastCursor = None
        if hoverCursor == None:
            hoverCursor = Qt.CursorShape.SizeAllCursor
        self.hoverCursor = hoverCursor
        self.setPreferredSize(10, 10)

    def initAttribute(self, posType:EnumPosType, hoverCursor:QCursor):
        self.posType = posType
        self.hoverCursor = hoverCursor
   
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def hasFocusWrapper(self):
        if self.hasFocus() or self.isSelected():
            return True
        else:
            return False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        painter.fillRect(self.rect(), Qt.yellow)

        painter.restore()

    def focusInEvent(self, event: QFocusEvent) -> None:
        parentItem:QGraphicsContainer = self.parentItem()
        parentItem.focusInEvent(event)
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        parentItem:QGraphicsContainer = self.parentItem()
        parentItem.focusOutEvent(event)
        return super().focusOutEvent(event)

class TextLayoutItem(QGraphicsLayoutItem):
    def __init__(self, text):
        super().__init__()
        self.text_item = QGraphicsTextItem(text)
        self.text_item.setParentItem(self)

    def sizeHint(self, which, constraint=QSizeF()):
        fm = QFontMetrics(self.text_item.font())
        return QSizeF(fm.width(self.text_item.toPlainText()), fm.height())

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.text_item.setPos(rect.topLeft())

class QGraphicsContainer(QGraphicsWidget):
    '''图元容器类型，为了可以支持QGraphicsLayoutItem的完整特性而特意绕了一下'''
    def __init__(self, parent: QGraphicsItem = None) -> None:
        super().__init__(parent)
        # self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.initUI()

    def initUI(self):
        self.padding = 10
        self.realItem = self.createItem()
        self.textChanged()

        self.roiMgr = CanvasROIManager(self)
        self.createResizeHandles()

        self.realItem.switchEditableBox()

    def switchEditableBox(self):
        self.realItem.switchEditableBox()

    def createItem(self):
        item = UICanvasTextItem(self)
        item.setPos(self.padding, self.padding)
        item.setPlainText("Fadfadfaf")
        item.document().contentsChanged.connect(self.textChanged)
        return item

    def textChanged(self):
        lastGeometry = self.geometry()
        # lastTextBoxSize = self.realItem.sceneBoundingRect().size()
        lastTextBoxSize = self.realItem.getCustomRect().size()
        lastGeometry.setWidth(lastTextBoxSize.width() + self.padding * 2)
        lastGeometry.setHeight(lastTextBoxSize.height() + self.padding * 2)
        self.setGeometry(lastGeometry)

    def geometry(self) -> QRectF:
        return super().geometry()

    def createResizeHandles(self):
        layout = QGraphicsAnchorLayout()
        # 去除布局边距，以便同边框点对齐
        layout.setContentsMargins(0, 0, 0, 0)

        topLeftCorner = self.roiMgr.addROI(QPointF(0, 0))
        topLeftCorner.initAttribute(EnumPosType.ControllerPosTL, Qt.SizeFDiagCursor)

        topCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        topCenterCorner.initAttribute(EnumPosType.ControllerPosTC, Qt.SizeVerCursor)

        topRightCorner = self.roiMgr.addROI(QPointF(0, 0))
        topRightCorner.initAttribute(EnumPosType.ControllerPosTR, Qt.SizeBDiagCursor)

        rightCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        rightCenterCorner.initAttribute(EnumPosType.ControllerPosRC, Qt.SizeHorCursor)

        bottomRightCorner = self.roiMgr.addROI(QPointF(0, 0))
        bottomRightCorner.initAttribute(EnumPosType.ControllerPosBR, Qt.SizeFDiagCursor)

        bottomCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        bottomCenterCorner.initAttribute(EnumPosType.ControllerPosBC, Qt.SizeVerCursor)

        bottomLeftCorner = self.roiMgr.addROI(QPointF(0, 0))
        bottomLeftCorner.initAttribute(EnumPosType.ControllerPosBL, Qt.SizeBDiagCursor)

        leftCenterCorner = self.roiMgr.addROI(QPointF(0, 0))
        leftCenterCorner.initAttribute(EnumPosType.ControllerPosLC, Qt.SizeHorCursor)

        topTipCorner = self.roiMgr.addROI(QPointF(0, 0))
        topTipCorner.initAttribute(EnumPosType.ControllerPosTT, Qt.PointingHandCursor)

        # 操作点中心锚定父边框左上角
        layout.addAnchor(topLeftCorner, Qt.AnchorVerticalCenter, layout, Qt.AnchorTop)
        layout.addAnchor(topLeftCorner, Qt.AnchorHorizontalCenter, layout, Qt.AnchorLeft)

        # 操作点中心锚定父边框顶部中间
        layout.addAnchor(layout, Qt.AnchorTop, topCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorHorizontalCenter, topCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框右上角
        layout.addAnchor(layout, Qt.AnchorTop, topRightCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorRight, topRightCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框右侧中间
        layout.addAnchor(layout, Qt.AnchorVerticalCenter, rightCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorRight, rightCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框右下角
        layout.addAnchor(layout, Qt.AnchorBottom, bottomRightCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorRight, bottomRightCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框底部中间
        layout.addAnchor(layout, Qt.AnchorBottom, bottomCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorHorizontalCenter, bottomCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框左下角
        layout.addAnchor(layout, Qt.AnchorBottom, bottomLeftCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorLeft, bottomLeftCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框左侧中间
        layout.addAnchor(layout, Qt.AnchorVerticalCenter, leftCenterCorner, Qt.AnchorVerticalCenter)
        layout.addAnchor(layout, Qt.AnchorLeft, leftCenterCorner, Qt.AnchorHorizontalCenter)

        # 操作点中心锚定父边框顶部中间
        layout.addAnchor(topCenterCorner, Qt.AnchorTop, topTipCorner, Qt.AnchorBottom)
        layout.addAnchor(topCenterCorner, Qt.AnchorHorizontalCenter, topTipCorner, Qt.AnchorHorizontalCenter)

        self.setLayout(layout)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        # painter.fillRect(self.rect(), Qt.blue)
        painter.setPen(Qt.blue)
        painter.drawRect(self.rect())

        painter.restore()

class CanvasROIManager():
    def __init__(self, parent: QGraphicsItem) -> None:
        self.parent = parent
        self.itemsOrderDict = OrderedDict()
        self.lastId = 0

    def addROI(self, pos:QPointF, hoverCursor:QCursor = None) -> CanvasROIItem:
        ''''添加操作点'''
        self.lastId += 1
        id = self.lastId
        roiItem = CanvasROIItem(id, hoverCursor, self.parent)
        self.itemsOrderDict[id] = roiItem
        roiItem.setPos(pos)
        return roiItem

    def removeROI(self, id:int):
        ''''移除操作点'''
        roiItem = self.itemsOrderDict.pop(id)
        self.parent.scene().removeItem(roiItem)

    def show(self):
        # if len(self.itemsOrderDict) == 0:
        #     parent:ResizableRectItem = self.parent
        #     parent.createResizeHandles()
        #     return

        for value in self.itemsOrderDict.values():
            roi:CanvasROIItem = value
            if not roi.isVisible():
                roi.show()

    def hide(self):
        for value in self.itemsOrderDict.values():
            roi:CanvasROIItem = value
            if roi.isVisible():
                roi.hide()

class UICanvasTextItem(QGraphicsTextItem):
    m_store_str:str
    mySignal = QtCore.pyqtSignal(str)
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setDefaultFlag()
        self.setDefaultTextColor(Qt.white)

        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

        self.editor = CanvasItemEditor(self)
        self.editor.m_nInterval = 6
        self.editor.getCustomRect = self.getCustomRect
        self.editor.mouseMoveResizeOperator = self.mouseMoveResizeOperator
        self.setAcceptHoverEvents(True)    

    def getCustomRect(self):
        return QRectF(QPointF(0, 0), self.document().size())

    def mouseMoveResizeOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        yInterval = abs(scenePos.y() - self.editor.m_pressedPos.y())

        font = QFont()
        finalSize = max(1, self.originFontSize * (1 + yInterval * 0.2))
        font.setPointSize(finalSize)
        self.setFont(font)
        self.update()

    # 设置默认模式
    def setDefaultFlag(self):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    # 取消文本选中状态
    def cancelSelectedText(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def focusInEvent(self, event: QFocusEvent) -> None:
        if (event.reason() != Qt.PopupFocusReason): # 注意右键菜单在此进入焦点时不保存原始文本
            self.m_store_str = self.toPlainText() # 保存原始文本
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if(event.reason() == Qt.MouseFocusReason and QApplication.mouseButtons()== Qt.RightButton):
            # 右键点击其他地方失去焦点，定义为取消操作，恢复原始文本
            self.setPlainText(self.m_store_str)
            self.setTextInteractionFlags(Qt.NoTextInteraction) # 恢复不能编辑状态
        elif(event.reason() == Qt.PopupFocusReason):
            #右键弹出菜单时不做处理
            pass
        else:
            #其他情况，包括下面点击回车的情况，编辑成功，发送信号给父对象
            self.cancelSelectedText()
            self.setDefaultFlag()
            self.mySignal.emit(self.toPlainText())
        return super().focusOutEvent(event)

    def isCanEditable(self):
        '''判断窗口的鼠标是否穿透了'''
        return (self.textInteractionFlags() | Qt.TextEditorInteraction) == self.textInteractionFlags()

    def switchEditableBox(self, event: QGraphicsSceneMouseEvent = None):
        self.clearFocus()
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()

        if event == None:
            return

        pos = self.mapToText(event.pos()) # 让光标移到当前鼠标所在位置
        # pos = math.ceil(len(self.toPlainText())/2) # 让光标移到文本中间
        textCursor = self.textCursor()
        textCursor.setPosition(pos)
        self.setTextCursor(textCursor)

    def mapToText(self, pos):
        return self.document().documentLayout().hitTest(QPointF(pos), Qt.FuzzyHit)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if(event.button() == Qt.LeftButton):
            if not self.isCanEditable():
                # 左键双击进入可编辑状态并打开焦点
                self.switchEditableBox(event)
                return

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # 自定义滚轮事件的行为
        finalFont = self.font()
        finalFontSize = finalFont.pointSize()
        # 例如，你可以改变文本的大小
        if event.angleDelta().y() > 0:
            # 放大
            finalFontSize = finalFontSize + 1
        else:
            # 缩小
            finalFontSize = max(1, finalFontSize - 1)
        finalFont.setPointSize(finalFontSize)
        self.setFont(finalFont)
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing, True)

        if self.isSelected():
            option.state = QStyle.StateFlag.State_None
        super().paint(painter, option, widget)

        # self.editor.paint(painter, option, widget)

    def getItemOper(self):
        return self.editor.m_itemAction

    def shape(self) -> QPainterPath:
        return self.editor.shape()

    def boundingRect(self) -> QRectF:
        return self.editor.boundingRect()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.isCanEditable():
            super().mousePressEvent(event)
            return

        if self.editor.m_itemAction == CanvasEditAction.DoNothing:
            super().mousePressEvent(event)
        self.editor.mousePressEvent(event)
        self.originFontSize = self.font().pointSize()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.editor.m_itemAction == CanvasEditAction.DoNothing:
            super().mouseMoveEvent(event)
        self.editor.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.editor.m_itemAction == CanvasEditAction.DoNothing:
            super().mouseReleaseEvent(event)
        self.editor.mouseReleaseEvent(event)

class UICanvasTextItemBak(QGraphicsTextItem):
    m_store_str:str
    mySignal = QtCore.pyqtSignal(str)
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setDefaultFlag()
        self.setAcceptHoverEvents(True)
        self.setDefaultTextColor(Qt.white)

        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    # 取消文本选中状态
    def cancelSelectedText(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def focusInEvent(self, event: QFocusEvent) -> None:
        if (event.reason() != Qt.PopupFocusReason): # 注意右键菜单在此进入焦点时不保存原始文本
            self.m_store_str = self.toPlainText() # 保存原始文本
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if(event.reason() == Qt.MouseFocusReason and QApplication.mouseButtons()== Qt.RightButton):
            # 右键点击其他地方失去焦点，定义为取消操作，恢复原始文本
            self.setPlainText(self.m_store_str)
            self.setTextInteractionFlags(Qt.NoTextInteraction) # 恢复不能编辑状态
        elif(event.reason() == Qt.PopupFocusReason):
            #右键弹出菜单时不做处理
            pass
        else:
            #其他情况，包括下面点击回车的情况，编辑成功，发送信号给父对象
            self.cancelSelectedText()
            self.setDefaultFlag()
            self.mySignal.emit(self.toPlainText())
        return super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if(event.button() == Qt.LeftButton):
            # 左键双击进入可编辑状态并打开焦点
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.setFocus()
            return super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.setOpacity(0.5)

    def hoverLeaveEvent(self, event):
        self.setOpacity(1.0)

    # def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
    #     if self.hasFocus():
    #         option.state = QStyle.StateFlag.State_None
    #         super().paint(painter, option, widget)
    #     else:
    #         super().paint(painter, option, widget)

    def paint(self, painter, option, widget):
        if self.isSelected():
            pen = QPen(Qt.white, Qt.DashLine, 2)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)