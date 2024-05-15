from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from canvas_item import *
from .canvas_scene import *

class MoveCommand(QUndoCommand):
    def __init__(self, canvasItem:QGraphicsItem, oldPos:QPointF, newPos:QPointF, parent=None):
        super().__init__(parent)
        self.attachItem = canvasItem
        self.oldPos = oldPos
        self.newPos = newPos

    def undo(self):
        self.attachItem.setPos(self.oldPos)

    def redo(self):
        self.attachItem.setPos(self.newPos)

class AddCommand(QUndoCommand):
    def __init__(self, canvasScene:CanvasScene, canvasItem:QGraphicsItem, parent=None):
        super().__init__(parent)
        self.scene = canvasScene
        self.item = canvasItem

    def undo(self):
        self.scene.itemList.remove(self.item)
        self.scene.removeItem(self.item)
        self.scene.update()

    def redo(self):
        self.scene.itemList.append(self.item)
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        self.scene.clearSelection()
        self.scene.update()

class DeleteCommand(QUndoCommand):
    def __init__(self, canvasScene:CanvasScene, canvasItem:QGraphicsItem, parent=None):
        super().__init__(parent)
        self.scene = canvasScene
        self.item = canvasItem

    def undo(self):
        self.scene.itemList.append(self.item)
        self.scene.addItem(self.item)
        self.scene.update()

    def redo(self):
        self.scene.itemList.remove(self.item)
        self.scene.removeItem(self.item)
