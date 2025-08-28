from abc import ABC, abstractmethod

class IFeature(ABC):
    @abstractmethod
    def run(self): pass

    @abstractmethod
    def create_prompt(self): pass