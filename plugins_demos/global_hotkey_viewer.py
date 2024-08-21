from plugin import *

class GlobalHotkeyViewerPlugin(PluginInterface):
    @property
    def name(self):
        return "全局快捷键查看器"

    @property
    def desc(self):
        return "打印快捷键信息"

    def handleEvent(self, eventName: GlobalEventEnum, *args, **kwargs):
        if eventName == GlobalEventEnum.GlobalHotKeyRegisterEnd:
            keyboard:KeyboardEx = kwargs["keyboard"]
            self.log(f"已注册快捷键：{keyboard.map_callbacks.keys()}")
        pass