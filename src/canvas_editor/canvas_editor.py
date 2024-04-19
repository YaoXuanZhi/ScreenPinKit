from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from canvas_item.canvas_util import CanvasROIManager
from .canvas_scene import CanvasScene, DrawActionEnum
from .canvas_view import CanvasView

class CanvasEditor(QWidget):
    """ Canvas编辑层 """
    def __init__(self, parent=None, sceneBrush:QBrush = None):
        super().__init__(parent)
        self.sceneBrush = sceneBrush
        self.defaultFlag()

    def defaultFlag(self):
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scene = CanvasScene(None, self.sceneBrush)
        # self.scene.setBackgroundBrush(self.sceneBrush)

        self.view = CanvasView(self.scene)
        self.layout.addWidget(self.view)

    def quitDraw(self):
        self.view.setEnabled(False)
        for item in self.view.scene().items():
            if hasattr(item, "roiMgr"):
                roiMgr:CanvasROIManager = item.roiMgr
                roiMgr.setShowState(False)

            item.setSelected(False)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum):
        self.scene.currentDrawActionEnum = drawActionEnum
        self.scene.pathItem = None
        self.view.setEnabled(drawActionEnum != DrawActionEnum.DrawNone)

    def isAllowDrag(self):
        return not self.view.isEnabled()