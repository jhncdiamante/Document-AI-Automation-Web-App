from dataclasses import dataclass

@dataclass
class Page:
    content: list[tuple]

    @property
    def average_recognition_accuracy(self) -> float:
        return sum([score for _, score in self.content]) / len(self.content)

    @property
    def text_content(self) -> str:
        return ", ".join([text for text, _ in self.content])
    