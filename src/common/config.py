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
    hotKeyScreenShot = ConfigItem(
        "HotKey", "ScreenShot", "", ConfigValidator())
    hotKeyScreenPaint = ConfigItem(
        "HotKey", "ScreenPaint", "", ConfigValidator())
    hotKeyToggleMouseClickThrough = ConfigItem(
        "HotKey", "MouseThough", "", ConfigValidator())
    hotKeyShowClipboard = ConfigItem(
        "HotKey", "ShowClipboard", "", ConfigValidator())
    hotKeySwitchScreenPaintMode = ConfigItem(
        "HotKey", "SwitchScreenPaintMode", "", ConfigValidator())

    # Software Update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())

    # Toolbar
    toolbarUseWheelZoom = ConfigItem(
        "Toolbar", "useWheelZoom", True, BoolValidator())
    toolbarApplyWheelItem = ConfigItem(
        "Toolbar", "applyWheelItem", True, BoolValidator())

    # WindowShadowStyle
    windowShadowStyleFocusColor = ColorConfigItem(
        "WindowShadowStyle", "focusColor", Qt.GlobalColor.blue)
    windowShadowStyleUnFocusColor = ColorConfigItem(
        "WindowShadowStyle", "unFocusColor", Qt.GlobalColor.gray)
    windowShadowStyleUseRoundStyle = ConfigItem(
        "WindowShadowStyle", "useRoundStyle", False, BoolValidator())
    windowShadowStyleIsSaveWithShadow = ConfigItem(
        "WindowShadowStyle", "isSaveWithShadow", False, BoolValidator())
    windowShadowStyleIsCopyWithShadow = ConfigItem(
        "WindowShadowStyle", "isCopyWithShadow", False, BoolValidator())

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

    # ShapeToolbar
    shapeToolbarPenWidth = RangeConfigItem(
        "ShapeToolbar", "penWidth", 2, RangeValidator(1, 30))
    shapeToolbarBrushColor = ColorConfigItem(
        "ShapeToolbar", "brushColor", Qt.GlobalColor.blue)
    shapeToolbarPenColor = ColorConfigItem(
        "ShapeToolbar", "penColor", Qt.GlobalColor.gray)
    shapeToolbarPenStyle = OptionsConfigItem(
        "ShapeToolbar", "penStyle", Qt.PenStyle.SolidLine, OptionsValidator([Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine]))
    shapeToolbarShape = OptionsConfigItem(
        "ShapeToolbar", "shape", CanvasShapeEnum.Rectangle, OptionsValidator(CanvasShapeEnum), EnumSerializer(CanvasShapeEnum))

    # ArrowToolbar
    arrowToolbarPenWidth = RangeConfigItem(
        "ArrowToolbar", "penWidth", 2, RangeValidator(1, 30))
    arrowToolbarBrushColor = ColorConfigItem(
        "ArrowToolbar", "brushColor", Qt.GlobalColor.blue)
    arrowToolbarPenColor = ColorConfigItem(
        "ArrowToolbar", "penColor", Qt.GlobalColor.gray)
    arrowToolbarPenStyle = OptionsConfigItem(
        "ArrowToolbar", "penStyle", Qt.PenStyle.SolidLine, OptionsValidator([Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine]))

    # LineStripToolbar
    lineStripToolbarPenWidth = RangeConfigItem(
        "LineStripToolbar", "penWidth", 5, RangeValidator(1, 30))
    lineStripToolbarPenColor = ColorConfigItem(
        "LineStripToolbar", "penColor", Qt.GlobalColor.red)

    # MarkerPenToolbar
    markerPenToolbarPenWidth = RangeConfigItem(
        "MarkerPenToolbar", "penWidth", 5, RangeValidator(1, 30))
    markerPenToolbarPenColor = ColorConfigItem(
        "MarkerPenToolbar", "penColor", Qt.GlobalColor.red)

    # PenToolbar
    penToolbarPenWidth = RangeConfigItem(
        "PenToolbar", "penWidth", 5, RangeValidator(1, 30))
    penToolbarPenColor = ColorConfigItem(
        "PenToolbar", "penColor", Qt.GlobalColor.red)

    # NumberMarkerItemToolbar
    numberMarkerItemToolbarFontFamily = ConfigItem(
        "NumberMarkerItemToolbar", "fontFamily", "Microsoft YaHei")
    numberMarkerItemToolbarTextColor = ColorConfigItem(
        "NumberMarkerItemToolbar", "textColor", Qt.GlobalColor.white)
    numberMarkerItemToolbarPenWidth = RangeConfigItem(
        "NumberMarkerItemToolbar", "penWidth", 2, RangeValidator(1, 30))
    numberMarkerItemToolbarPenColor = ColorConfigItem(
        "NumberMarkerItemToolbar", "penColor", Qt.GlobalColor.gray)
    numberMarkerItemToolbarPenStyle = OptionsConfigItem(
        "NumberMarkerItemToolbar", "penStyle", Qt.PenStyle.SolidLine, OptionsValidator([Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine]))

    @property
    def numberMarkerItemToolbarFont(self):
        font = QFont(self.numberMarkerItemToolbarFontFamily.value)
        return font

    @numberMarkerItemToolbarFont.setter
    def numberMarkerItemToolbarFont(self, font: QFont):
        self.numberMarkerItemToolbarFontFamily.value = font.family()
        self.save()

    @property
    def textEditToolbarFont(self):
        font = QFont(self.textEditToolbarFontFamily.value)
        return font

    @textEditToolbarFont.setter
    def textEditToolbarFont(self, font: QFont):
        self.textEditToolbarFontFamily.value = font.family()
        self.save()

YEAR = 2023
AUTHOR = "YaoXuanZhi"
APP_NAME = "ScreenPinKit"
VERSION = "0.5"
HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io"
FEEDBACK_URL = "https://github.com/YaoXuanZhi/ScreenPinKit/issues"
RELEASE_URL = "https://github.com/YaoXuanZhi/ScreenPinKit/releases/latest"

cfg = Config()
qconfig.load('config/config.json', cfg)