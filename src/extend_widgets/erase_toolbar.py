from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_item import *
from .canvas_item_toolbar import *
from canvas_editor import DrawActionEnum

class EraseToolbar(CommandBarView):
    eraseTypeChangedSignal = pyqtSignal(DrawActionEnum)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        eraseActions = [
            Action(ScreenShotIcon.MOSAIC, '画笔', triggered=lambda: self.eraseTypeChangedSignal.emit(DrawActionEnum.UseEraser)),
            Action(ScreenShotIcon.RECTANGLE, '矩形', triggered=lambda: self.eraseTypeChangedSignal.emit(DrawActionEnum.UseEraserRectItem)),
            ]

        self.actionGroup = QActionGroup(self)
        for action in eraseActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)
        
        self.addActions(eraseActions)