# coding:utf-8
from enum import Enum

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QGuiApplication, QFont
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, ConfigValidator, FolderValidator, ConfigSerializer)

# class HotKeyValidator(ConfigValidator):
#     """ Options validator """

#     def __init__(self, options):
#         if not options:
#             raise ValueError("The `options` can't be empty.")

#         if isinstance(options, Enum):
#             options = options._member_map_.values()

#         self.options = list(options)

#     def validate(self, value):
#         return value in self.options

#     def correct(self, value):
#         return value if self.validate(value) else self.options[0]

class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # General
    dpiScale = OptionsConfigItem(
        "General", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "General", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    cacheFolder = ConfigItem(
        "General", "CacheFolder", "./cache", FolderValidator())

    # HotKey
    screenShotHotKey = ConfigItem(
        "HotKey", "ScreenShot", "", ConfigValidator())
    screenPaintHotKey = ConfigItem(
        "HotKey", "ScreenPaint", "", ConfigValidator())
    mouseThoughHotKey = ConfigItem(
        "HotKey", "MouseThough", "", ConfigValidator())
    showClipboardHotKey = ConfigItem(
        "HotKey", "ShowClipboard", "", ConfigValidator())

YEAR = 2023
AUTHOR = "YaoXuanZhi"
VERSION = "0.5"
HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"

cfg = Config()
qconfig.load('config/config.json', cfg)