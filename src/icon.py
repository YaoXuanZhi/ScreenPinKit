# coding: utf-8
from enum import Enum

from qfluentwidgets import FluentIconBase, getIconColor, Theme


class ScreenShotIcon(FluentIconBase, Enum):
    LOGO = "截图"
    QUIT = "取消"
    SETTING = "设置"
    WHITE_BOARD = "whiteboard"
    COPY = "复制"
    TEXT_FRAME = "文本框"
    TEXT = "文本"
    ERASE = "橡皮"
    PENCIL = "铅笔"
    PEN = "圆珠笔"
    UNDO = "撤销"
    REDO = "恢复"
    SAVE = "保存"
    SAVE_AS = "另存为"
    FINISHED = "完成"
    DELETE_ALL = "delete-all"
    IMGAGE_EDITOR = "编辑图像"
    TRASH = "回收站"
    BRUSH = "刷"
    UNDO2 = "左2"
    REDO2 = "右2"
    OCR = "通用ocr"
    GUIDE = "翻开的书"
    CLICK_THROUGH = "进入地理围栏"

    ARROW = "箭头"
    MARKER_PEN = "记号笔"
    STAR = "星"
    RECTANGLE = "方形边框"
    POLYGONAL_LINE = "折线"
    POLYGON = "多边形"

    def path(self, theme=Theme.AUTO):
        # return f"resource/icons/{self.value}_{getIconColor(theme)}.svg"
        return f"resource/icons/icons8-{self.value}-64.png"

# QIcon(ScreenShotIcon.path(ScreenShotIcon.LOGO))