from abc import ABC
from dataclasses import dataclass
from backend.src.Documents.Page import Page

@dataclass
class Document(ABC):
    type: str | None = None
    pages: list[Page] = None

    @property
    def number_of_pages(self) -> int:
        return len(self.pages)

    @property
    def full_document_text(self) -> str:
        document_text = ""
        for page in self.pages:
            document_text += f"{page.text_content}, "
        return document_text

        
