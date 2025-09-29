from abc import ABC, abstractmethod


class IModel(ABC):
    @abstractmethod
    def set_prompt(self):
        pass

    @abstractmethod
    def get_text_response(self):
        pass
