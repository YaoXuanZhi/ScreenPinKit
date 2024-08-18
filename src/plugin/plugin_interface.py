from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def execute(self):
        pass