# coding=utf-8
from common import ScreenShotIcon, cfg
from .canvas_item_toolbar import *

class ShapeToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "brushColor" : cfg.get(cfg.shapeToolbarBrushColor),
            "penColor" : cfg.get(cfg.shapeToolbarPenColor),
            "penWidth" : cfg.get(cfg.shapeToolbarPenWidth),
            "penStyle" : cfg.get(cfg.shapeToolbarPenStyle),
            "shape" : cfg.get(cfg.shapeToolbarShape),
        }

        self.outlineTypeInfos = [
            (self.tr("Solid line"), Qt.PenStyle.SolidLine),
            (self.tr("Dash line"), Qt.PenStyle.DashLine),
        ]

        self.shapeTypeInfos = [
            (self.tr("Ellipse"), ScreenShotIcon.CIRCLE, CanvasShapeEnum.Ellipse),
            (self.tr("Triangle"), ScreenShotIcon.TRIANGLE, CanvasShapeEnum.Triangle),
            (self.tr("Rectangle"), ScreenShotIcon.RECTANGLE, CanvasShapeEnum.Rectangle),
            (self.tr("Star"), ScreenShotIcon.STAR, CanvasShapeEnum.Star),
        ]

    def refreshStyleUI(self):
        penColor:QColor = self.styleMap["penColor"]
        brushColor:QColor = self.styleMap["brushColor"]
        self.outlineColorPickerButton.setColor(penColor)
        self.backgroundColorPickerButton.setColor(brushColor)
        self.opacitySlider.setValue(self.opacity)

        currentShape = self.styleMap["shape"]
        currentIndex = 0
        for _, _, shapeType in self.shapeTypeInfos:
            if shapeType == currentShape:
                break
            currentIndex = currentIndex + 1 
        self.shapeComBox.setCurrentIndex(currentIndex)

        currentIndex = 0
        currentPenStyle = self.styleMap["penStyle"]
        for _, penStyle in self.outlineTypeInfos:
            if penStyle == currentPenStyle:
                break
            currentIndex = currentIndex + 1 
        self.outlineTypeComBox.setCurrentIndex(currentIndex)

    def initUI(self):
        self.shapeComBox = self.initShapeOptionUI()
        self.addSeparator()
        self.outlineTypeComBox, self.outlineColorPickerButton = self.initPenOptionUI()
        self.addSeparator()
        self.backgroundColorPickerButton = self.initColorOptionUI(self.tr("Brush"), Qt.GlobalColor.red)
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(self.tr("Opacity"), self.opacity, 10, 100)
    
    def outlineTypeComBoxHandle(self, index):
        comBox:ComboBox = self.outlineTypeComBox
        self.styleMap["penStyle"] = comBox.currentData()        
        self.refreshAttachItem()

    def shapeTypeComBoxHandle(self, index):
        comBox:ComboBox = self.shapeComBox
        self.styleMap["shape"] = comBox.currentData()
        self.refreshAttachItem()

    def listenerEvent(self):
        self.outlineColorPickerButton.colorChanged.connect(self.outlineColorChangedHandler)
        self.backgroundColorPickerButton.colorChanged.connect(self.backgroundColorChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)
        self.shapeComBox.currentIndexChanged.connect(self.shapeTypeComBoxHandle)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def outlineColorChangedHandler(self, color:QColor):
        self.styleMap["penColor"] = color
        self.refreshAttachItem()

    def backgroundColorChangedHandler(self, color:QColor):
        self.styleMap["brushColor"] = color
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
        self.initTemplateOptionUI(self.tr("Shape"), shapeComBox)
        return shapeComBox
    
    def initPenOptionUI(self):
        '''画笔选项'''

        optionName = self.tr("Pen")

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