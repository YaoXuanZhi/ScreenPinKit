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
    UseMarkerPen = "使用记号笔"
    UseMarkerItem = "使用标记"
    PasteSvg = "粘贴图案"

    DrawDiversity = "绘制多边形"
    DrawRectangle = "绘制矩形"
    DrawEllipse = "绘制椭圆"
    DrawArrow = "绘制箭头"
    DrawStar = "绘制五角星"
    DrawPolygonalLine = "绘制折线"
    SwitchLock = "切换锁定"
    SelectItem = "选择对象"
    Mosaic = "马赛克"

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None, backgroundBrush:QBrush = None):
        super().__init__(parent)
        self.currentDrawActionEnum = DrawActionEnum.DrawNone

        self.pathItem = None
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
        pathItem1.setEditableState(True)
        pathItem1.completeDraw()
        self.addItem(pathItem1)

        pathItem2 = CanvasCommonPathItem(None, True)
        pathItem2.polygon = QPolygonF(finalPoints)
        pathItem2.completeDraw()
        pathItem2.setEditableState(True)
        pathItem2.moveBy(300, 0)
        self.addItem(pathItem2)

        pathItem3 = CanvasEditablePath(None, False)
        pathItem3.addPoint(QPointF(-100, -100), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-30, -50), Qt.PointingHandCursor)
        pathItem3.addPoint(QPointF(-200, -280), Qt.SizeAllCursor)
        pathItem3.update()
        self.addItem(pathItem3)

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

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        view:QGraphicsView = self.views()[0]
        pos = view.mapFromScene(event.scenePos())
        item = view.itemAt(pos)
        targetPos = event.scenePos()
        if item != None and self.pathItem != item:
            return super().mousePressEvent(event)
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            if event.button() == Qt.LeftButton:
                if not view.isCanDrag() and item == None:
                    if self.currentDrawActionEnum == DrawActionEnum.EditText:
                        self.pathItem = CanvasTextItem()
                        self.pathItem.switchEditableBox()
                        self.addItem(self.pathItem)

                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerItem:
                        self.pathItem = CanvasMarkderItem(QRectF(0, 0, 50, 50))
                        self.addItem(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
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

                        self.addItem(self.pathItem)
                        targetPos.setX(targetPos.x() - self.pathItem.boundingRect().width() / 2)
                        targetPos.setY(targetPos.y() - self.pathItem.boundingRect().height() / 2)
                        self.pathItem.setPos(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UsePencil:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasPencilItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseEraser:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            if self.bgBrush != None:
                                eraseBrush = self.bgBrush
                                erasePen = QPen(eraseBrush, 10)
                            else:
                                erasePen = QPen(Qt.GlobalColor.blue)
                            self.pathItem = CanvasEraserItem(None, erasePen)
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)

                # if not self.views()[0].isCanDrag() and (not item or self.pathItem == item or not issubclass(type(item), CanvasROI)):
                if not view.isCanDrag() and (not item or self.pathItem == item or not issubclass(type(item), CanvasROI) or issubclass(type(item), CanvasCommonPathItem)):
                    if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasPolygonItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                        else:
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.update()
                    elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasArrowItem()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            self.pathItem = CanvasMarkerPen()
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
                    elif self.currentDrawActionEnum in [DrawActionEnum.DrawRectangle, DrawActionEnum.DrawEllipse, DrawActionEnum.DrawStar]:
                        if self.pathItem == None:
                            self.setEditableState(False)
                            if self.currentDrawActionEnum == DrawActionEnum.DrawRectangle:
                                self.pathItem = CanvasClosedShapeItem(None, CanvasClosedShapeEnum.Rectangle)
                            elif self.currentDrawActionEnum == DrawActionEnum.DrawEllipse:
                                self.pathItem = CanvasClosedShapeItem(None, CanvasClosedShapeEnum.Ellipse)
                            elif self.currentDrawActionEnum == DrawActionEnum.DrawStar:
                                self.pathItem = CanvasClosedShapeItem(None, CanvasClosedShapeEnum.Star)
                            self.addItem(self.pathItem)
                            self.pathItem.polygon.append(targetPos)
                            self.pathItem.polygon.append(targetPos)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            if self.pathItem != None and not self.views()[0].isCanDrag():
                targetPos = event.scenePos()

                if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum == DrawActionEnum.UsePencil:
                    self.pathItem.polygon.append(targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum == DrawActionEnum.UseEraser:
                    self.pathItem.polygon.append(targetPos)
                    self.pathItem.update()
                elif self.currentDrawActionEnum in [DrawActionEnum.DrawRectangle, DrawActionEnum.DrawEllipse, DrawActionEnum.DrawStar]:
                    self.pathItem.polygon.replace(self.pathItem.polygon.count() - 1, targetPos)
                    self.pathItem.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        finalItem = None
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            if self.currentDrawActionEnum == DrawActionEnum.DrawPolygonalLine:
                if event.button() == Qt.RightButton and self.pathItem != None:
                    if self.pathItem.polygon.count() > 1:
                        self.pathItem.polygon.remove(self.pathItem.polygon.count() - 1)
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                        finalItem = self.pathItem
                    else:
                        self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
            elif self.currentDrawActionEnum == DrawActionEnum.DrawArrow:                
                if event.button() == Qt.RightButton and self.pathItem != None:
                    self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                        finalItem = self.pathItem
                    self.setEditableState(True)
                    self.pathItem = None
            elif self.currentDrawActionEnum == DrawActionEnum.UseMarkerPen:                
                if event.button() == Qt.RightButton and self.pathItem != None:
                    self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                        finalItem = self.pathItem
                    self.setEditableState(True)
                    self.pathItem = None
            elif self.currentDrawActionEnum == DrawActionEnum.UsePencil:                
                if event.button() == Qt.LeftButton and self.pathItem != None:
                    self.pathItem.completeDraw()
                    self.itemList.append(self.pathItem)
                    self.pathItem = None
            elif self.currentDrawActionEnum == DrawActionEnum.UseEraser:                
                if event.button() == Qt.LeftButton and self.pathItem != None:
                    self.pathItem.completeDraw()
                    self.itemList.append(self.pathItem)
                    self.pathItem = None
            elif self.currentDrawActionEnum in [DrawActionEnum.DrawRectangle, DrawActionEnum.DrawEllipse, DrawActionEnum.DrawStar]:
                if event.button() == Qt.RightButton and self.pathItem != None:
                    self.removeItem(self.pathItem)
                    self.setEditableState(True)
                    self.pathItem = None
                elif event.button() == Qt.LeftButton and self.pathItem != None:
                    if self.pathItem.polygon.at(0) == self.pathItem.polygon.at(1):
                        self.removeItem(self.pathItem)
                    else:
                        self.pathItem.completeDraw()
                        self.itemList.append(self.pathItem)
                        finalItem = self.pathItem
                    self.setEditableState(True)
                    self.pathItem = None
        # if finalItem != None:
        #     finalItem.setFocus(Qt.FocusReason.OtherFocusReason)
        #     finalItem.setSelected(True)
        super().mouseReleaseEvent(event)