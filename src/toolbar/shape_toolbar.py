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

        self.penStyleInfos = [
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
        self.penColorPickerButton.setColor(penColor)
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
        for _, penStyle in self.penStyleInfos:
            if penStyle == currentPenStyle:
                break
            currentIndex = currentIndex + 1 
        self.penStyleComBox.setCurrentIndex(currentIndex)

    def initUI(self):
        self.shapeComBox = self.initShapeOptionUI()
        self.addSeparator()
        self.penStyleComBox, self.penColorPickerButton = self.initPenOptionUI()
        self.addSeparator()
        self.backgroundColorPickerButton = self.initColorOptionUI(self.tr("Brush"), Qt.GlobalColor.red)
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(self.tr("Opacity"), self.opacity, 10, 100)
    
    def penStyleComBoxHandle(self, index):
        comBox:ComboBox = self.penStyleComBox
        self.styleMap["penStyle"] = comBox.currentData()        
        self.refreshAttachItem()

    def shapeTypeComBoxHandle(self, index):
        comBox:ComboBox = self.shapeComBox
        self.styleMap["shape"] = comBox.currentData()
        self.refreshAttachItem()

    def listenerEvent(self):
        self.penColorPickerButton.colorChanged.connect(self.penColorChangedHandle)
        self.backgroundColorPickerButton.colorChanged.connect(self.backgroundColorChangedHandle)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandle)
        self.shapeComBox.currentIndexChanged.connect(self.shapeTypeComBoxHandle)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def penColorChangedHandle(self, color:QColor):
        self.styleMap["penColor"] = color
        self.refreshAttachItem()

    def backgroundColorChangedHandle(self, color:QColor):
        self.styleMap["brushColor"] = color
        self.refreshAttachItem()

    def opacityValueChangedHandle(self, value:float):
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
        penStyleComBox = ComboBox(self)
        for text, enum in self.penStyleInfos:
            penStyleComBox.addItem(text=text, userData=enum)
        penStyleComBox.currentIndexChanged.connect(self.penStyleComBoxHandle)

        # 颜色选项
        colorPickerButton = ColorPickerButtonEx(Qt.GlobalColor.yellow, optionName, self, enableAlpha=True)
        colorPickerButton.setCheckable(True)
        colorPickerButton.setFixedSize(30, 30)

        # 布局
        optionView = QWidget()
        optionLayout = QHBoxLayout()
        optionView.setLayout(optionLayout)
        optionLayout.addWidget(QLabel(optionName))
        optionLayout.addWidget(penStyleComBox)
        optionLayout.addWidget(colorPickerButton)
        self.addWidget(optionView)

        return penStyleComBox, colorPickerButton

    def wheelZoom(self, angleDelta:int):
        finalValue = self.styleMap["penWidth"]
        (minValue, maxValue) = cfg.shapeToolbarPenWidth.range

        if angleDelta > 1:
            finalValue = min(maxValue, finalValue + 1)
        else:
            finalValue = max(minValue, finalValue - 1)
        self.styleMap["penWidth"] = finalValue

        if self.canvasItem != None and cfg.get(cfg.toolbarApplyWheelItem):
            self.canvasItem.resetStyle(self.styleMap.copy())