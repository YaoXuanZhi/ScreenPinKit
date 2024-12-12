# coding=utf-8
from common import cfg
from extend_widgets import *


class KeySequenceEditCard(SettingCard):
    def __init__(self, actionName: str, configItem: ConfigItem = None, parent=None):
        """
        Parameters
        ----------
        actionName: str
            the text of push button

        keySequenceStr: str
            the key sequence of card

        parent: QWidget
            parent widget
        """
        super().__init__(QIcon(), actionName, None, parent)
        self.configItem = configItem
        defaultValue = ""
        if configItem:
            defaultValue = qconfig.get(configItem)
        self.keySequenceEdit = KeySequenceEditPlus(defaultValue)
        self.hBoxLayout.addWidget(self.keySequenceEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.keySequenceEdit.keySequenceEdit.keySequenceChanged.connect(
            self.__onKeySequenceChanged
        )

    def __onKeySequenceChanged(self, keySequence: QKeySequence):
        self.setValue(keySequence.toString().lower())

    def setValue(self, keySequenceStr: str):
        qconfig.set(self.configItem, keySequenceStr)
        self.keySequenceEdit.keySequenceEdit.setKeySequence(keySequenceStr)


class HotkeySettingCardGroup(SettingCardGroup):
    """Setting card group"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent)

        self.hotkeyScreenShotCard = KeySequenceEditCard(
            self.tr("Screen shot"), cfg.hotKeyScreenShot, parent=self
        )
        self.hotkeyRepeatScreenShotCard = KeySequenceEditCard(
            self.tr("Repeat Screen shot"), cfg.hotKeyRepeatScreenShot, parent=self
        )
        self.hotkeyShowClipboardCard = KeySequenceEditCard(
            self.tr("Show clipboard"), cfg.hotKeyShowClipboard, parent=self
        )
        self.hotkeyScreenPaintCard = KeySequenceEditCard(
            self.tr("Screen paint"), cfg.hotKeyScreenPaint, parent=self
        )
        self.hotkeySwitchScreenPaintModeCard = KeySequenceEditCard(
            self.tr("Switch screen paint mode"),
            cfg.hotKeySwitchScreenPaintMode,
            parent=self,
        )
        self.hotkeyToggleMouseClickThroughCard = KeySequenceEditCard(
            self.tr("Toggle mouse click-through"),
            cfg.hotKeyToggleMouseClickThrough,
            parent=self,
        )

        self.__initLayout()

    def __initLayout(self):
        self.addSettingCard(self.hotkeyScreenShotCard)
        self.addSettingCard(self.hotkeyRepeatScreenShotCard)
        self.addSettingCard(self.hotkeyShowClipboardCard)
        self.addSettingCard(self.hotkeyScreenPaintCard)
        self.addSettingCard(self.hotkeySwitchScreenPaintModeCard)
        self.addSettingCard(self.hotkeyToggleMouseClickThroughCard)
