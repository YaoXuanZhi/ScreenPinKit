# coding=utf-8
from typing import Union
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from canvas_item.canvas_util import *

class ComboBoxSettingCardPlus(SettingCard):
    """ Setting card with a combo box """

    def __init__(self, configItem: OptionsConfigItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, options=None, parent=None):
        """
        Parameters
        ----------
        configItem: OptionsConfigItem
            configuration item operated by the card

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        options: List[tuple:(text, enum)]
            the text of items

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.comboBox = ComboBox(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        for text, enum in options:
            self.comboBox.addItem(text=text, userData=enum)

        currentIndex = 0
        matchValue = qconfig.get(configItem)
        for text, enum in options:
            if matchValue == enum:
                break
            currentIndex = currentIndex + 1 
        self.comboBox.setCurrentIndex(currentIndex)

        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def _onCurrentIndexChanged(self, index: int):
        qconfig.set(self.configItem, self.comboBox.itemData(index))