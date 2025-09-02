from backend.src.Features.IFeature import AIFeature
from backend.src.Configs.DocumentGeneralAudit import DOCUMENT_GENERAL_AUDIT_PROMPT


class GeneralAudit(AIFeature):

    def audit(self, document):
        self._ai_model.set_prompt(f"{DOCUMENT_GENERAL_AUDIT_PROMPT}\n\n"
                                  f"{document.full_document_text}")
        return self._ai_model.get_json_response()