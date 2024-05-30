# coding=utf-8
from common import ScreenShotIcon
from canvas_editor import DrawActionEnum
from .canvas_item_toolbar import *

class EraseToolbar(CanvasItemToolBar):
    eraseTypeChangedSignal = pyqtSignal(DrawActionEnum)
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def initDefaultStyle(self):
        self.styleMap = {
            "width" : 5,
        }

    def initUI(self):
        self.addSeparator()
        eraseActions = [
            Action(ScreenShotIcon.FULL_Dot, self.tr("Eraser pen"), triggered=lambda: self.eraseTypeChangedSignal.emit(DrawActionEnum.UseEraser)),
            Action(ScreenShotIcon.FULL_RECTANGLE, self.tr("Eraser frame"), triggered=lambda: self.eraseTypeChangedSignal.emit(DrawActionEnum.UseEraserRectItem)),
            ]

        self.actionGroup = QActionGroup(self)
        for action in eraseActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)
        
        self.addActions(eraseActions)

        eraseActions[0].trigger()
        self.addSeparator()

    def refreshStyleUI(self):
        pass

    def refreshAttachItem(self):
        if self.canvasItem != None and hasattr(self.canvasItem, "resetStyle"):
            self.canvasItem.resetStyle(self.styleMap.copy())

    def wheelZoom(self, angleDelta:int):
        finalValue = self.styleMap["width"]

        # 自定义滚轮事件的行为
        if angleDelta > 1:
            # 放大
            finalValue = finalValue + 1
        else:
            # 缩小
            finalValue = max(finalValue - 1, 1)
        self.styleMap["width"] = finalValue