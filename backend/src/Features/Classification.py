from src.Documents.Page import Page
from src.Configs import DOCUMENT_CLASSIFICATION_PROMPT
from src.Documents.Document import get_full_document_text
from src.Features.IFeature import AIFeature


class DocumentClassification(AIFeature):

    def classify(self, pages_read: list[Page]):
        self._ai_model.set_prompt(f"{DOCUMENT_CLASSIFICATION_PROMPT} {get_full_document_text(pages_read)}")
        return self._ai_model.get_text_response()