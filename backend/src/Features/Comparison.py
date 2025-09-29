from src.Configs import DOCUMENT_COMPARISON_PROMPT
from src.Features.IFeature import AIFeature


class DocumentComparison(AIFeature):
    def compare(self, document1, document2):
        self._ai_model.set_prompt(
            f"{DOCUMENT_COMPARISON_PROMPT}\n\n"
            f"{document1.name}: {document1.parsed_content}\n\n"
            f"{document2.name}: {document2.parsed_content}"
        )
        return self._ai_model.get_json_response()
