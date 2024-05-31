# coding:utf-8
from enum import Enum
from canvas_item import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, ConfigValidator, FolderValidator, ConfigSerializer)

class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    # CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
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
    imageNameFormat = ConfigItem(
        "General", "ImageNameFormat", "ScreenPinKit_{0}.png", ConfigValidator())

    # HotKey
    screenShotHotKey = ConfigItem(
        "HotKey", "ScreenShot", "", ConfigValidator())
    screenPaintHotKey = ConfigItem(
        "HotKey", "ScreenPaint", "", ConfigValidator())
    mouseThoughHotKey = ConfigItem(
        "HotKey", "MouseThough", "", ConfigValidator())
    showClipboardHotKey = ConfigItem(
        "HotKey", "ShowClipboard", "", ConfigValidator())
    switchScreenPaintModeHotKey = ConfigItem(
        "HotKey", "SwitchScreenPaintMode", "", ConfigValidator())

    # Software Update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())

    # Toolbar
    toolbarUseWheelZoom = ConfigItem(
        "Toolbar", "useWheelZoom", True, BoolValidator())
    toolbarApplyWheelItem = ConfigItem(
        "Toolbar", "applyWheelItem", True, BoolValidator())

    # ShadowStyle
    focusShadowColor = ColorConfigItem("ShadowStyle", "focusColor", "#225C7F")
    unFocusShadowColor = ColorConfigItem("ShadowStyle", "unFocusColor", "#7d7d7d")
    useRoundStyle = ConfigItem(
        "ShadowStyle", "useRoundStyle", False, BoolValidator())
    isSaveWithShadow = ConfigItem(
        "ShadowStyle", "isSaveWithShadow", False, BoolValidator())
    isCopyWithShadow = ConfigItem(
        "ShadowStyle", "isCopyWithShadow", False, BoolValidator())

    # TextEditToolbar
    textEditToolbarFontFamily = ConfigItem(
        "TextEditToolbar", "fontFamily", "Microsoft YaHei")
    textEditToolbarFontSize = RangeConfigItem(
        "TextEditToolbar", "fontSize", 5, RangeValidator(1, 100))
    textEditToolbarTextColor = ColorConfigItem(
        "TextEditToolbar", "textColor", Qt.red)

    # EffectToolbar
    effectToolbarStrength = RangeConfigItem(
        "EffectToolbar", "strength", 5, RangeValidator(1, 15))
    effectToolbarEffectType = OptionsConfigItem(
        "EffectToolbar", "effectType", AfterEffectType.Blur, OptionsValidator(AfterEffectType), EnumSerializer(AfterEffectType))

    # EraseToolbar
    eraseToolbarWidth = RangeConfigItem(
        "EraseToolbar", "width", 5, RangeValidator(1, 30))

YEAR = 2023
AUTHOR = "YaoXuanZhi"
APP_NAME = "ScreenPinKit"
VERSION = "0.5"
HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io"
FEEDBACK_URL = "https://github.com/YaoXuanZhi/ScreenPinKit/issues"
RELEASE_URL = "https://github.com/YaoXuanZhi/ScreenPinKit/releases/latest"

cfg = Config()
qconfig.load('config/config.json', cfg)