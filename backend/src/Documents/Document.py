from abc import ABC
from dataclasses import dataclass
from src.Documents.Page import Page


def get_full_document_text(pages: list[Page]):
    document_text = ""
    for page in pages:
        document_text += f"{page.text_with_location_content}, "
    return document_text


@dataclass
class Document(ABC):
    pages: list[Page] = None
    _parsed_content: dict | None = None

    @property
    def parsed_content(self) -> dict | None:
        return self._parsed_content

    @parsed_content.setter
    def parsed_content(self, content: dict):
        self._parsed_content = content

    @property
    def number_of_pages(self) -> int:
        return len(self.pages)

    @property
    def full_document_text(self) -> str:
        return get_full_document_text(self.pages)
