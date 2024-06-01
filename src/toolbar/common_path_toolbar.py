# coding=utf-8
from .canvas_item_toolbar import *

class CommonPathToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "color" : QColor(100, 200, 150),
            "width" : 5,
        }

    def initUI(self):
        self.colorPickerButton = self.initColorOptionUI(self.tr("Color"), self.styleMap["color"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(self.tr("Opacity"), self.opacity, 10, 100)

    def listenerEvent(self):
        self.colorPickerButton.colorChanged.connect(self.colorChangedHandle)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandle)

    def refreshStyleUI(self):
        textColor:QColor = self.styleMap["color"]
        self.opacitySlider.setValue(self.opacity)
        self.colorPickerButton.setColor(textColor)

    def colorChangedHandle(self, color:QColor):
        self.styleMap["color"] = color
        self.refreshAttachItem()

    def opacityValueChangedHandle(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())