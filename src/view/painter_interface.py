# coding=utf-8
from enum import Enum
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common import ScreenShotIcon
from qfluentwidgets import *

from canvas_editor import CanvasEditor, DrawActionEnum, SceneUserNotifyEnum
from canvas_item import *
from toolbar import *

# 绘制动作
class DrawAction():
    def __init__(self, actionEnum:DrawActionEnum, painterTool:QWidget, callback=None) -> None:
        self.actionEnum:DrawActionEnum = actionEnum
        self.painterTool = painterTool
        self.callback = callback

    def switchEditState(self, isEdit:bool):
        if self.callback != None:
            self.callback(isEdit)

# 绘图控件
class PainterInterface(QWidget):
    def __init__(self, parent=None, physicalPixmap:QPixmap=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.physicalPixmap = physicalPixmap
        self.toolbar:QWidget = None
        self.actionGroup:QActionGroup = None
        self.drawWidget:CanvasEditor = None
        self.sceneBrush:QBrush = None
        self.painterToolBarMgr:PainterToolBarManager = None
        self.clearDraw(True)
        self.initLayout()

    def initLayout(self):
        self.contentLayout = QVBoxLayout()
        self.contentLayout.setAlignment(Qt.AlignHCenter)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.contentLayout)

        if self.physicalPixmap != None:
            basePixmap = self.physicalPixmap.copy()
            self.sceneBrush = QBrush(basePixmap)
            screenDevicePixelRatio = QApplication.primaryScreen().grabWindow(0).devicePixelRatio()
            transform = QTransform()
            transform.scale(1/screenDevicePixelRatio, 1/screenDevicePixelRatio)
            self.sceneBrush.setTransform(transform)

    def getCommandBarPosition(self) -> BubbleTipTailPosition:
        return BubbleTipTailPosition.TOP_RIGHT

    def showCommandBar(self):
        if self.toolbar != None:
            self.toolbar.show()
            self.drawWidget.switchDrawTool(DrawActionEnum.DrawNone)
            return

        position = self.getCommandBarPosition()
        view = CommandBarView(self)

        # 锁定机制-绘制工具
        lockState = self.drawWidget.getLockState()
        if lockState:
            switchLockAction = Action(ScreenShotIcon.LOCKED, '锁定', triggered=self.switchLocked)
        else:
            switchLockAction = Action(ScreenShotIcon.UNLOCKED, '解锁', triggered=self.switchLocked)

        switchLockAction.setCheckable(True)
        self.switchLockButton = view.addAction(switchLockAction)
        switchLockAction.setChecked(lockState)

        view.addSeparator()

        selectItemAction = Action(ScreenShotIcon.SELECT_ITEM, '选择', triggered=lambda: self.switchDrawTool(DrawActionEnum.SelectItem))
        finalDrawActions = [
            selectItemAction
        ]
        self.selectItemAction = selectItemAction

        # 初始化绘制工具栏
        drawActions = [
            Action(ScreenShotIcon.SHAPE, '形状', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawRectangle)),
            Action(ScreenShotIcon.POLYGONAL_LINE, '折线', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawPolygonalLine)),
            Action(ScreenShotIcon.GUIDE, '标记', triggered=lambda: self.switchDrawTool(DrawActionEnum.UseMarkerItem)),
            # Action(ScreenShotIcon.POLYGON, '图案', triggered=lambda: self.switchDrawTool(DrawActionEnum.PasteSvg)),
            Action(ScreenShotIcon.ARROW, '箭头', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow)),
            Action(ScreenShotIcon.MARKER_PEN, '记号笔', triggered=lambda: self.switchDrawTool(DrawActionEnum.UseMarkerPen)),
            Action(ScreenShotIcon.PENCIL, '铅笔', triggered=lambda: self.switchDrawTool(DrawActionEnum.UsePencil)),
            Action(ScreenShotIcon.TEXT, '文本', triggered=lambda: self.switchDrawTool(DrawActionEnum.EditText)),
        ]

        for action in drawActions:
            finalDrawActions.append(action)

        # 仅当有背景画刷的时候，橡皮擦和模糊工具才可以使用
        if self.drawWidget.sceneBrush != None:
            extendActions = [
                Action(ScreenShotIcon.ERASE, '橡皮擦', triggered=lambda: self.switchDrawTool(DrawActionEnum.UseEraser)),
                Action(ScreenShotIcon.FILL_REGION, '马赛克', triggered=lambda: self.switchDrawTool(DrawActionEnum.Blur)),
            ]
            for action in extendActions:
                finalDrawActions.append(action)

        self.actionGroup = QActionGroup(self)
        for action in finalDrawActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)

        view.addActions(finalDrawActions)
        view.addSeparator()
        view.addActions([
            Action(ScreenShotIcon.DELETE_ALL, '清除绘画', triggered=self.clearDraw),
            Action(ScreenShotIcon.UNDO2, '撤销', triggered=self.undo),
            Action(ScreenShotIcon.REDO2, '重做', triggered=self.redo),
            Action(ScreenShotIcon.FINISHED, '完成绘画', triggered=self.completeDraw),
        ])

        view.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        view.setIconSize(QSize(20, 20))

        view.resizeToSuitableWidth()

        self.toolbar = BubbleTip.make(
            target=self,
            view=view,
            duration=-1,
            tailPosition=position,
            parent=self,
        )

        self.initDrawLayer()
        self.painterToolBarMgr = PainterToolBarManager(view)
        self.painterToolBarMgr.providerChangeDrawActionSignal.connect(self.onProviderChangeDrawAction)

    def onProviderChangeDrawAction(self, drawActionEnum:DrawActionEnum):
        self.switchDrawTool(drawActionEnum)

    def initDrawLayer(self):
        if self.drawWidget != None: 
            return

        self.drawWidget = CanvasEditor(self, self.sceneBrush)
        self.drawWidget.initUI()
        self.drawWidget.setNofityEvent(self.sceneUserNotifyHandler)
        self.contentLayout.addWidget(self.drawWidget)

    def sceneUserNotifyHandler(self, sceneUserNotifyEnum:SceneUserNotifyEnum, item:QGraphicsItem):
        if sceneUserNotifyEnum == SceneUserNotifyEnum.EndDrawedEvent and not self.drawWidget.getLockState():
            if item != None:
                if hasattr(item, "forcecSelect"):
                    item.forcecSelect()
                self.directSwitchSelectItem()
            self.selectItemAction.setChecked(True)

        if sceneUserNotifyEnum in [SceneUserNotifyEnum.SelectItemChangedEvent, SceneUserNotifyEnum.StartDrawedEvent, SceneUserNotifyEnum.SelectNothing]:
            if self.painterToolBarMgr != None:
                self.painterToolBarMgr.switchSelectItemToolBar(item, sceneUserNotifyEnum)

    def completeDraw(self):
        self.switchDrawTool(DrawActionEnum.DrawNone)
        if self.toolbar != None:
            self.clearDrawFlag()
            self.toolbar.close()
            self.toolbar.destroy()
            self.toolbar = None
            self.painterToolBarMgr.close()
            self.painterToolBarMgr = None
            self.drawWidget.quitDraw()

    def switchLocked(self):
        self.drawWidget.switchLockState()
        finalIcon = None
        tip = ""
        if self.drawWidget.getLockState():
            finalIcon = ScreenShotIcon.LOCKED
            tip = "锁定"
        else:
            finalIcon = ScreenShotIcon.UNLOCKED
            tip = "解锁"
        self.switchLockButton.setIcon(finalIcon)
        self.switchLockButton.setToolTip(tip)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.completeDraw()

    def keyPressEvent(self, event) -> None:
        # 监听ESC键，当按下ESC键时，逐步取消编辑状态
        if event.key() == Qt.Key_Escape:
            # 如果当前绘图工具不在编辑状态，则本次按下Esc键会关掉绘图工具条
            if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
                self.clearDrawFlag()
                self.drawWidget.quitDraw()
            elif self.toolbar != None and self.toolbar.isVisible():
                self.completeDraw()
            else:
                self.destroyImage()

    def contextMenuEvent(self, event:QContextMenuEvent):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(ScreenShotIcon.WHITE_BOARD, '标注', triggered=self.showCommandBar),
            Action(ScreenShotIcon.COPY, '复制', triggered=self.copyToClipboard),
            Action(ScreenShotIcon.CLICK_THROUGH, '鼠标穿透', triggered=self.clickThrough),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def checkDrawActionChange(self):
        # 如果中途切换了绘图工具，则关闭上一个绘图工具的编辑状态
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum != self.currentDrawActionEnum:
            self.createCustomInfoBar(f"绘图工具切换到 【{self.currentDrawActionEnum.value}】")

    def addDrawAction(self, drawAction:DrawAction):
        self.drawActions.append(drawAction)

    def undo(self):
        self.drawWidget.undo()

    def redo(self):
        self.drawWidget.redo()

    def clickThrough(self):
        self.parentWidget().setMouseThroughState(True)

    def destroyImage(self):
        self.parentWidget().close()

    # 得到最终绘制后的Pixmap
    def getFinalPixmap(self) -> QPixmap:
        # 经测试，这种方式截屏会有概率出现白边，推测是精度问题导致的，遂改成下面的实现
        # return self.grab()
        
        basePixmap = self.physicalPixmap.copy()
        painter = QPainter()
        painter.begin(basePixmap)
        if self.drawWidget != None:
            painter.drawPixmap(self.drawWidget.geometry(), self.drawWidget.grab())
        painter.end()
        return basePixmap
        
    def copyToClipboard(self):
        finalPixmap = self.getFinalPixmap()
        QApplication.clipboard().setPixmap(finalPixmap)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum, cursor:QCursor = Qt.CursorShape.ArrowCursor):
        self.drawWidget.switchDrawTool(drawActionEnum)
        self.currentDrawActionEnum = drawActionEnum 
        if self.painterToolBarMgr != None:
            self.painterToolBarMgr.switchDrawTool(drawActionEnum)
        self.checkDrawActionChange()
        self.setCursor(cursor)
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawRectangle:
            # 如果上一个绘图工具是绘制矩形，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.addDrawAction(DrawAction(drawActionEnum, None))

    def directSwitchSelectItem(self, cursor:QCursor = Qt.CursorShape.ArrowCursor):
        drawActionEnum = DrawActionEnum.SelectItem
        self.drawWidget.switchDrawTool(drawActionEnum)
        self.currentDrawActionEnum = drawActionEnum 
        # if self.painterToolBarMgr != None:
        #     self.painterToolBarMgr.switchDrawTool(drawActionEnum)
        # self.checkDrawActionChange()
        self.setCursor(cursor)
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawRectangle:
            # 如果上一个绘图工具是绘制矩形，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.addDrawAction(DrawAction(drawActionEnum, None))

    def clearDraw(self, isInit:bool=False):
        if not isInit:
            if hasattr(self, "drawWidget"):
                self.drawWidget.clearDraw()

        self.drawActions: list[DrawAction] = []
        self.clearDrawFlag()

    def focusInEvent(self, event:QFocusEvent) -> None:
        self.parentWidget().focused = True
        self.parentWidget().update()

    def focusOutEvent(self, event:QFocusEvent) -> None:
        # 获取鼠标居于屏幕上的位置点
        pos = QCursor.pos()

        # 计算绘图区和工具区的并集
        painterRect = QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(self.rect().bottomRight()))
        rects = [painterRect]
        if self.toolbar != None:
            toolbarRect = QRect(self.toolbar.mapToGlobal(self.toolbar.rect().topLeft()), self.toolbar.mapToGlobal(self.toolbar.rect().bottomRight()))
            rects.append(toolbarRect)
        region = QRegion()
        region.setRects(rects)

        # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
        if not region.contains(pos):
            self.parentWidget().focused = False
            self.parentWidget().update()

    def clearDrawFlag(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if self.actionGroup != None:
            for action in self.actionGroup.actions():
                action.setChecked(False)

    def createCustomInfoBar(self, text:str):
        w = InfoBar.new(
            icon=ScreenShotIcon.GUIDE,
            title='',
            content=text,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.BOTTOM,
            duration=1000,
            parent=self
        )
        # w.iconWidget.setFixedSize(QSize(40, 40))
        w.setCustomBackgroundColor('white', '#202020')

    def wheelEvent(self, event: QWheelEvent):
        if self.painterToolBarMgr != None:
            self.painterToolBarMgr.zoomComponent.TriggerEvent(event.angleDelta().y())
        return super().wheelEvent(event)