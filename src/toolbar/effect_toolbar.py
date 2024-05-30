# coding=utf-8
from common import ScreenShotIcon
from .canvas_item_toolbar import *

class EffectToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.styleMap = {
            "strength" : 2,
            "effectType" : AfterEffectType.Mosaic,
        }

        self.effectTypeInfos = [
            (self.tr("Blur"), ScreenShotIcon.BLUR, AfterEffectType.GaussianBlur),
            (self.tr("Mosaic"), ScreenShotIcon.MOSAIC, AfterEffectType.Mosaic),
        ]

    def refreshStyleUI(self):
        strength:int = self.styleMap["strength"]
        self.strengthSlider.setValue(strength)

        currentEffectType = self.styleMap["effectType"]
        currentIndex = 0
        for _, _, effectType in self.effectTypeInfos:
            if effectType == currentEffectType:
                break
            currentIndex = currentIndex + 1 
        self.effectTypeComBox.setCurrentIndex(currentIndex)

    def initUI(self):
        self.effectTypeComBox = self.initEffectOptionUI()
        self.strengthSlider = self.initSliderOptionUI(self.tr("Effect strength"), self.styleMap["strength"], 2, 10)
        self.addSeparator()

    def initEffectOptionUI(self):
        '''特效选项'''
        effectTypeComBox = ComboBox(self)
        for text, icon, enum in self.effectTypeInfos:
            effectTypeComBox.addItem(text=text, icon=icon, userData=enum)
        self.initTemplateOptionUI(self.tr("Effect"), effectTypeComBox)
        return effectTypeComBox

    def listenerEvent(self):
        self.strengthSlider.valueChanged.connect(self.strengthValueChangedHandler)
        self.effectTypeComBox.currentIndexChanged.connect(self.effectTypeComBoxHandle)

    def onEffectTypeChanged(self, effectType:AfterEffectType):
        self.styleMap["effectType"] = effectType
        self.refreshAttachItem()

    def strengthValueChangedHandler(self, value:float):
        self.styleMap["strength"] = value
        self.refreshAttachItem()

    def effectTypeComBoxHandle(self, index):
        comBox:ComboBox = self.effectTypeComBox
        self.styleMap["effectType"] = comBox.currentData()
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