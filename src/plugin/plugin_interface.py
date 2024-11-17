import os, inspect
from abc import ABC, abstractmethod
from enum import Enum


class GlobalEventEnum(Enum):
    OcrStartEvent = 1
    """OCR开始事件"""
    OcrEndSuccessEvent = 2
    """OCR结束事件"""
    OcrEndFailEvent = 3
    """OCR失败事件"""

    ImageCopyingEvent = 4
    """图片复制中事件"""
    ImageSavingEvent = 5
    """图片保存中事件"""

    RegisterContextMenuEvent = 6
    """注册右键弹出菜单事件"""

    RegisterToolbarMenuEvent = 7
    """注册工具栏菜单事件"""

    GlobalHotKeyRegisterStart = 13
    """全局热键开始注册"""
    GlobalHotKeyRegisterEnd = 14
    """全局热键结束注册"""


class PluginInterface(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def desc(self):
        pass

    def onLoaded(self):
        pass

    def handleEvent(self, eventName: GlobalEventEnum, *args, **kwargs):
        # self.log(f"[{self.name}]：{eventName} ==> {args} {kwargs}")
        pass

    def log(self, message):
        frame = inspect.currentframe().f_back
        evalFilename = frame.f_code.co_filename
        evalLineNumber = frame.f_lineno
        final = f"""<----------{self.name}|{evalFilename}:{evalLineNumber}---------->
{message}"""
        print(final)
