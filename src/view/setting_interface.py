# coding:utf-8
from common import cfg, ScreenShotIcon, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog

class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = pyqtSignal()
    cacheFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # general
        self.generalGroup = SettingCardGroup(
            self.tr("General"), self.scrollWidget)
        self.cacheFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.DOWNLOAD,
            self.tr("Cache directory"),
            cfg.get(cfg.cacheFolder),
            self.generalGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # textEditToolbar
        self.textEditToolbarGroup = SettingCardGroup(self.tr("TextEditToolbar"), self.scrollWidget)
        self.textEditToolbarFontCard = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Font family'),
            parent=self.textEditToolbarGroup
        )
        self.textEditToolbarFontSizeCard = RangeSettingCard(
            cfg.textEditToolbarFontSize,
            FIF.FONT_SIZE,
            self.tr('Font size'),
            parent=self.textEditToolbarGroup
        )
        self.textEditToolbarTextColorCard = ColorSettingCard(
            cfg.textEditToolbarTextColor,
            FIF.PALETTE,
            self.tr("Text color"),
            parent=self.textEditToolbarGroup,
            enableAlpha=True
        )

        # effectToolBar
        self.effectToolBarGroup = SettingCardGroup(self.tr("EffectToolBar"), self.scrollWidget)
        self.effectToolBarEffectTypeCard = ComboBoxSettingCard(
            cfg.effectToolbarEffectType,
            ScreenShotIcon.FILL_REGION,
            self.tr('Effect type'),
            self.tr('Set your default effect type'),
            texts=['Blur', 'Mosaic'],
            parent=self.effectToolBarGroup
        )
        self.effectToolBarStrengthCard = RangeSettingCard(
            cfg.effectToolbarStrength,
            FIF.HIGHTLIGHT,
            self.tr("Effect strength"),
            parent=self.effectToolBarGroup
        )

        # eraseToolbar
        self.eraseToolbarGroup = SettingCardGroup(self.tr("EraseToolbar"), self.scrollWidget)
        self.eraseToolbarWidthCard = RangeSettingCard(
            cfg.eraseToolbarWidth,
            FIF.HIGHTLIGHT,
            self.tr("Eraser width"),
            parent=self.eraseToolbarGroup
        )

        # shapeToolbar
        self.shapeToolbarGroup = SettingCardGroup(self.tr("ShapeToolbar"), self.scrollWidget)
        self.shapeToolbarPenWidthCard = RangeSettingCard(
            cfg.shapeToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=self.shapeToolbarGroup
        )
        self.shapeToolbarBrushColorCard = ColorSettingCard(
            cfg.shapeToolbarBrushColor,
            FIF.PALETTE,
            self.tr("Brush color"),
            parent=self.shapeToolbarGroup,
            enableAlpha=True
        )
        self.shapeToolbarPenColorCard = ColorSettingCard(
            cfg.shapeToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=self.shapeToolbarGroup,
            enableAlpha=True
        )
        self.shapeToolbarPenStyleCard = OptionsSettingCard(
            cfg.shapeToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            self.tr("Change brush style"),
            texts=[
                "SolidLine", "DashLine"
            ],
            parent=self.shapeToolbarGroup
        )
        self.shapeToolbarEffectTypeCard = ComboBoxSettingCard(
            cfg.shapeToolbarShape,
            ScreenShotIcon.SHAPE,
            self.tr('Shape'),
            self.tr('Set your default shape'),
            texts=['Ellipse', 'Triangle', 'Rectangle', 'Star'],
            parent=self.shapeToolbarGroup
        )

        # arrowToolbar
        self.arrowToolbarGroup = SettingCardGroup(self.tr("ArrowToolbar"), self.scrollWidget)
        self.arrowToolbarPenWidthCard = RangeSettingCard(
            cfg.arrowToolbarPenWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=self.arrowToolbarGroup
        )
        self.arrowToolbarBrushColorCard = ColorSettingCard(
            cfg.arrowToolbarBrushColor,
            FIF.PALETTE,
            self.tr("Brush color"),
            parent=self.arrowToolbarGroup,
            enableAlpha=True
        )
        self.arrowToolbarPenColorCard = ColorSettingCard(
            cfg.arrowToolbarPenColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=self.arrowToolbarGroup,
            enableAlpha=True
        )
        self.arrowToolbarPenStyleCard = OptionsSettingCard(
            cfg.arrowToolbarPenStyle,
            FIF.HIGHTLIGHT,
            self.tr("Pen style"),
            self.tr("Change brush style"),
            texts=[
                "SolidLine", "DashLine"
            ],
            parent=self.arrowToolbarGroup
        )

        # lineStripToolbar
        self.lineStripToolbarGroup = SettingCardGroup(self.tr("LineStripToolbar"), self.scrollWidget)
        self.lineStripToolbarWidthCard = RangeSettingCard(
            cfg.lineStripToolbarWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=self.lineStripToolbarGroup
        )
        self.lineStripToolbarColorCard = ColorSettingCard(
            cfg.lineStripToolbarColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=self.lineStripToolbarGroup,
            enableAlpha=True
        )

        # markerPenToolbar
        self.markerPenToolbarGroup = SettingCardGroup(self.tr("MarkerPenToolbar"), self.scrollWidget)
        self.markerPenToolbarFontCard = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Font family'),
            parent=self.markerPenToolbarGroup
        )
        self.markerPenToolbarWidthCard = RangeSettingCard(
            cfg.markerPenToolbarWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=self.markerPenToolbarGroup
        )
        self.markerPenToolbarColorCard = ColorSettingCard(
            cfg.markerPenToolbarColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=self.markerPenToolbarGroup,
            enableAlpha=True
        )

        # penToolbar
        self.penToolbarGroup = SettingCardGroup(self.tr("PenToolbar"), self.scrollWidget)
        self.penToolbarWidthCard = RangeSettingCard(
            cfg.penToolbarWidth,
            FIF.FONT_SIZE,
            self.tr("Pen width"),
            parent=self.penToolbarGroup
        )
        self.penToolbarColorCard = ColorSettingCard(
            cfg.penToolbarColor,
            FIF.PALETTE,
            self.tr("Pen color"),
            parent=self.penToolbarGroup,
            enableAlpha=True
        )

        # numberMarkerItemToolbar
        self.numberMarkerItemToolbarGroup = SettingCardGroup(self.tr("NumberMarkerItemToolbar"), self.scrollWidget)
        self.numberMarkerItemToolbarTextColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarTextColor,
            FIF.PALETTE,
            self.tr("Text color"),
            parent=self.numberMarkerItemToolbarGroup,
            enableAlpha=True
        )
        self.numberMarkerItemToolbarBackgroundColorCard = ColorSettingCard(
            cfg.numberMarkerItemToolbarBackgroundColor,
            FIF.PALETTE,
            self.tr("Background color"),
            parent=self.numberMarkerItemToolbarGroup,
            enableAlpha=True
        )

        # shadowStyle
        self.shadowStyleGroup = SettingCardGroup(self.tr("ShadowStyle"), self.scrollWidget)
        self.shadowStyleFocusColorCard = ColorSettingCard(
            cfg.focusShadowColor,
            FIF.PALETTE,
            self.tr("Focus color"),
            parent=self.shadowStyleGroup,
            enableAlpha=True
        )
        self.shadowStyleUnfocusColorCard = ColorSettingCard(
            cfg.unFocusShadowColor,
            FIF.PALETTE,
            self.tr("Unfocus color"),
            parent=self.shadowStyleGroup,
            enableAlpha=True
        )
        self.shadowStyleUseRoundStyleCard = SwitchSettingCard(
            FIF.VOLUME,
            self.tr('Use round style'),
            None,
            configItem=cfg.useRoundStyle,
            parent=self.shadowStyleGroup
        )
        self.shadowStyleIsSaveWithShadowCard = SwitchSettingCard(
            FIF.FEEDBACK,
            self.tr('Save screenshot with shadow'),
            None,
            configItem=cfg.isSaveWithShadow,
            parent=self.shadowStyleGroup
        )
        self.ShadowStyleisCopyWithShadowCard = SwitchSettingCard(
            FIF.CHECKBOX,
            self.tr('Copy screenshot with shadow'),
            None,
            configItem=cfg.isCopyWithShadow,
            parent=self.shadowStyleGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve ScreenPinKit by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(600, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 30, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # add cards to group
        self.generalGroup.addSettingCard(self.cacheFolderCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.textEditToolbarGroup.addSettingCard(self.textEditToolbarFontCard)
        self.textEditToolbarGroup.addSettingCard(self.textEditToolbarFontSizeCard)
        self.textEditToolbarGroup.addSettingCard(self.textEditToolbarTextColorCard)

        self.effectToolBarGroup.addSettingCard(self.effectToolBarStrengthCard)
        self.effectToolBarGroup.addSettingCard(self.effectToolBarEffectTypeCard)

        self.eraseToolbarGroup.addSettingCard(self.eraseToolbarWidthCard)

        self.shapeToolbarGroup.addSettingCard(self.shapeToolbarPenWidthCard)
        self.shapeToolbarGroup.addSettingCard(self.shapeToolbarPenColorCard)
        self.shapeToolbarGroup.addSettingCard(self.shapeToolbarBrushColorCard)
        self.shapeToolbarGroup.addSettingCard(self.shapeToolbarPenStyleCard)
        self.shapeToolbarGroup.addSettingCard(self.shapeToolbarEffectTypeCard)

        self.arrowToolbarGroup.addSettingCard(self.arrowToolbarPenWidthCard)
        self.arrowToolbarGroup.addSettingCard(self.arrowToolbarPenColorCard)
        self.arrowToolbarGroup.addSettingCard(self.arrowToolbarBrushColorCard)
        self.arrowToolbarGroup.addSettingCard(self.arrowToolbarPenStyleCard)

        self.lineStripToolbarGroup.addSettingCard(self.lineStripToolbarWidthCard)
        self.lineStripToolbarGroup.addSettingCard(self.lineStripToolbarColorCard)

        self.markerPenToolbarGroup.addSettingCard(self.markerPenToolbarFontCard)
        self.markerPenToolbarGroup.addSettingCard(self.markerPenToolbarWidthCard)
        self.markerPenToolbarGroup.addSettingCard(self.markerPenToolbarColorCard)

        self.penToolbarGroup.addSettingCard(self.penToolbarWidthCard)
        self.penToolbarGroup.addSettingCard(self.penToolbarColorCard)

        self.numberMarkerItemToolbarGroup.addSettingCard(self.numberMarkerItemToolbarTextColorCard)
        self.numberMarkerItemToolbarGroup.addSettingCard(self.numberMarkerItemToolbarBackgroundColorCard)

        self.shadowStyleGroup.addSettingCard(self.shadowStyleFocusColorCard)
        self.shadowStyleGroup.addSettingCard(self.shadowStyleUnfocusColorCard)
        self.shadowStyleGroup.addSettingCard(self.shadowStyleUseRoundStyleCard)
        self.shadowStyleGroup.addSettingCard(self.shadowStyleIsSaveWithShadowCard)
        self.shadowStyleGroup.addSettingCard(self.ShadowStyleisCopyWithShadowCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.generalGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.textEditToolbarGroup)
        self.expandLayout.addWidget(self.effectToolBarGroup)
        self.expandLayout.addWidget(self.eraseToolbarGroup)
        self.expandLayout.addWidget(self.shapeToolbarGroup)
        self.expandLayout.addWidget(self.arrowToolbarGroup)
        self.expandLayout.addWidget(self.lineStripToolbarGroup)
        self.expandLayout.addWidget(self.markerPenToolbarGroup)
        self.expandLayout.addWidget(self.penToolbarGroup)
        self.expandLayout.addWidget(self.numberMarkerItemToolbarGroup)
        self.expandLayout.addWidget(self.shadowStyleGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            cfg.desktopLyricFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.desktopLyricFont = font

    def __onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.cacheFolderCard.setContent(folder)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # # music in the pc
        self.cacheFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
