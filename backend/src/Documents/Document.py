from abc import ABC
from dataclasses import dataclass
from backend.src.Documents.Page import Page


def get_full_document_text(pages: list[Page]):
    document_text = ""
    for page in pages:
        document_text += f"{page.text_content}, "
    return document_text

@dataclass
class Document(ABC):
    pages: list[Page] = None
    parsed_content: str | None = None

    @property
    def number_of_pages(self) -> int:
        return len(self.pages)

    @property
    def full_document_text(self) -> str:
        return get_full_document_text(self.pages)

        
