import os, random
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from canvas_item import *

class DrawActionEnum(Enum):
    DrawNone = "无操作"
    EditText = "编辑文字"
    UsePencil = "使用画笔"
    UseEraser = "使用橡皮擦"
    UseEraserRectItem = "使用橡皮框"
    UseMarkerPen = "使用记号笔"
    UseMarkerItem = "使用标记"
    PasteSvg = "粘贴图案"

    DrawDiversity = "绘制多边形"
    DrawRectangle = "绘制矩形"
    DrawEllipse = "绘制椭圆"
    DrawArrow = "绘制箭头"
    DrawStar = "绘制五角星"
    DrawPolygonalLine = "绘制折线"
    SelectItem = "选择对象"
    Mosaic = "马赛克工具"
    Blur = "模糊工具"

class SceneUserNotifyEnum(Enum):
    StartDrawedEvent = "已开始绘制"
    EndDrawedEvent = "已结束绘制"
    SelectItemChangedEvent = "选中图元已改变"
    SelectNothing = "啥也没选中"

class CanvasScene(QGraphicsScene):
    itemMovedSignal = pyqtSignal(QGraphicsItem, QPointF, QPointF)
    itemDeleteSignal = pyqtSignal(QGraphicsScene, QGraphicsItem)
    itemAddSignal = pyqtSignal(QGraphicsScene, QGraphicsItem)
    itemRotatedSignal = pyqtSignal(QGraphicsItem, float, float)
    itemResizedSignal = pyqtSignal(QGraphicsItem, tuple, tuple)

    def __init__(self, parent=None, backgroundBrush:QBrush = None):
        super().__init__(parent)
        self._currentDrawActionEnum = DrawActionEnum.DrawNone
        self._isLockedTool = True

        self.pathItem = None
        self.lastAddItem = None
        self.bgBrush = backgroundBrush

        self.itemList:list = []
        self._itemNotifyCallBack = None
        self._lastSelectedItem = None

        self.selectionChanged.connect(self.selectionChangedHandler)
        # self.setBackgroundBrush(self.bgBrush)

        # self.blurMgr = BlurManager()
        # self.blurMgr.saveBlurPixmap(self.bgBrush.texture().copy())

    def selectionChangedHandler(self):
        selectItem = None
        if len(self.selectedItems()) > 0:
            if hasattr(self.selectedItems()[0], "completeDraw"):
                selectItem = self.selectedItems()[0]
            else:
                return
        if self._itemNotifyCallBack != None:
            if self.currentDrawActionEnum == DrawActionEnum.SelectItem and selectItem == None:
                self._itemNotifyCallBack(SceneUserNotifyEnum.SelectNothing, selectItem)
            else:
                self._itemNotifyCallBack(SceneUserNotifyEnum.SelectItemChangedEvent, selectItem)
        self._lastSelectedItem = selectItem

    def initNodes(self):
        targetRect = QRectF(QPointF(0, 0), QSizeF(100, 100))
        arrowStyleMap = {
            "arrowLength" : 32.0,
            "arrowAngle" : 0.5,
            "arrowBodyLength" : 18,
            "arrowBodyAngle" : 0.2,

            "arrowBrush" : QBrush(QColor(255, 0, 0, 100)),
            "arrowPen" : QPen(QColor(255, 0, 0), 2, Qt.SolidLine),
        }
        # finalPoints = CanvasUtil.buildArrowPath(QPainterPath(), QPolygonF([targetRect.topLeft(), targetRect.bottomRight()]), arrowStyleMap)
        finalPoints = CanvasUtil.buildStarPath(QPainterPath(), QPolygonF([targetRect.topLeft(), targetRect.bottomRight()]))
        pathItem1 = CanvasCommonPathItem(None, False)
        pathItem1.polygon = QPolygonF(finalPoints)
        pathItem1.completeDraw()
        self.__startDraw(pathItem1)

        pathItem2 = CanvasCommonPathItem(None, True)
        pathItem2.polygon = QPolygonF(finalPoints)
        pathItem2.completeDraw()
        pathItem2.moveBy(300, 0)
        self.__startDraw(pathItem2)

        pathItem3 = CanvasEditablePath(None, False)
        pathItem3.addPoint(QPointF(-100, -100), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-30, -50), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-200, -280), Qt.SizeAllCursor)
        pathItem3.update()
        self.__startDraw(pathItem3)

    def setNofityEvent(self, callBack:callable = None):
        self._itemNotifyCallBack = callBack

    @property
    def currentDrawActionEnum(self): return self._currentDrawActionEnum
    @currentDrawActionEnum.setter
    def currentDrawActionEnum(self, value): 
        if self._currentDrawActionEnum == value:
            return
        self._currentDrawActionEnum = value
        self.setEditableState(value == DrawActionEnum.SelectItem)

    @property
    def isLockedTool(self): return self._isLockedTool
    @isLockedTool.setter
    def isLockedTool(self, value): 
        self._isLockedTool = value

    def __startDraw(self, item:QGraphicsObject):
        if self.lastAddItem != None:
            self.lastAddItem.setEditableState(False)
        self.addItem(item)
        if self._itemNotifyCallBack != None:
            self._itemNotifyCallBack(SceneUserNotifyEnum.StartDrawedEvent, item)

    def forceCompleteDraw(self):
        if self.pathItem != None:
            isOk = True
            # 由于线段控件强制退出时，需要回收一个预览操作点，需要额外处理
            if isinstance(self.pathItem, CanvasPolygonItem):
                if self.pathItem.polygon.count() > 2:
                    self.pathItem.polygon.remove(self.pathItem.polygon.count() - 1)
                else:
                    isOk = False
            self.__completeDraw(self.pathItem, isOk)
        self.lastAddItem = None

    def __completeDraw(self, item:CanvasCommonPathItem, isOk:bool = True):
        if isOk:
            item.completeDraw()
            # self.itemList.append(item)
            self.itemAddSignal.emit(self, item)
            self.lastAddItem = item
            # self.saveAfterEffectPixmap()
            item.setEditableState(True)
            # if not self.isLockedTool:
            #     item.setFocus(Qt.FocusReason.OtherFocusReason)

        if not isOk:
            self.removeItem(item)
            if self.lastAddItem != None:
                self.lastAddItem.setEditableState(True)

        self.pathItem = None

        if self._itemNotifyCallBack != None:
            if isOk:
                self._itemNotifyCallBack(SceneUserNotifyEnum.EndDrawedEvent, item)
            else:
                self._itemNotifyCallBack(SceneUserNotifyEnum.EndDrawedEvent, None)

        if isOk and hasattr(item, "transformComponent"):
            item.transformComponent.movedSignal.connect(self.itemMovedSignal)
            item.transformComponent.rotatedSignal.connect(self.itemRotatedSignal)
            item.transformComponent.resizedSignal.connect(self.itemResizedSignal)

    def clearDraw(self):
        self.clear()
        self.pathItem = None
        self.lastAddItem = None
        self.itemList = []

    def canUndo(self):
        return self.pathItem == None

    def saveAfterEffectPixmap(self):
        '''
        缓存机制：开启多线程缓存上次操作的快照后处理结果
        '''
        basePixmap = self.bgBrush.texture().copy()
        painter = QPainter()
        painter.begin(basePixmap)
        view = self.views()[0]
        painter.drawPixmap(view.geometry(), view.grab())
        painter.end()

        # self.blurMgr.saveBlurPixmap(basePixmap)

    def switchLockState(self):
        self.isLockedTool = not self.isLockedTool

    def setEditableState(self, isEditable:bool):
        for item0 in self.itemList:
            item:CanvasCommonPathItem = item0
            item.setEditableState(isEditable)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent):
        selectedItems = self.selectedItems()
        if len(selectedItems) > 0:
            selectItem = selectedItems[0]
            selectItem.wheelEvent(event)
            event.accept()
            return
        return super().wheelEvent(event)

    # 参考https://excalidraw.com/上面的操作方式
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        view:QGraphicsView = self.views()[0]
        targetPos = event.scenePos()
        item = self.itemAt(event.scenePos(), view.transform())

        # item = None
        # itemList = self.items(event.scenePos())
        # if len(itemList) > 0:
        #     item = itemList[0]

        isSkip = False
        if self.currentDrawActionEnum in [DrawActionEnum.DrawNone, DrawActionEnum.SelectItem]:
            isSkip = True
        if item == self.lastAddItem and item != None:
            isSkip = True
        if item != None and CanvasUtil.isRoiItem(item):
            isSkip = True
        if isinstance(item, CanvasTextItem) and item.isSelected():
            return super().mousePressEvent(event)

        if isSkip and not self.isLockedTool:
            return super().mousePressEvent(event)
        else:
            if event.button() == Qt.LeftButton:
                if self.pathItem == None:
                    if self.currentDrawActionEnum == DrawActionEnum.EditText:
                        self.pathItem = CanvasTextItem()
                        self.pathItem.switchEditableBox()
                        self.__startDraw(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                        self.__completeDraw(self.pathItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerItem:
                        self.pathItem = CanvasMarkerItem(QRectF(0, 0, 50, 50))
                        self.__startDraw(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                        self.__completeDraw(self.pathItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.PasteSvg:
                        folderPath = os.path.join(os.path.dirname(__file__), "../canvas_item/demos/resources")
                        def getSvgFiles(folderPath):
                            result = []
                            for filePath in os.listdir(folderPath):
                                if filePath.endswith(".svg"):
                                    result.append(os.path.join(folderPath, filePath))
                            return result
                        svgPaths = getSvgFiles(folderPath)
                        index = random.randint(0, len(svgPaths) - 1)
                        svgPath = svgPaths[index]
                        if index % 2 == 0:
                            self.pathItem = CanvasSvgItem(QRectF(), svgPath)
                        else:
                            self.pathItem = CanvasSvgItem(QRectF(0, 0, 100, 100), svgPath)

                        self.__startDraw(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                        self.__completeDraw(self.pathItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.UsePencil:
                        self.pathItem = CanvasPencilItem()
                        self.__startDraw(self.pathItem)
                        self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraser:
                        if self.pathItem == None:
                            if self.bgBrush != None:
                                eraseBrush = self.bgBrush
                                erasePen = QPen(eraseBrush, 10)
                            else:
                                erasePen = QPen(Qt.GlobalColor.blue)
                            self.pathItem = CanvasEraserItem(erasePen)
                            self.__startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraserRectItem:
                        if self.pathItem == None:
                            if self.bgBrush != None:
                                self.pathItem = CanvasEraserRectItem(self.bgBrush)
                                self.__startDraw(self.pathItem)
                                self.pathItem.polygon.append(targetPos)
                                self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.Blur:
                        if self.pathItem == None:
                            if self.bgBrush != None:
                                # blurPixmap = self.blurMgr.lastBlurPixmap.copy()
                                blurPixmap = None
                                sourcePixmap = self.bgBrush.texture().copy()
                                self.pathItem = CanvasBlurRectItem(sourcePixmap, blurPixmap, None)
                                self.__startDraw(self.pathItem)
                                self.pathItem.polygon.append(targetPos)
                                self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                        if self.pathItem == None:
                            self.pathItem = CanvasArrowItem()
                            self.__startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                        if self.pathItem == None:
                            self.pathItem = CanvasMarkerPen()
                            self.__startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum in [DrawActionEnum.DrawRectangle, DrawActionEnum.DrawEllipse, DrawActionEnum.DrawStar]:
                        if self.pathItem == None:
                            if self.currentDrawActionEnum == DrawActionEnum.DrawRectangle:
                                self.pathItem = CanvasClosedShapeItem(None, CanvasClosedShapeEnum.Rectangle)
                            elif self.currentDrawActionEnum == DrawActionEnum.DrawEllipse:
                                self.pathItem = CanvasClosedShapeItem(None, CanvasClosedShapeEnum.Ellipse)
                            elif self.currentDrawActionEnum == DrawActionEnum.DrawStar:
                                self.pathItem = CanvasClosedShapeItem(None, CanvasClosedShapeEnum.Star)
                            self.__startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)

                if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                    if self.pathItem == None:
                        self.pathItem = CanvasPolygonItem()
                        self.__startDraw(self.pathItem)
                        self.pathItem.polygon.append(targetPos)
                        self.pathItem.polygon.append(targetPos)
                    else:
                        self.pathItem.polygon.append(targetPos)
                        self.pathItem.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.currentDrawActionEnum in [DrawActionEnum.DrawNone, DrawActionEnum.SelectItem] and self.pathItem != None:
            targetPos = event.scenePos()

            if self.currentDrawActionEnum in [
                DrawActionEnum.DrawPolygonalLine, 
                DrawActionEnum.DrawArrow, 
                DrawActionEnum.UseMarkerPen, 
                DrawActionEnum.UseEraserRectItem, 
                DrawActionEnum.DrawRectangle, 
                DrawActionEnum.DrawEllipse, 
                DrawActionEnum.DrawStar,
                DrawActionEnum.Blur,
                ]:
                self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                self.pathItem.update()
            elif self.currentDrawActionEnum in [DrawActionEnum.UsePencil, DrawActionEnum.UseEraser]:
                self.pathItem.polygon.append(targetPos)
                self.pathItem.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone and self.pathItem != None:

            if self.currentDrawActionEnum in [DrawActionEnum.DrawPolygonalLine] and event.button() == Qt.RightButton:
                if event.button() == Qt.RightButton and self.pathItem != None:
                    isOk = False
                    if self.pathItem.polygon.count() > 2:
                        self.pathItem.polygon.remove(self.pathItem.polygon.count() - 1)
                        isOk = True
                    self.__completeDraw(self.pathItem, isOk)
            elif self.currentDrawActionEnum in [DrawActionEnum.UsePencil, DrawActionEnum.UseEraser]:
                if event.button() == Qt.LeftButton:
                    self.__completeDraw(self.pathItem)
            elif self.currentDrawActionEnum in [
                DrawActionEnum.DrawArrow, 
                DrawActionEnum.UseMarkerPen, 
                DrawActionEnum.UseEraserRectItem, 
                DrawActionEnum.DrawRectangle, 
                DrawActionEnum.DrawEllipse, 
                DrawActionEnum.DrawStar,
                DrawActionEnum.Blur,
                ]:
                if event.button() == Qt.LeftButton:
                    isOk = False
                    if self.pathItem.polygon.at(0) != self.pathItem.polygon.at(1):
                        isOk = True
                    self.__completeDraw(self.pathItem, isOk)

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace]:
            for item in self.selectedItems():
                finalItem = item
                # 需要兼容边缘操作点和ROI操作点
                while not hasattr(finalItem, "completeDraw") and finalItem.parentItem() != None:
                    finalItem = finalItem.parentItem()

                if hasattr(finalItem, "completeDraw"):
                    if not isinstance(finalItem, CanvasTextItem) or not finalItem.isCanEditable():
                        # self.itemList.remove(finalItem)
                        # self.removeItem(finalItem)
                        self.itemDeleteSignal.emit(self, finalItem)

                        if self._itemNotifyCallBack != None:
                            self._itemNotifyCallBack(SceneUserNotifyEnum.SelectNothing, None)

                        break

        return super().keyPressEvent(event)