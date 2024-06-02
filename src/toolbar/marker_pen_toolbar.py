# coding=utf-8
from common import cfg
from .canvas_item_toolbar import *

class MarkerPenToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "penColor" : cfg.get(cfg.markerPenToolbarPenColor),
            "penWidth" : cfg.get(cfg.markerPenToolbarPenWidth),
        }

    def initUI(self):
        self.colorPickerButton = self.initColorOptionUI(self.tr("Color"), self.styleMap["penColor"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(self.tr("Opacity"), self.opacity, 10, 100)

    def listenerEvent(self):
        self.colorPickerButton.colorChanged.connect(self.colorChangedHandle)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandle)

    def refreshStyleUI(self):
        penColor:QColor = self.styleMap["penColor"]
        self.opacitySlider.setValue(self.opacity)
        self.colorPickerButton.setColor(penColor)

    def colorChangedHandle(self, color:QColor):
        self.styleMap["penColor"] = color
        self.refreshAttachItem()

    def opacityValueChangedHandle(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def wheelZoom(self, angleDelta:int):
        finalValue = self.styleMap["penWidth"]
        (minValue, maxValue) = cfg.markerPenToolbarPenWidth.range

        # 自定义滚轮事件的行为
        if angleDelta > 1:
            # 放大
            finalValue = min(maxValue, finalValue + 2)
        else:
            # 缩小
            finalValue = max(minValue, finalValue - 2)
        self.styleMap["penWidth"] = finalValue

        if self.canvasItem != None and cfg.get(cfg.toolbarApplyWheelItem):
            self.canvasItem.resetStyle(self.styleMap.copy())