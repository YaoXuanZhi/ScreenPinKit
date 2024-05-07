from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_item import *
from .canvas_item_toolbar import *

class TextEditToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "font" : QFont(),
            "textColor" : QColor(100, 200, 150),
        }

    def initUI(self):
        self.boldButton = self.addAction(Action(ScreenShotIcon.RECTANGLE, '加粗', triggered=self.fontExtStyleChangedHandler))
        self.boldButton.setCheckable(True)
        self.italicButton = self.addAction(Action(ScreenShotIcon.ARROW, '斜体', triggered=self.fontExtStyleChangedHandler))
        self.italicButton.setCheckable(True)
        self.textColorPickerButton = self.initColorOptionUI("文本颜色", self.styleMap["textColor"])
        self.fontPickerButton = self.initFontOptionUI("字体选择", self.styleMap["font"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI("不透明度")

    def fontExtStyleChangedHandler(self):
        font:QFont = self.styleMap["font"]
        font.setBold(self.boldButton.isChecked())
        font.setItalic(self.italicButton.isChecked())

        self.fontPickerButton.setTargetFont(font)

        self.refreshAttachItem()

    # def selectItemChangedHandle(self, canvasItem:QGraphicsItem):
    #     # 更新形状选项
    #     font = self.styleMap["font"]
    #     currentIndex = 0
    #     for _, _, shapeType in self.shapeTypeInfos:
    #         if shapeType == currentShape:
    #             break
    #         currentIndex = currentIndex + 1 
    #     self.shapeComBox.setCurrentIndex(currentIndex)

    def refreshStyleUI(self):
        font:QFont = self.styleMap["font"]
        textColor:QColor = self.styleMap["textColor"]
        self.boldButton.setChecked(font.bold())
        self.italicButton.setChecked(font.italic())
        self.opacitySlider.setValue(self.opacity)
        self.textColorPickerButton.setColor(textColor)
        self.fontPickerButton.setTargetFont(font)

    def textColorChangedHandler(self, color:QColor):
        self.styleMap["textColor"] = color
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
        self.fontPickerButton.fontChanged.connect(self.fontChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.resetStyle(self.styleMap.copy())