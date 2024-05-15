from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from canvas_item.canvas_util import CanvasROIManager
from .canvas_scene import CanvasScene, DrawActionEnum
from .canvas_view import CanvasView
from .canvas_commands import *

class CanvasEditor(QWidget):
    '''
    Canvas编辑层
    sceneBrush == None时，则说明是桌面绘图，
    在截图绘图里，其橡皮擦原理是基于sceneBrush来实现的
    '''

    def __init__(self, parent=None, sceneBrush:QBrush = None):
        super().__init__(parent)
        self.sceneBrush = sceneBrush
        self.defaultFlag()
        self.painter = QPainter()
        self.undoStack = QUndoStack(self)

    def defaultFlag(self):
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def initUI(self):
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.scene = CanvasScene(None, self.sceneBrush)
        self.view = CanvasView(self.scene)
        self.contentLayout.addWidget(self.view)
        self.setEditorEnabled(True)
        self.initUndoFramework()
        self.initActions()

    def initActions(self):
        actions = [
            QAction("撤销", self, triggered=self.undo, shortcut="ctrl+z"),
            QAction("重做", self, triggered=self.redo, shortcut="ctrl+y"),
        ]
        self.addActions(actions)

    def setNofityEvent(self, callBack:callable = None):
        self.scene.setNofityEvent(callBack)

    def clearDraw(self):
        self.undoStack.clear()
        self.scene.clearDraw()

    def quitDraw(self):
        self.setEditorEnabled(False)
        for item in self.view.scene().items():
            if hasattr(item, "roiMgr"):
                roiMgr:CanvasROIManager = item.roiMgr
                roiMgr.setShowState(False)

            item.setSelected(False)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum):
        if self.scene.currentDrawActionEnum == drawActionEnum:
            return
        self.scene.forceCompleteDraw()
        self.scene.currentDrawActionEnum = drawActionEnum
        self.setEditorEnabled(drawActionEnum != DrawActionEnum.DrawNone)

    def switchLockState(self):
        self.scene.switchLockState()

    def getLockState(self):
        return self.scene.isLockedTool

    def isEditorEnabled(self):
        return self.view.isEnabled()

    def setEditorEnabled(self, isOpen:bool):
        '''
        为了兼容桌面标注和截图标注，默认给QGraphicsScene添加一个透明度为1的背景，
        用来避免桌面标注时绘图层鼠标穿透了
        '''
        if self.sceneBrush == None:
            if isOpen:
                color = QColor(Qt.GlobalColor.white)
                color.setAlpha(1)
                # color.setAlpha(100)
                self.scene.setBackgroundBrush(QBrush(color))
            else:
                self.scene.setBackgroundBrush(QBrush(Qt.NoBrush))
        self.view.setEnabled(isOpen)

    def initUndoFramework(self):
        self.scene.itemMovedSignal.connect(self.itemMoved)
        self.scene.itemDeleteSignal.connect(self.itemDelete)
        self.scene.itemAddSignal.connect(self.itemAdd)

    def redo(self):
        if not self.isEditorEnabled() or not self.scene.canUndo():
            return
        self.undoStack.redo()

    def undo(self):
        if not self.isEditorEnabled() or not self.scene.canUndo():
            return
        self.undoStack.undo()

    def itemMoved(self, canvasItem:QGraphicsItem, oldPos:QPointF, newPos:QPointF):
        self.undoStack.push(MoveCommand(canvasItem, oldPos, newPos))

    def itemAdd(self, canvasScene:QGraphicsScene, canvasItem:QGraphicsItem):
        self.undoStack.push(AddCommand(canvasScene, canvasItem))

    def itemDelete(self, canvasScene:QGraphicsScene, canvasItem:QGraphicsItem):
        self.undoStack.push(DeleteCommand(canvasScene, canvasItem))