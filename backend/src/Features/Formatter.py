from src.Configs import DOCUMENT_FORMATTING_PROMPT
from src.Features.IFeature import AIFeature

class DocumentFormatter(AIFeature):

    def format_document(self, document):
        self._ai_model.set_prompt(f"{DOCUMENT_FORMATTING_PROMPT}\n"
                                  f"Document fields: {document.fields}\n\n"
                                  f"Document Text Content: {document.full_document_text}")
        document.parsed_content = self._ai_model.get_text_response()