# coding=utf-8
from common import cfg
from .canvas_item_toolbar import *


class NumberMarkerItemToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity: int = 100
        defaultFont = QFont()
        defaultFontFamily = cfg.get(cfg.numberMarkerItemToolbarFontFamily)
        defaultFont.setFamily(defaultFontFamily)
        self.styleMap = {
            "font": defaultFont,
            "textColor": cfg.get(cfg.numberMarkerItemToolbarTextColor),
            "penColor": cfg.get(cfg.numberMarkerItemToolbarPenColor),
            "penWidth": cfg.get(cfg.numberMarkerItemToolbarPenWidth),
            "penStyle": cfg.get(cfg.numberMarkerItemToolbarPenStyle),
            "brushColor": cfg.get(cfg.numberMarkerItemToolbarBrushColor),
        }

        self.penStyleInfos = [
            (self.tr("Solid line"), Qt.PenStyle.SolidLine),
            (self.tr("Dash line"), Qt.PenStyle.DashLine),
        ]

    def initUI(self):
        self.penStyleComBox, self.penColorPickerButton = self.initPenOptionUI()
        self.addSeparator()
        self.brushColorPickerButton = self.initColorOptionUI(
            self.tr("Brush"), self.styleMap["brushColor"]
        )
        self.addSeparator()
        self.textColorPickerButton = self.initColorOptionUI(
            self.tr("Text color"), self.styleMap["textColor"]
        )
        self.fontPickerButton = self.initFontOptionUI(
            self.tr("Font"), self.styleMap["font"]
        )
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(
            self.tr("Opacity"), self.opacity, 10, 100
        )

    def penStyleComBoxHandle(self, index):
        comBox: ComboBox = self.penStyleComBox
        self.styleMap["penStyle"] = comBox.currentData()
        self.refreshAttachItem()

    def refreshStyleUI(self):
        font: QFont = self.styleMap["font"]
        textColor: QColor = self.styleMap["textColor"]
        penColor: QColor = self.styleMap["penColor"]
        brushColor: QColor = self.styleMap["brushColor"]
        self.penColorPickerButton.setColor(penColor)
        self.brushColorPickerButton.setColor(brushColor)
        self.textColorPickerButton.setColor(textColor)
        self.fontPickerButton.setTargetFont(font)
        self.opacitySlider.setValue(self.opacity)

        currentIndex = 0
        currentPenStyle = self.styleMap["penStyle"]
        for _, penStyle in self.penStyleInfos:
            if penStyle == currentPenStyle:
                break
            currentIndex = currentIndex + 1
        self.penStyleComBox.setCurrentIndex(currentIndex)

    def textColorChangedHandle(self, color: QColor):
        self.styleMap["textColor"] = color
        self.refreshAttachItem()

    def penStyleComBoxHandle(self, index):
        comBox: ComboBox = self.penStyleComBox
        self.styleMap["penStyle"] = comBox.currentData()
        self.refreshAttachItem()

    def fontChangedHandle(self, font: QFont):
        self.styleMap["font"] = font
        self.refreshAttachItem()

    def opacityValueChangedHandle(self, value: float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def listenerEvent(self):
        self.penColorPickerButton.colorChanged.connect(self.penColorChangedHandle)
        self.brushColorPickerButton.colorChanged.connect(self.brushColorChangedHandle)
        self.textColorPickerButton.colorChanged.connect(self.textColorChangedHandle)
        self.fontPickerButton.fontChanged.connect(self.fontChangedHandle)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandle)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def penColorChangedHandle(self, color: QColor):
        self.styleMap["penColor"] = color
        self.refreshAttachItem()

    def brushColorChangedHandle(self, color: QColor):
        self.styleMap["brushColor"] = color
        self.refreshAttachItem()

    def initPenOptionUI(self):
        """画笔选项"""

        optionName = self.tr("Pen")

        # 描边风格选项
        penStyleComBox = ComboBox(self)
        for text, enum in self.penStyleInfos:
            penStyleComBox.addItem(text=text, userData=enum)
        penStyleComBox.currentIndexChanged.connect(self.penStyleComBoxHandle)

        # 颜色选项
        colorPickerButton = ColorPickerButtonEx(
            Qt.GlobalColor.yellow, optionName, self, enableAlpha=True
        )
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

    def wheelZoom(self, angleDelta: int):
        finalValue = self.styleMap["penWidth"]
        (minValue, maxValue) = cfg.numberMarkerItemToolbarPenWidth.range

        if angleDelta > 1:
            finalValue = min(maxValue, finalValue + 1)
        else:
            finalValue = max(minValue, finalValue - 1)
        self.styleMap["penWidth"] = finalValue

        if self.canvasItem != None and cfg.get(cfg.toolbarApplyWheelItem):
            self.canvasItem.resetStyle(self.styleMap.copy())
