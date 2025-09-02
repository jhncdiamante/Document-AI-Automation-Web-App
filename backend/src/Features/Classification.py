from backend.src.Documents.Page import Page
from backend.src.LLM.Configs.ClassificationPrompt import DOCUMENT_CLASSIFICATION_PROMPT
from backend.src.Documents.Document import get_full_document_text
from backend.src.Features.IFeature import AIFeature


class DocumentClassification(AIFeature):

    def classify(self, pages_read: list[Page]):
        self._ai_model.set_prompt(f"{DOCUMENT_CLASSIFICATION_PROMPT} {get_full_document_text(pages_read)}")
        return self._ai_model.get_text_response()