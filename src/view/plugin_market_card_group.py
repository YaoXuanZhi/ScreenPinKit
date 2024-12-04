# coding=utf-8
import os, random, time
from extend_widgets import *
from plugin import *

class LineEdit(SearchLineEdit):
    """ Search line edit """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(self.tr('Search plugins'))
        self.setFixedWidth(304)
        self.textChanged.connect(self.search)

class StatisticsWidget(QWidget):
    """ Statistics widget """

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)

        self.valueLabel = BodyLabel(value, self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignBottom)

        setFont(self.valueLabel, 18, QFont.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

class ItemCard(ElevatedCardWidget):
    """ App information card """

    def __init__(self, icon: FluentIcon, parent=None):
        super().__init__(parent)
        self.setFixedSize(304, 160)
        self.itemState = EnumItemCardState.NoneState
        self.iconWidget = TransparentToolButton(icon, self)
        self.iconWidget.setIconSize(QSize(64, 64))

        self.nameLabel = TitleLabel('PluginTemplate', self)
        setFont(self.nameLabel, 14, QFont.Bold)
        self.versionLabel = QLabel("v1.0.0")
        setFont(self.versionLabel, 14)
        self.companyLabel = HyperlinkLabel(
            QUrl('http://interwovencode.xyz/'), 'InterwovenCode Inc.', self)

        self.descriptionLabel = BodyLabel(
            'This is a plugin template for developing plugins.', self)
        setFont(self.descriptionLabel, 12)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('Component', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.contentLayout = QVBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.optionSliderLayout = QHBoxLayout()

        self.initLayout()

    def initLayout(self):
        self.contentLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)

        iconLayout = QVBoxLayout()
        self.topLayout.addLayout(iconLayout)
        iconLayout.addWidget(self.iconWidget)
        iconLayout.addWidget(self.tagButton)

        pluginBaseLayout = QVBoxLayout()
        self.topLayout.addLayout(pluginBaseLayout)
        pluginBaseLayout.addWidget(self.nameLabel)
        pluginBaseLayout.addWidget(self.versionLabel)
        pluginBaseLayout.addWidget(self.companyLabel)

        pluginBaseLayout.addLayout(self.optionSliderLayout)
        self.contentLayout.addWidget(self.descriptionLabel)

    def setInstalledUI(self):
        if hasattr(self, 'downloadButton'):
            self.downloadButton.deleteLater()

        self.switchButton = SwitchButton(self.tr('关闭'))
        self.deleteButton = TransparentToolButton(FluentIcon.DELETE)

        self.optionSliderLayout.addWidget(self.switchButton)
        self.optionSliderLayout.addWidget(self.deleteButton, 0, Qt.AlignRight)

        self.deleteButton.clicked.connect(self.onDeleteButtonClicked)
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)

        self.switchButton.setChecked(True)
        self.setItemState(EnumItemCardState.ActiveState)

    def setUnInstalledUI(self):
        if hasattr(self, 'deleteButton'):
            self.deleteButton.deleteLater()
        if hasattr(self,'switchButton'):
            self.switchButton.deleteLater()

        self.downloadButton = TransparentToolButton(FluentIcon.DOWNLOAD)
        self.downloadButton.clicked.connect(self.onDownloadButtonClicked)
        self.optionSliderLayout.addWidget(self.downloadButton, 0, Qt.AlignRight)
        self.setItemState(EnumItemCardState.UninstallState)

    def bindConfigItem(self, configItem: PluginConfigItemEx):
        self.configItem = configItem
        self.configItem.valueChanged.connect(pluginMgr.reloadPlugins)

        lastItemState:EnumItemCardState = pluginCfg.get(self.configItem)
        if lastItemState == EnumItemCardState.UninstallState:
            self.setUnInstalledUI()
        elif lastItemState == EnumItemCardState.ActiveState:
            self.setInstalledUI()
        elif lastItemState == EnumItemCardState.DeActiveState:
            self.setInstalledUI()
            self.switchButton.setChecked(False)

    def onDeleteButtonClicked(self):
        self.setUnInstalledUI()

    def onDownloadButtonClicked(self):
        self.setInstalledUI()

    def setItemState(self, newState: EnumItemCardState):
        if self.itemState == newState:
            return

        self.itemState = newState
        pluginCfg.set(self.configItem, newState)

    @property
    def tagName(self) -> str:
        return self.tagButton.text()

    @tagName.setter
    def tagName(self, value:str):
        self.tagButton.setText(value)

    @property
    def url(self) -> str:
        return self.companyLabel.url.toString()

    @url.setter
    def url(self, value:str):
        self.companyLabel.setUrl(value)

    @property
    def title(self) -> str:
        return self.nameLabel.text()

    @title.setter
    def title(self, value:str):
        self.nameLabel.setText(value)

    @property
    def version(self) -> str:
        return self.versionLabel.text()

    @version.setter
    def version(self, value:str):
        self.versionLabel.setText(value)

    @property
    def description(self) -> str:
        return self.descriptionLabel.text()

    @description.setter
    def description(self, value:str):
        self.descriptionLabel.setText(value)

    @property
    def author(self) -> str:
        return self.companyLabel.text()

    @author.setter
    def author(self, value:str):
        self.companyLabel.setText(value)

    @property
    def icon(self) -> QIcon:
        return self.iconWidget.icon

    @icon.setter
    def icon(self, icon:QIcon):
        self.iconWidget.setIcon(icon)

    def onSwitchCheckedChanged(self, isChecked):
        if isChecked:
            self.switchButton.setText(self.tr('开启'))
        else:
            self.switchButton.setText(self.tr('关闭'))

        if isChecked:
            self.setItemState(EnumItemCardState.ActiveState)
        else:
            self.setItemState(EnumItemCardState.DeActiveState)

