from plugin import *

class Plugin2(PluginInterface):
    @property
    def name(self):
        return "Plugin2"

    @property
    def desc(self):
        return "随便写"