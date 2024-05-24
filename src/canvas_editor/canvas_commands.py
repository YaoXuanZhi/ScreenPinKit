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
        self.item.setSelected(False)
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
        self.item.setSelected(False)
        self.scene.itemList.append(self.item)
        self.scene.addItem(self.item)
        self.scene.update()

    def redo(self):
        self.scene.itemList.remove(self.item)
        self.scene.removeItem(self.item)

class RotateCommand(QUndoCommand):
    def __init__(self, canvasItem:QGraphicsItem, oldRotate:QPointF, newRotate:QPointF, parent=None):
        super().__init__(parent)
        self.attachItem = canvasItem
        self.oldRotate = oldRotate
        self.newRotate = newRotate

    def undo(self):
        self.attachItem.setRotation(self.oldRotate)

    def redo(self):
        self.attachItem.setRotation(self.newRotate)

class ResizeCommand(QUndoCommand):
    def __init__(self, canvasItem:CanvasCommonPathItem, oldValue:tuple, newValue:tuple, parent=None):
        super().__init__(parent)
        self.attachItem = canvasItem
        (oldPolygon, oldRoiPosList) = oldValue
        (newPolygon, newRoiPosList) = newValue
        self.oldPolygon = oldPolygon
        self.oldRoiPosList = oldRoiPosList
        self.newPolygon = newPolygon
        self.newRoiPosList = newRoiPosList

    def undo(self):
        self.attachItem.polygon = self.oldPolygon
        self.attachItem.syncRoiItemsFromPolygon(self.oldRoiPosList)
        self.attachItem.refreshTransformOriginPoint()

    def redo(self):
        self.attachItem.polygon = self.newPolygon
        self.attachItem.syncRoiItemsFromPolygon(self.newRoiPosList)
        self.attachItem.refreshTransformOriginPoint()