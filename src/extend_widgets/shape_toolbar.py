from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_editor import *
from canvas_item import *
from .canvas_item_toolbar import *

class ShapeToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "brush" : QBrush(QColor(255, 0, 0, 100)),
            "pen" : QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine),
            "shape" : CanvasClosedShapeEnum.Rectangle,
        }

        self.outlineTypeInfos = [
            ("实线", Qt.PenStyle.SolidLine),
            ("虚线", Qt.PenStyle.DashLine),
        ]

        self.shapeTypeInfos = [
            ("矩形", ScreenShotIcon.RECTANGLE, CanvasClosedShapeEnum.Rectangle),
            ("圆形", ScreenShotIcon.CIRCLE, CanvasClosedShapeEnum.Ellipse),
            ("五角星", ScreenShotIcon.STAR, CanvasClosedShapeEnum.Star),
        ]

    def selectItemChangedHandle(self, canvasItem:QGraphicsItem):
        # 更新形状选项
        currentShape = self.styleMap["shape"]
        currentIndex = 0
        for _, _, shapeType in self.shapeTypeInfos:
            if shapeType == currentShape:
                break
            currentIndex = currentIndex + 1 
        self.shapeComBox.setCurrentIndex(currentIndex)

    def refreshStyleUI(self):
        pen:QPen = self.styleMap["pen"]
        brush:QBrush = self.styleMap["brush"]
        self.outlineColorPickerButton.setColor(pen.color())
        self.backgroundColorPickerButton.setColor(brush.color())
        self.opacitySlider.setValue(self.opacity)

    def initUI(self):
        self.shapeComBox = self.initShapeOptionUI()
        self.addSeparator()
        self.outlineTypeComBox, self.outlineColorPickerButton = self.initOutlineOptionUI()
        self.addSeparator()
        self.backgroundColorPickerButton = self.initColorOptionUI("背景", Qt.GlobalColor.red)
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI("不透明度")
    
    def outlineTypeComBoxHandle(self, index):
        comBox:ComboBox = self.outlineTypeComBox
        print(f"=====> {comBox.currentData()}")

    def shapeTypeComBoxHandle(self, index):
        comBox:ComboBox = self.shapeComBox
        self.styleMap["shape"] = comBox.currentData()
        self.refreshAttachItem()

    def listenerEvent(self):
        self.outlineColorPickerButton.colorChanged.connect(self.outlineColorChangedHandler)
        self.backgroundColorPickerButton.colorChanged.connect(self.backgroundColorChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def outlineColorChangedHandler(self, color:QColor):
        pen:QPen = self.styleMap["pen"]        
        pen.setColor(color)

        self.refreshAttachItem()

    def backgroundColorChangedHandler(self, color:QColor):
        brush:QBrush = self.styleMap["brush"]
        brush.setColor(color)

        self.refreshAttachItem()

    def opacityValueChangedHandler(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def initShapeOptionUI(self):
        '''形状选项'''
        shapeComBox = ComboBox(self)
        for text, icon, enum in self.shapeTypeInfos:
            shapeComBox.addItem(text=text, icon=icon, userData=enum)
        shapeComBox.currentIndexChanged.connect(self.shapeTypeComBoxHandle)
        self.initTemplateOptionUI("形状", shapeComBox)
        return shapeComBox
    
    def initOutlineOptionUI(self):
        '''描边选项'''

        optionName = "描边"

        # 描边风格选项
        outlineTypeComBox = ComboBox(self)
        for text, enum in self.outlineTypeInfos:
            outlineTypeComBox.addItem(text=text, userData=enum)
        outlineTypeComBox.currentIndexChanged.connect(self.outlineTypeComBoxHandle)

        # 颜色选项
        colorPickerButton = ColorPickerButtonEx(Qt.GlobalColor.yellow, optionName, self, enableAlpha=True)
        colorPickerButton.setCheckable(True)
        colorPickerButton.setFixedSize(30, 30)

        # 布局
        optionView = QWidget()
        optionLayout = QHBoxLayout()
        optionView.setLayout(optionLayout)
        optionLayout.addWidget(QLabel(optionName))
        optionLayout.addWidget(outlineTypeComBox)
        optionLayout.addWidget(colorPickerButton)
        self.addWidget(optionView)

        return outlineTypeComBox, colorPickerButton