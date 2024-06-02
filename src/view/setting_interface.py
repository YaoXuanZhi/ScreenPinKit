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
from .toolbar_interface import ToolbarSettingCard

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

        # toolbar
        self.toolbarGroup = SettingCardGroup(self.tr("Toolbar"), self.scrollWidget)
        self.toolbarListCard = ToolbarSettingCard(
            FIF.SETTING,
            self.tr('Toolbar Perference'),
            self.tr('Font family'),
            parent=self.toolbarGroup
        )

        # windowShadowStyle
        self.windowShadowStyleGroup = SettingCardGroup(self.tr("WindowShadowStyle"), self.scrollWidget)
        self.windowShadowStyleFocusColorCard = ColorSettingCard(
            cfg.windowShadowStyleFocusColor,
            FIF.PALETTE,
            self.tr("Focus color"),
            parent=self.windowShadowStyleGroup,
        )
        self.windowShadowStyleUnfocusColorCard = ColorSettingCard(
            cfg.windowShadowStyleUnFocusColor,
            FIF.PALETTE,
            self.tr("Unfocus color"),
            parent=self.windowShadowStyleGroup,
        )
        self.windowShadowStyleUseRoundStyleCard = SwitchSettingCard(
            FIF.VOLUME,
            self.tr('Use round style'),
            None,
            configItem=cfg.windowShadowStyleUseRoundStyle,
            parent=self.windowShadowStyleGroup
        )
        self.windowShadowStyleIsSaveWithShadowCard = SwitchSettingCard(
            FIF.FEEDBACK,
            self.tr('Save screenshot with shadow'),
            None,
            configItem=cfg.windowShadowStyleIsSaveWithShadow,
            parent=self.windowShadowStyleGroup
        )
        self.windowShadowStyleisCopyWithShadowCard = SwitchSettingCard(
            FIF.CHECKBOX,
            self.tr('Copy screenshot with shadow'),
            None,
            configItem=cfg.windowShadowStyleIsCopyWithShadow,
            parent=self.windowShadowStyleGroup
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

        self.toolbarGroup.addSettingCard(self.toolbarListCard)

        self.windowShadowStyleGroup.addSettingCard(self.windowShadowStyleFocusColorCard)
        self.windowShadowStyleGroup.addSettingCard(self.windowShadowStyleUnfocusColorCard)
        self.windowShadowStyleGroup.addSettingCard(self.windowShadowStyleUseRoundStyleCard)
        self.windowShadowStyleGroup.addSettingCard(self.windowShadowStyleIsSaveWithShadowCard)
        self.windowShadowStyleGroup.addSettingCard(self.windowShadowStyleisCopyWithShadowCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.generalGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.windowShadowStyleGroup)
        self.expandLayout.addWidget(self.toolbarGroup)
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

        # general
        self.cacheFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))