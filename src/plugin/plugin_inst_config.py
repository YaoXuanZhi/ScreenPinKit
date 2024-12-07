from PyQt5.QtGui import QIcon
from .plugin_interface import PluginInterface, GlobalEventEnum

class PluginInstConfig(PluginInterface):
    def __init__(self):
        super().__init__()
        self._name = "test"
        self._displayName = ""
        self._desc = ""
        self._author = ""
        self._icon = QIcon()
        self._version = ""
        self._url = ""
        self._tags = []
        self._previewImages = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def displayName(self):
        return self._displayName

    @displayName.setter
    def displayName(self, value):
        self._displayName = value

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def tags(self) -> list:
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def previewImages(self) -> list:
        return self._previewImages

    @previewImages.setter
    def previewImages(self, value):
        self._previewImages = value