from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from common import cfg
from .canvas_item_toolbar import *

class PolygonLineToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "color" : QColor(255, 0, 0),
            "width" : 5,
        }

    def initUI(self):
        self.colorPickerButton = self.initColorOptionUI(self.tr("Color"), self.styleMap["color"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(self.tr("Opacity"), self.opacity, 10, 100)

    def listenerEvent(self):
        self.colorPickerButton.colorChanged.connect(self.colorChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def refreshStyleUI(self):
        textColor:QColor = self.styleMap["color"]
        self.opacitySlider.setValue(self.opacity)
        self.colorPickerButton.setColor(textColor)

    def colorChangedHandler(self, color:QColor):
        self.styleMap["color"] = color
        self.refreshAttachItem()

    def opacityValueChangedHandler(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def wheelZoom(self, angleDelta:int):
        finalValue = self.styleMap["width"]

        # 自定义滚轮事件的行为
        if angleDelta > 1:
            # 放大
            finalValue = finalValue + 2
        else:
            # 缩小
            finalValue = max(finalValue - 2, 1)
        self.styleMap["width"] = finalValue

        if self.canvasItem != None and cfg.get(cfg.toolbarApplyWheelItem):
            self.canvasItem.resetStyle(self.styleMap.copy())