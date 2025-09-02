from backend.src.Configs.DocumentComparison import DOCUMENT_COMPARISON_PROMPT
from backend.src.Features.IFeature import AIFeature

class DocumentComparison(AIFeature):
    def compare(self, document1, document2):
        self._ai_model.set_prompt(f"{DOCUMENT_COMPARISON_PROMPT}\n\n"
                                        f"Document 1: {document1.full_document_text}\n\n"
                                        f"Document 2: {document2.full_document_text}")
        return self._ai_model.get_json_response()