class ItemCardView(QWidget):
    """ Item card view """
    searchedSignal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("background-color: transparent;")
        self.trie = Trie()
        self.searchLineEdit = LineEdit(self)

        self.view = QFrame(self)
        self.scrollArea = SmoothScrollArea(self.view)
        self.scrollWidget = QWidget(self.scrollArea)

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self.view)
        self.flowLayout = FlowLayout(self.scrollWidget, isTight=True)
        self.fuzzyMatch = FuzzyMatch()

        self.cards = []     # type:List[ItemCard]
        self.icons = []
        self.currentIndex = -1
        self.options = []

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setViewportMargins(0, 0, 0, 0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.searchLineEdit)
        self.vBoxLayout.addWidget(self.view)

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.scrollArea)

        self.flowLayout.setVerticalSpacing(8)
        self.flowLayout.setHorizontalSpacing(8)
        self.flowLayout.setContentsMargins(0, 3, 0, 0)

        self.searchLineEdit.clearSignal.connect(self.showAllPlugins)
        self.searchLineEdit.searchSignal.connect(self.search)

        self.initUI()

    def initUI(self):
        for plugin in pluginMgr.plugins:
            self.addPlugin(plugin)

    def addPlugin(self, plugin: PluginInterface):
        """ add plugin to view """
        pluginName = plugin.name
        icon = plugin.icon
        if not hasattr(pluginCfg, pluginName):
            configItem = PluginConfigItemEx(
                pluginName, "pluginState", 
                EnumItemCardState.UninstallState, 
            )

            setattr(pluginCfg, pluginName, configItem)
        else:
            configItem = getattr(pluginCfg, pluginName)

        card = ItemCard(icon, self)
        card.bindConfigItem(configItem)
        card.title = plugin.displayName
        card.version = plugin.version
        card.author = plugin.author
        card.description = plugin.desc
        card.url = plugin.url
        # card.tagName = plugin.tags[0]
        card.tagName = "内置库"

        self.trie.insert(pluginName, len(self.cards))
        self.fuzzyMatch.insertItem(pluginName + plugin.displayName + plugin.desc)
        self.cards.append(card)
        self.icons.append(icon)
        self.options.append(pluginName)
        self.flowLayout.addWidget(card)

    def search(self, keyWord: str):
        """ search icons """

        isSkip = True
        if not hasattr(self, "lastIndexes"):
            self.lastIndexes = {}

        indexes = self.fuzzyMatch.bestMatch(keyWord)
        if indexes != self.lastIndexes:
            isSkip = False

        self.lastIndexes = indexes

        if isSkip:
            return

        self.flowLayout.removeAllWidgets()

        for i, card in enumerate(self.cards):
            isVisible = i in indexes
            if isVisible:
                card.show()
            else:
                card.hide()
            if isVisible:
                self.flowLayout.addWidget(card)

        self.update()

    def showAllPlugins(self):
        self.flowLayout.removeAllWidgets()
        for card in self.cards:
            card.show()
            self.flowLayout.addWidget(card)

class MarketSettingCard(ScrollArea):
    """Toolbar card with a push button"""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.interface = ItemCardView(self)

        self.resize(400, 400)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.interface)

class PluginMarketCardGroup(SettingCardGroup):
    """Setting card group"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)
        self.marketCard = MarketSettingCard(self)
        self.addSettingCard(self.marketCard)