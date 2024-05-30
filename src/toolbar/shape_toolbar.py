from common import ScreenShotIcon
from extend_widgets import *
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
            "brushColor" : QColor(255, 0, 0, 0),
            "penColor" : QColor(255, 0, 0),
            "penWidth" : 2,
            "penStyle" : Qt.PenStyle.SolidLine,
            "shape" : CanvasShapeEnum.Rectangle,
        }

        self.outlineTypeInfos = [
            ("实线", Qt.PenStyle.SolidLine),
            ("虚线", Qt.PenStyle.DashLine),
        ]

        self.shapeTypeInfos = [
            ("矩形", ScreenShotIcon.RECTANGLE, CanvasShapeEnum.Rectangle),
            ("圆形", ScreenShotIcon.CIRCLE, CanvasShapeEnum.Ellipse),
            ("三角形", ScreenShotIcon.CIRCLE, CanvasShapeEnum.Triangle),
            ("五角星", ScreenShotIcon.STAR, CanvasShapeEnum.Star),
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

        currentIndex = 0
        currentPenStyle = self.styleMap["penStyle"]
        for _, penStyle in self.outlineTypeInfos:
            if penStyle == currentPenStyle:
                break
            currentIndex = currentIndex + 1 
        self.outlineTypeComBox.setCurrentIndex(currentIndex)

    def refreshStyleUI(self):
        penColor:QColor = self.styleMap["penColor"]
        brushColor:QColor = self.styleMap["brushColor"]
        self.outlineColorPickerButton.setColor(penColor)
        self.backgroundColorPickerButton.setColor(brushColor)
        self.opacitySlider.setValue(self.opacity)

    def initUI(self):
        self.shapeComBox = self.initShapeOptionUI()
        self.addSeparator()
        self.outlineTypeComBox, self.outlineColorPickerButton = self.initPenOptionUI()
        self.addSeparator()
        self.backgroundColorPickerButton = self.initColorOptionUI("画刷", Qt.GlobalColor.red)
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI("不透明度", self.opacity, 10, 100)
    
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
        shapeComBox.currentIndexChanged.connect(self.shapeTypeComBoxHandle)
        self.initTemplateOptionUI("形状", shapeComBox)
        return shapeComBox
    
    def initPenOptionUI(self):
        '''画笔选项'''

        optionName = "画笔"

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