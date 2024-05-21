from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_item import *
from .canvas_item_toolbar import *

class ArrowToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "brushColor" : QColor(255, 0, 0, 100),
            "penColor" : QColor(255, 0, 0),
            "penWidth" : 2,
            "penStyle" : Qt.PenStyle.SolidLine,
        }

        self.outlineTypeInfos = [
            ("实线", Qt.PenStyle.SolidLine),
            ("虚线", Qt.PenStyle.DashLine),
        ]

    def initUI(self):
        self.outlineTypeComboBox = self.initComboBoxOptionUI("画笔风格", self.outlineTypeInfos, self.styleMap["penStyle"])
        self.penColorPickerButton = self.initColorOptionUI("画笔颜色", self.styleMap["penColor"])
        self.brushColorPickerButton = self.initColorOptionUI("笔刷颜色", self.styleMap["brushColor"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI("不透明度", self.opacity, 10, 100)

    def listenerEvent(self):
        self.outlineTypeComboBox.currentIndexChanged.connect(self.outlineTypeComboBoxHandle)
        self.penColorPickerButton.colorChanged.connect(self.penColorChangedHandler)
        self.brushColorPickerButton.colorChanged.connect(self.brushColorChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def selectItemChangedHandle(self, canvasItem:QGraphicsItem):
        currentIndex = 0
        currentPenStyle = self.styleMap["penStyle"]
        for _, penStyle in self.outlineTypeInfos:
            if penStyle == currentPenStyle:
                break
            currentIndex = currentIndex + 1 
        self.outlineTypeComboBox.setCurrentIndex(currentIndex)

    def refreshStyleUI(self):
        penColor:QColor = self.styleMap["penColor"]
        brushColor:QColor = self.styleMap["brushColor"]
        self.opacitySlider.setValue(self.opacity)
        self.penColorPickerButton.setColor(penColor)
        self.brushColorPickerButton.setColor(brushColor)

    def outlineTypeComboBoxHandle(self, index):
        comBox:ComboBox = self.outlineTypeComboBox
        self.styleMap["penStyle"] = comBox.currentData()
        self.refreshAttachItem()

    def penColorChangedHandler(self, color:QColor):
        self.styleMap["penColor"] = color
        self.refreshAttachItem()

    def brushColorChangedHandler(self, color:QColor):
        self.styleMap["brushColor"] = color
        self.refreshAttachItem()

    def opacityValueChangedHandler(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())