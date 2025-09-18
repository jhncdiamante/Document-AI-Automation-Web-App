from src.Features.IFeature import AIFeature
from src.Configs import DOCUMENT_GENERAL_AUDIT_PROMPT


class GeneralAudit(AIFeature):

    def audit(self, document):
        self._ai_model.set_prompt(f"{DOCUMENT_GENERAL_AUDIT_PROMPT}\n\n"
                                  f"{document.parsed_content}")
        return self._ai_model.get_json_response()