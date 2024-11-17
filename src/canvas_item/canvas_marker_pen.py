# coding=utf-8
from .canvas_line_strip_item import CanvasLineStripItem
from .canvas_util import *


class CanvasMarkerPen(CanvasLineStripItem):
    """
    绘图工具-记号笔
    @note 滚轮可以控制笔触大小
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initEditMode()

    def __initEditMode(self):
        """仅保Roi操作点"""
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(
            CanvasCommonPathItem.HitTestMode, False
        )  # 如果想要显示当前HitTest区域，注释这行代码即可

    def type(self) -> int:
        return EnumCanvasItemType.CanvasMarkerPen.value
