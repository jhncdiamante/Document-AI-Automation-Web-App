from backend.src.Documents.Document import Document
from backend.src.LLM.Configs.ClassificationPrompt import DOCUMENT_CLASSIFICATION_PROMPT

class DocumentClassification:
    def __init__(self, model):
        self.llm_model = model

    def classify(self, document: Document):
        self.llm_model.set_prompt(f"{DOCUMENT_CLASSIFICATION_PROMPT} {document.full_document_text}")
        prompt_results = self.llm_model.get_text_response()
        return prompt_results