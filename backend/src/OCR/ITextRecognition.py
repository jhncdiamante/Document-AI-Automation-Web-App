from abc import ABC, abstractmethod
from src.Documents.Page import Page


class ITextRecognition(ABC):
    @abstractmethod
    def get_recognized_texts(self, page: Page):
        pass
