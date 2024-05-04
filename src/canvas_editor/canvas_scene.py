import os, random
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
    Mosaic = "马赛克"

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None, backgroundBrush:QBrush = None):
        super().__init__(parent)
        self._currentDrawActionEnum = DrawActionEnum.DrawNone
        self._isLockedTool = False

        self.pathItem = None
        self.lastAddItem = None
        self.bgBrush = backgroundBrush

        self.itemList:list = []

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
        self._startDraw(pathItem1)

        pathItem2 = CanvasCommonPathItem(None, True)
        pathItem2.polygon = QPolygonF(finalPoints)
        pathItem2.completeDraw()
        pathItem2.moveBy(300, 0)
        self._startDraw(pathItem2)

        pathItem3 = CanvasEditablePath(None, False)
        pathItem3.addPoint(QPointF(-100, -100), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-30, -50), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-200, -280), Qt.SizeAllCursor)
        pathItem3.update()
        self._startDraw(pathItem3)

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

    def _startDraw(self, item:QGraphicsObject):
        if self.lastAddItem != None:
            self.lastAddItem.setEditableState(False)
        self.addItem(item)

    def _completeDraw(self, item:QGraphicsObject, isOk:bool = True):
        if isOk:
            item.completeDraw()
            self.itemList.append(item)
            self.lastAddItem = item
            item.setEditableState(True)

        if not isOk:
            self.removeItem(item)
            if self.lastAddItem != None:
                self.lastAddItem.setEditableState(True)

        self.pathItem = None

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
        if self.currentDrawActionEnum in [DrawActionEnum.DrawNone, DrawActionEnum.SelectItem] or (item == self.lastAddItem and item != None):
            return super().mousePressEvent(event)
        else:
            if event.button() == Qt.LeftButton:
                if self.pathItem == None:
                    if self.currentDrawActionEnum == DrawActionEnum.EditText:
                        self.pathItem = CanvasTextItem()
                        self.pathItem.switchEditableBox()
                        self._startDraw(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                        self._completeDraw(self.pathItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerItem:
                        self.pathItem = CanvasMarkderItem(QRectF(0, 0, 50, 50))
                        self._startDraw(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                        self._completeDraw(self.pathItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.PasteSvg:
                        svgNames = [
                            "diagonal_resize_1.svg",
                            "diagonal_resize_2.svg",
                            "horizontal_resize.svg",
                            "vertical_resize.svg",
                            "zsh.svg",
                        ]
                        svgName = svgNames[random.randint(0, 4)]
                        svgPath = os.path.join(os.path.dirname(__file__), "../canvas_item/demos/resources", svgName)
                        if random.randint(0, 9) % 2 == 0:
                            self.pathItem = CanvasSvgItem(QRectF(), svgPath)
                        else:
                            self.pathItem = CanvasSvgItem(QRectF(0, 0, 100, 100), svgPath)

                        self._startDraw(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                        self._completeDraw(self.pathItem)
                    elif self.currentDrawActionEnum == DrawActionEnum.UsePencil:
                        self.pathItem = CanvasPencilItem()
                        self._startDraw(self.pathItem)
                        self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraser:
                        if self.pathItem == None:
                            if self.bgBrush != None:
                                eraseBrush = self.bgBrush
                                erasePen = QPen(eraseBrush, 10)
                            else:
                                erasePen = QPen(Qt.GlobalColor.blue)
                            self.pathItem = CanvasEraserItem(None, erasePen)
                            self._startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraserRectItem:
                        if self.pathItem == None:
                            if self.bgBrush != None:
                                eraseBrush = self.bgBrush
                                erasePen = QPen(eraseBrush, 10)
                            else:
                                erasePen = QPen(Qt.GlobalColor.blue)
                            self.pathItem = CanvasEraserRectItem(None, erasePen)
                            self._startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                        if self.pathItem == None:
                            self.pathItem = CanvasArrowItem()
                            self._startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                        if self.pathItem == None:
                            self.pathItem = CanvasMarkerPen()
                            self._startDraw(self.pathItem)
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
                            self._startDraw(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)

                if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                    if self.pathItem == None:
                        self.pathItem = CanvasPolygonItem()
                        self._startDraw(self.pathItem)
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
                    self._completeDraw(self.pathItem, isOk)
            elif self.currentDrawActionEnum in [DrawActionEnum.UsePencil, DrawActionEnum.UseEraser]:
                if event.button() == Qt.LeftButton:
                    self._completeDraw(self.pathItem)
            elif self.currentDrawActionEnum in [
                DrawActionEnum.DrawArrow, 
                DrawActionEnum.UseMarkerPen, 
                DrawActionEnum.UseEraserRectItem, 
                DrawActionEnum.DrawRectangle, 
                DrawActionEnum.DrawEllipse, 
                DrawActionEnum.DrawStar,
                ]:
                if event.button() == Qt.LeftButton:
                    isOk = False
                    if self.pathItem.polygon.at(0) != self.pathItem.polygon.at(1):
                        isOk = True
                    self._completeDraw(self.pathItem, isOk)
        super().mouseReleaseEvent(event)