from backend.src.Configs.DocumentFormats import DOCUMENT_FORMATTING_PROMPT
from backend.src.Documents.DocumentFormatting.DeathCertificate import DeathCertificate
from backend.src.Documents.DocumentFormatting.DRW import DeathRegistrationWorksheet


DOCUMENT_FORMATS = [DeathRegistrationWorksheet, DeathCertificate]

class DocumentFormatter:
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def format_document(self, document):

        doc_fields = None
        for document_format in DOCUMENT_FORMATS:
            if document.type == document_format.name:
                doc_fields = document_format.fields
                break
        else:
            raise ValueError(f"Document type of {document.type} is not supported.")

        self.llm_model.set_prompt(f"{DOCUMENT_FORMATTING_PROMPT}\n"
                                  f"{doc_fields}\n\n"
                                  f"{document.full_document_text}")
        prompt_results = self.llm_model.run()
        return prompt_results