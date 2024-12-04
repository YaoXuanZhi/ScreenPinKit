from enum import Enum
from extend_widgets import *

class EnumItemCardState(Enum):
    NoneState = -1 # 未知
    UninstallState = 0 # 未安装
    ActiveState = 1 # 已安装且已启用
    DeActiveState = 2 # 已安装但未启用

class PluginConfigItem(ConfigItem):
    """ Config item with options """

    @property
    def options(self):
        return self.validator.options

    @property
    def isIgnored(self):
        return False

    def __str__(self):
        return f'{self.__class__.__name__}[options={self.options}, value={self.value}]'

class PluginConfigItemEx(PluginConfigItem):
    """ Config item with options """
    def __init__(self, group, name, default):
        super().__init__(group, name, default, OptionsValidator(EnumItemCardState), EnumSerializer(EnumItemCardState))

    @property
    def isIgnored(self):
        if self.value in [EnumItemCardState.NoneState, EnumItemCardState.UninstallState]:
            return True
        return False

class QPluginConfig(QObject):
    """ 
    Config of plugin，支持动态拓展属性
    参考QConfig实现
    """

    def __init__(self):
        super().__init__()
        self.file = Path("config/config.json")
        self._cfg = self

    def get(self, item):
        """ get the value of config item """
        return item.value

    def set(self, item, value, save=True, copy=True):
        """ set the value of config item

        Parameters
        ----------
        item: ConfigItem
            config item

        value:
            the new value of config item

        save: bool
            whether to save the change to config file

        copy: bool
            whether to deep copy the new value
        """
        if item.value == value:
            return

        # deepcopy new value
        try:
            item.value = deepcopy(value) if copy else value
        except:
            item.value = value

        if save:
            self.save()

    def toDict(self, serialize=True):
        """ convert config items to `dict` """
        items = {}
        for name in dir(self._cfg):
            item = getattr(self._cfg, name)
            if not isinstance(item, ConfigItem):
                continue

            if isinstance(item, PluginConfigItem):
                if item.isIgnored:
                    continue

            value = item.serialize() if serialize else item.value
            if not items.get(item.group):
                if not item.name:
                    items[item.group] = value
                else:
                    items[item.group] = {}

            if item.name:
                items[item.group][item.name] = value

        return items

    def save(self):
        """ save config """
        self._cfg.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cfg.file, "w", encoding="utf-8") as f:
            json.dump(self._cfg.toDict(), f, ensure_ascii=False, indent=4)

    @exceptionHandler()
    def load(self, file=None, config=None):
        """ load config

        Parameters
        ----------
        file: str or Path
            the path of json config file

        config: Config
            config object to be initialized
        """
        if isinstance(config, QPluginConfig):
            self._cfg = config

        if isinstance(file, (str, Path)):
            self._cfg.file = Path(file)

        try:
            with open(self._cfg.file, encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = {}

        # map config items'key to item
        items = {}
        for name in dir(self._cfg):
            item = getattr(self._cfg, name)
            if isinstance(item, ConfigItem):
                items[item.key] = item

        # update the value of config item
        for k, v in cfg.items():
            if not isinstance(v, dict) and items.get(k) is not None:
                items[k].deserializeFrom(v)
            elif isinstance(v, dict):
                for key0, value in v.items():
                    key = k + "." + key0

                    if items.get(key) is None:
                        configItem = PluginConfigItemEx(k, key0, EnumItemCardState.UninstallState)
                        setattr(self._cfg, k, configItem)
                        item = getattr(self._cfg, k)
                        item.deserializeFrom(value)
                        items[item.key] = item
                    else:
                        items[key].deserializeFrom(value)

    def isOnByPluginName(self, pluginName):
        if not hasattr(self._cfg, pluginName):
            return False

        configItem = getattr(self._cfg, pluginName)
        result = self.get(configItem)
        return result == EnumItemCardState.ActiveState

pluginCfg = QPluginConfig()