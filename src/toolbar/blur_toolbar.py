# coding=utf-8
from common import ScreenShotIcon
from canvas_editor import DrawActionEnum
from .canvas_item_toolbar import *

class BlurToolbar(CanvasItemToolBar):
    blurTypeChangedSignal = pyqtSignal(DrawActionEnum)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.styleMap = {
            "strength" : 2,
        }

    def refreshStyleUI(self):
        strength:int = self.styleMap["strength"]
        self.strengthSlider.setValue(strength)

    def initUI(self):
        eraseActions = [
            Action(ScreenShotIcon.MOSAIC, self.tr("Mosaic"), triggered=lambda: self.blurTypeChangedSignal.emit(DrawActionEnum.UseMosaicTool)),
            Action(ScreenShotIcon.BLUR, self.tr("Blur"), triggered=lambda: self.blurTypeChangedSignal.emit(DrawActionEnum.UseEraserRectItem)),
            ]

        self.actionGroup = QActionGroup(self)
        for action in eraseActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)
        
        self.addActions(eraseActions)
        eraseActions[0].trigger()
        self.strengthSlider = self.initSliderOptionUI(self.tr("Effect strength"), self.styleMap["strength"], 2, 10)

    def listenerEvent(self):
        self.strengthSlider.valueChanged.connect(self.strengthValueChangedHandler)

    def strengthValueChangedHandler(self, value:float):
        self.styleMap["strength"] = value
        self.refreshAttachItem()

    def wheelZoom(self, angleDelta:int):
        # 自定义滚轮事件的行为
        if angleDelta > 1:
            # 放大
            self.strengthSlider.setValue(self.strengthSlider.value() + 1)
        else:
            # 缩小
            self.strengthSlider.setValue(self.strengthSlider.value() - 1)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.resetStyle(self.styleMap.copy())