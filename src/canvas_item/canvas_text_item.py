from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class CanvasTextItem(QGraphicsTextItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

        self.setDefaultFlag()
        self.setDefaultTextColor(Qt.white)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        # self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

    # 取消文本选中状态
    def cancelSelectedText(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def isCanEditable(self):
        '''是否可编辑'''
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

    def switchEditableBox2(self):
        self.clearFocus()
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()

        textCursor = self.textCursor()
        textCursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(textCursor)

    def mapToText(self, pos):
        return self.document().documentLayout().hitTest(QPointF(pos), Qt.FuzzyHit)

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
            # self.mySignal.emit(self.toPlainText())
        if len(self.toPlainText()) == 0:
            # 如果文本为空，则删除这个图元
            self.scene().removeItem(self)
        return super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if(event.button() == Qt.LeftButton):
            if not self.isCanEditable():
                # 左键双击进入可编辑状态并打开焦点
                self.switchEditableBox(event)
                return

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        # 自定义滚轮事件的行为
        finalFont = self.font()
        finalFontSize = finalFont.pointSize()
        # 例如，你可以改变文本的大小
        if event.delta() > 0:
            # 放大
            finalFontSize = finalFontSize + 1
        else:
            # 缩小
            finalFontSize = max(1, finalFontSize - 1)
        finalFont.setPointSize(finalFontSize)
        self.setFont(finalFont)
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        option.state = option.state & ~QStyle.StateFlag.State_Selected
        # option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        return super().paint(painter, option, widget)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.clearFocus()
        return super().keyPressEvent(event)

    def setEditableState(self, isEditable:bool):
        '''设置可编辑状态'''
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    def completeDraw(self):
        pass