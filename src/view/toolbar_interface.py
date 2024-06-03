# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from common import cfg, ScreenShotIcon, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from typing import Union
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from extend_widgets import *
from canvas_item.after_effect_util import AfterEffectType
from canvas_item.canvas_shape_item import CanvasShapeEnum

class ToolbarInterface(QWidget):
    """ Toolbar interface """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("""
            ToolbarInterface{background: white}
            QLabel{
                font: 20px 'Segoe UI';
                background: rgb(242,242,242);
                border-radius: 8px;
            }
        """)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.textEditToolbarInterface = self.buildTextEditToolbar()
        self.eraseToolbarInterface = self.buildEraseToolbar()
        self.shapeToolbarInterface = self.buildShapeToolbar()
        self.arrowToolbarInterface = self.buildArrowToolbar()
        self.lineStripToolbarInterface = self.buildLineStripToolbar()
        self.markerPenToolbarInterface = self.buildMarkerPenToolbar()
        self.penToolbarInterface = self.buildPenToolbar()
        self.numberMarkerItemToolbarInterface = self.buildNumberMarkerItemToolbar()
        self.effectToolbarInterface = self.buildEffectToolBar()

        # add items to pivot
        self.addSubInterface(self.shapeToolbarInterface, 'shapeToolbarInterface', self.tr('ShapeToolbar'))
        self.addSubInterface(self.lineStripToolbarInterface, 'lineStripToolbarInterface', self.tr('LineStripToolbar'))
        self.addSubInterface(self.numberMarkerItemToolbarInterface, 'numberMarkerItemToolbarInterface', self.tr('NumberMarkerItemToolbar'))
        self.addSubInterface(self.arrowToolbarInterface, 'arrowToolbarInterface', self.tr('ArrowToolbar'))
        self.addSubInterface(self.markerPenToolbarInterface, 'markerPenToolbarInterface', self.tr('MarkerPenToolbar'))
        self.addSubInterface(self.penToolbarInterface, 'penToolbarInterface', self.tr('PenToolbar'))
        self.addSubInterface(self.textEditToolbarInterface, 'textEditToolbarInterface', self.tr('TextEditToolbar'))
        self.addSubInterface(self.eraseToolbarInterface, 'eraseToolbarInterface', self.tr('EraseToolbar'))
        self.addSubInterface(self.effectToolbarInterface, 'effectToolbarInterface', self.tr('EffectToolbar'))

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.textEditToolbarInterface)
        self.pivot.setCurrentItem(self.textEditToolbarInterface.objectName())

    def __onTextEditToolbarFontCardClicked(self):
        font, isOk = QFontDialog.getFont(
            cfg.textEditToolbarFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.textEditToolbarFont = font

    def __onNumberMarkerItemToolbarFontCardClicked(self):
        font, isOk = QFontDialog.getFont(
            cfg.numberMarkerItemToolbarFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.numberMarkerItemToolbarFont = font

    def buildEffectToolBar(self):
        effectToolBarGroup = SettingCardGroupLite(self)
        effectToolBarEffectTypeCard = ComboBoxSettingCardPlus(
            cfg.effectToolbarEffectType,
            ScreenShotIcon.FILL_REGION,
            self.tr('Effect type'),
            None,
            options=[
                (self.tr('Blur'), AfterEffectType.Blur), 
                (self.tr('Mosaic'), AfterEffectType.Mosaic), 
                (self.tr('Detail'), AfterEffectType.Detail), 
                (self.tr('Find_Edges'), AfterEffectType.Find_Edges), 
                (self.tr('Contour'), AfterEffectType.Contour),
                ],
            parent=effectToolBarGroup
        )
        effectToolBarStrengthCard = RangeSettingCard(
            cfg.effectToolbarStrength,
            FIF.HIGHTLIGHT,
            self.tr("Effect strength"),
            parent=effectToolBarGroup
        )

        effectToolBarGroup.addSettingCard(effectToolBarEffectTypeCard)
        effectToolBarGroup.addSettingCard(effectToolBarStrengthCard)
        return effectToolBarGroup

    def buildNumberMarkerItemToolbar(self):
        numberMarkerItemToolbarGroup = SettingCardGroupLite(self)
        numberMarkerItemToolbarFontCard = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Font family'),
            parent=numberMarkerItemToolbarGroup
        )
        numberMarkerItemToolbarTextColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarTextColor,
            FIF.PALETTE,
            self.tr("Text color"),
            parent=numberMarkerItemToolbarGroup,
            enableAlpha=True
        )
        numberMarkerItemToolbarPenWidthCard = RangeSettingCard(
            cfg.numberMarkerItemToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=numberMarkerItemToolbarGroup
        )
        numberMarkerItemToolbarPenColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=numberMarkerItemToolbarGroup,
            enableAlpha=True
        )
        numberMarkerItemToolbarPenStyleCard = ComboBoxSettingCardPlus(
            cfg.numberMarkerItemToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            None,
            options=[
                (self.tr("Solid line"), Qt.PenStyle.SolidLine), 
                (self.tr("Dash line"), Qt.PenStyle.DashLine),
            ],
            parent=numberMarkerItemToolbarGroup
        )
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarFontCard)
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarTextColorCard)
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarPenWidthCard)
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarPenColorCard)
        numberMarkerItemToolbarGroup.addSettingCard(numberMarkerItemToolbarPenStyleCard)

        numberMarkerItemToolbarFontCard.clicked.connect(self.__onNumberMarkerItemToolbarFontCardClicked)
        return numberMarkerItemToolbarGroup

    def buildPenToolbar(self):
        penToolbarGroup = SettingCardGroupLite(self)
        penToolbarWidthCard = RangeSettingCard(
            cfg.penToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=penToolbarGroup
        )
        penToolbarColorCard = ColorSettingCard(
            cfg.penToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=penToolbarGroup,
            enableAlpha=True
        )
        penToolbarGroup.addSettingCard(penToolbarColorCard)
        penToolbarGroup.addSettingCard(penToolbarWidthCard)
        return penToolbarGroup

    def buildMarkerPenToolbar(self):
        markerPenToolbarGroup = SettingCardGroupLite(self)
        markerPenToolbarWidthCard = RangeSettingCard(
            cfg.markerPenToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=markerPenToolbarGroup
        )
        markerPenToolbarColorCard = ColorSettingCard(
            cfg.markerPenToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=markerPenToolbarGroup,
            enableAlpha=True
        )
        markerPenToolbarGroup.addSettingCard(markerPenToolbarColorCard)
        markerPenToolbarGroup.addSettingCard(markerPenToolbarWidthCard)
        return markerPenToolbarGroup

    def buildLineStripToolbar(self):
        lineStripToolbarGroup = SettingCardGroupLite(self)
        lineStripToolbarWidthCard = RangeSettingCard(
            cfg.lineStripToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=lineStripToolbarGroup
        )
        lineStripToolbarColorCard = ColorSettingCard(
            cfg.lineStripToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=lineStripToolbarGroup,
            enableAlpha=True
        )
        lineStripToolbarGroup.addSettingCard(lineStripToolbarColorCard)
        lineStripToolbarGroup.addSettingCard(lineStripToolbarWidthCard)
        return lineStripToolbarGroup

    def buildArrowToolbar(self):
        arrowToolbarGroup = SettingCardGroupLite(self)
        arrowToolbarPenWidthCard = RangeSettingCard(
            cfg.arrowToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=arrowToolbarGroup
        )
        arrowToolbarBrushColorCard = ColorSettingCard(
            cfg.arrowToolbarBrushColor,
            FIF.PALETTE,
            self.tr("Brush color"),
            parent=arrowToolbarGroup,
            enableAlpha=True
        )
        arrowToolbarPenColorCard = ColorSettingCard(
            cfg.arrowToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=arrowToolbarGroup,
            enableAlpha=True
        )
        arrowToolbarPenStyleCard = ComboBoxSettingCardPlus(
            cfg.arrowToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            None,
            options=[
                (self.tr("Solid line"), Qt.PenStyle.SolidLine), 
                (self.tr("Dash line"), Qt.PenStyle.DashLine),
            ],
            parent=arrowToolbarGroup
        )

        arrowToolbarGroup.addSettingCard(arrowToolbarPenWidthCard)
        arrowToolbarGroup.addSettingCard(arrowToolbarPenColorCard)
        arrowToolbarGroup.addSettingCard(arrowToolbarBrushColorCard)
        arrowToolbarGroup.addSettingCard(arrowToolbarPenStyleCard)
        return arrowToolbarGroup

    def buildEraseToolbar(self):
        eraseToolbarGroup = SettingCardGroupLite(self)
        eraseToolbarWidthCard = RangeSettingCard(
            cfg.eraseToolbarWidth,
            FIF.HIGHTLIGHT,
            self.tr("Eraser width"),
            parent=eraseToolbarGroup
        )
        eraseToolbarGroup.addSettingCard(eraseToolbarWidthCard)
        return eraseToolbarGroup

    def buildTextEditToolbar(self):
        textEditToolbarGroup = SettingCardGroupLite(self)
        textEditToolbarFontCard = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Font family'),
            parent=textEditToolbarGroup
        )
        textEditToolbarFontSizeCard = RangeSettingCard(
            cfg.textEditToolbarFontSize,
            FIF.FONT_SIZE,
            self.tr('Font size'),
            parent=textEditToolbarGroup
        )
        textEditToolbarTextColorCard = ColorSettingCard(
            cfg.textEditToolbarTextColor,
            FIF.PALETTE,
            self.tr("Text color"),
            parent=textEditToolbarGroup,
            enableAlpha=True
        )

        textEditToolbarGroup.addSettingCard(textEditToolbarFontCard)
        textEditToolbarGroup.addSettingCard(textEditToolbarFontSizeCard)
        textEditToolbarGroup.addSettingCard(textEditToolbarTextColorCard)
        textEditToolbarFontCard.clicked.connect(self.__onTextEditToolbarFontCardClicked)
        return textEditToolbarGroup

    def buildShapeToolbar(self):
        # shapeToolbar
        shapeToolbarGroup = SettingCardGroupLite(self)
        shapeToolbarPenWidthCard = RangeSettingCard(
            cfg.shapeToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=shapeToolbarGroup
        )
        shapeToolbarBrushColorCard = ColorSettingCard(
            cfg.shapeToolbarBrushColor,
            FIF.PALETTE,
            self.tr("Brush color"),
            parent=shapeToolbarGroup,
            enableAlpha=True
        )
        shapeToolbarPenColorCard = ColorSettingCard(
            cfg.shapeToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=shapeToolbarGroup,
            enableAlpha=True
        )
        shapeToolbarPenStyleCard = ComboBoxSettingCardPlus(
            cfg.shapeToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            None,
            options=[
                (self.tr("Solid line"), Qt.PenStyle.SolidLine), 
                (self.tr("Dash line"), Qt.PenStyle.DashLine),
            ],
            parent=shapeToolbarGroup
        )
        shapeToolbarEffectTypeCard = ComboBoxSettingCardPlus(
            cfg.shapeToolbarShape,
            ScreenShotIcon.SHAPE,
            self.tr('Shape'),
            None,
            options=[
                ('Ellipse', CanvasShapeEnum.Ellipse),
                ('Triangle', CanvasShapeEnum.Triangle),
                ('Rectangle', CanvasShapeEnum.Rectangle),
                ('Star', CanvasShapeEnum.Star),
                ],
            parent=shapeToolbarGroup
        )

        shapeToolbarGroup.addSettingCard(shapeToolbarPenWidthCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarPenColorCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarBrushColorCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarPenStyleCard)
        shapeToolbarGroup.addSettingCard(shapeToolbarEffectTypeCard)
        return shapeToolbarGroup

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        self.adjustSize()

class ToolbarSettingCard(ScrollArea):
    """ Toolbar card with a push button """

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.interface = ToolbarInterface(self)

        self.resize(400, 300)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.interface)
        return
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.expandLayout.addWidget(self.interface)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 30, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        # self.scrollWidget.adjustSize()
        self.adjustSize()
