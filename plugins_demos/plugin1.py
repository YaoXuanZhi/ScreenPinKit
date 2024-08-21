from plugin import *

class Plugin1(PluginInterface):
    @property
    def name(self):
        return "Plugin1"

    @property
    def desc(self):
        return "有啥作用呢？1"

    def handleEvent(self, eventName, *args, **kwargs):
        return super().handleEvent(eventName, *args, **kwargs)