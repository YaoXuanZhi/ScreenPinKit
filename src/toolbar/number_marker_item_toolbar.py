# coding=utf-8
from common import cfg
from .canvas_item_toolbar import *

class NumberMarkerItemToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        defaultFont = QFont()
        defaultFontFamily = cfg.get(cfg.textEditToolbarFontFamily)
        defaultFont.setFamily(defaultFontFamily)
        self.styleMap = {
            "font" : defaultFont,
            "textColor" : cfg.get(cfg.numberMarkerItemToolbarTextColor),
            "backgroundColor" : cfg.get(cfg.numberMarkerItemToolbarBackgroundColor),
        }

    def initUI(self):
        self.textColorPickerButton = self.initColorOptionUI(self.tr("Text color"), self.styleMap["textColor"])
        self.fontPickerButton = self.initFontOptionUI(self.tr("Font"), self.styleMap["font"])
        self.addSeparator()
        self.backgroundColorPickerButton = self.initColorOptionUI(self.tr("Brush color"), self.styleMap["backgroundColor"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(self.tr("Opacity"), self.opacity, 10, 100)

    def refreshStyleUI(self):
        font:QFont = self.styleMap["font"]
        textColor:QColor = self.styleMap["textColor"]
        backgroundColor:QColor = self.styleMap["backgroundColor"]
        self.opacitySlider.setValue(self.opacity)
        self.textColorPickerButton.setColor(textColor)
        self.backgroundColorPickerButton.setColor(backgroundColor)
        self.fontPickerButton.setTargetFont(font)

    def textColorChangedHandler(self, color:QColor):
        self.styleMap["textColor"] = color
        self.refreshAttachItem()

    def backgroundColorChangedHandler(self, color:QColor):
        self.styleMap["backgroundColor"] = color
        self.refreshAttachItem()

    def fontChangedHandler(self, font:QFont):
        self.styleMap["font"] = font
        self.refreshAttachItem()

    def opacityValueChangedHandler(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def listenerEvent(self):
        self.textColorPickerButton.colorChanged.connect(self.textColorChangedHandler)
        self.backgroundColorPickerButton.colorChanged.connect(self.backgroundColorChangedHandler)
        self.fontPickerButton.fontChanged.connect(self.fontChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())