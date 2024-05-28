from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from common import ScreenShotIcon
from extend_widgets import *
from canvas_item import *
from .canvas_item_toolbar import *
from canvas_editor import DrawActionEnum

class EraseToolbar(CanvasItemToolBar):
    eraseTypeChangedSignal = pyqtSignal(DrawActionEnum)
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def initDefaultStyle(self):
        self.styleMap = {
            "width" : 5,
        }

    def initUI(self):
        eraseActions = [
            Action(ScreenShotIcon.MOSAIC, '橡皮擦', triggered=lambda: self.eraseTypeChangedSignal.emit(DrawActionEnum.UseEraser)),
            Action(ScreenShotIcon.RECTANGLE, '橡皮框', triggered=lambda: self.eraseTypeChangedSignal.emit(DrawActionEnum.UseEraserRectItem)),
            ]

        self.actionGroup = QActionGroup(self)
        for action in eraseActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)
        
        self.addActions(eraseActions)

    def refreshStyleUI(self):
        pass

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.resetStyle(self.styleMap.copy())

    def wheelZoom(self, angleDelta:int):
        finalValue = self.styleMap["width"]

        # 自定义滚轮事件的行为
        if angleDelta > 1:
            # 放大
            finalValue = min(finalValue + 1, 20)
        else:
            # 缩小
            finalValue = max(finalValue - 1, 1)
        self.styleMap["width"] = finalValue