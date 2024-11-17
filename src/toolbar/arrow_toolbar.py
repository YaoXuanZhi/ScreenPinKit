# coding=utf-8
from common import cfg
from .canvas_item_toolbar import *


class ArrowToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity: int = 100
        self.styleMap = {
            "brushColor": cfg.get(cfg.arrowToolbarBrushColor),
            "penColor": cfg.get(cfg.arrowToolbarPenColor),
            "penWidth": cfg.get(cfg.arrowToolbarPenWidth),
            "penStyle": cfg.get(cfg.arrowToolbarPenStyle),
        }

        self.penStyleInfos = [
            (self.tr("Solid line"), Qt.PenStyle.SolidLine),
            (self.tr("Dash line"), Qt.PenStyle.DashLine),
        ]

    def initUI(self):
        self.penStyleComboBox, self.penColorPickerButton = self.initPenOptionUI()
        self.addSeparator()
        self.brushColorPickerButton = self.initColorOptionUI(
            self.tr("Brush"), self.styleMap["brushColor"]
        )
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI(
            self.tr("Opacity"), self.opacity, 10, 100
        )

    def listenerEvent(self):
        self.penStyleComboBox.currentIndexChanged.connect(self.penStyleComboBoxHandle)
        self.penColorPickerButton.colorChanged.connect(self.penColorChangedHandle)
        self.brushColorPickerButton.colorChanged.connect(self.brushColorChangedHandle)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandle)

    def refreshStyleUI(self):
        penColor: QColor = self.styleMap["penColor"]
        brushColor: QColor = self.styleMap["brushColor"]
        self.opacitySlider.setValue(self.opacity)
        self.penColorPickerButton.setColor(penColor)
        self.brushColorPickerButton.setColor(brushColor)

        currentIndex = 0
        currentPenStyle = self.styleMap["penStyle"]
        for _, penStyle in self.penStyleInfos:
            if penStyle == currentPenStyle:
                break
            currentIndex = currentIndex + 1
        self.penStyleComboBox.setCurrentIndex(currentIndex)

    def penStyleComboBoxHandle(self, index):
        comBox: ComboBox = self.penStyleComboBox
        self.styleMap["penStyle"] = comBox.currentData()
        self.refreshAttachItem()

    def penColorChangedHandle(self, color: QColor):
        self.styleMap["penColor"] = color
        self.refreshAttachItem()

    def brushColorChangedHandle(self, color: QColor):
        self.styleMap["brushColor"] = color
        self.refreshAttachItem()

    def opacityValueChangedHandle(self, value: float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def initPenOptionUI(self):
        """画笔选项"""

        optionName = self.tr("Pen")

        # 描边风格选项
        penStyleComBox = ComboBox(self)
        for text, enum in self.penStyleInfos:
            penStyleComBox.addItem(text=text, userData=enum)

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
