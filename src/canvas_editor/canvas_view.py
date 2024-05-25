from PyQt5 import QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from canvas_item.canvas_util import *

class CanvasView(QGraphicsView):
    '''
    注意，不应该对Scene进行缩放，否则你的橡皮擦实现需要改变思路，
    通过新建一个橡皮层来实现，因为一旦缩放之后，Sene同背景就会不匹配了
    '''
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

        # self.zoomComponent = ZoomComponent()
        # self.zoomComponent.zoomClamp = True
        # self.zoomComponent.signal.connect(self.zoomHandle)

    # def zoomHandle(self, zoomFactor):
    #     self.scale(zoomFactor, zoomFactor)

    def initUI(self):
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scene_width, self.scene_height = self.frameSize().width(), self.frameSize().height()
        self.setSceneRect(0, 0, self.scene_width, self.scene_height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border:0px;")
        self.setRenderHint(QPainter.Antialiasing)

    def isCanDrag(self):
        '''判断当前是否可以拖曳图元'''
        matchMode = self.dragMode()
        return (matchMode | QGraphicsView.RubberBandDrag == matchMode)

    def switchCanvas(self):
        if self.isCanDrag():
            self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event: QWheelEvent):
        pathItem = None
        if hasattr(self.scene(), "pathItem"):
            pathItem = self.scene().pathItem
        # 如果有选中了某个图元，则滚动事件会正常往下分发
        if len(self.scene().selectedItems()) < 1 and pathItem == None:
            # self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        return super().wheelEvent(event)