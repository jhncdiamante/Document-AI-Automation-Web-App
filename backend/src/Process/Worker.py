from pdf2image import convert_from_path
import numpy as np
import json
from datetime import datetime

from backend.src.Documents.Page import Page
from backend.src.OCR.PaddleTextRecognition import PaddleOCRTextRecognition
from backend.src.Features.Classification import DocumentClassification
from backend.src.LLM.Models.ChatGPT import ChatGPTAI
from backend.src.Documents.DocumentFormatting.DeathCertificate import DeathCertificate
from backend.src.Documents.DocumentFormatting.DRW import DeathRegistrationWorksheet
from backend.src.Features.Formatter import DocumentFormatter
from backend.src.Features.Comparison import DocumentComparison
from backend.src.Features.General import GeneralAudit


class Worker:
    def __init__(self, ai_model=None, socketio=None, poppler_path=r"D:\libraries_and_such\poppler\poppler-25.07.0\Library\bin"):
        self.ai = ai_model or ChatGPTAI()
        self.formatter = DocumentFormatter(self.ai)
        self.comparer = DocumentComparison(self.ai)
        self.classifier = DocumentClassification(self.ai)
        self.general_audit = GeneralAudit(self.ai)
        self.ocr = PaddleOCRTextRecognition()
        self.socketio = socketio  
        self.poppler_path = poppler_path

    def _convert_pdf_pages_to_images(self, pdf_path):
        return convert_from_path(
            pdf_path=pdf_path,
            poppler_path=self.poppler_path
        )

    def _standardize_document(self, uploaded_files):
        print("Standardizing document pages.")
        documents = []
        for file in uploaded_files:
            pages = self._convert_pdf_pages_to_images(file)
            pages_read = []

            for page in pages[:1]:
                image_np = np.array(page)
                recognized_texts = self.ocr.get_recognized_texts(image_np)
                pages_read.append(Page(content=recognized_texts))

            document_type = self.classifier.classify(pages_read).strip().lower()

            if document_type == "death registration worksheet":
                document = DeathRegistrationWorksheet(pages=pages_read)
            elif document_type == "certificate of death":
                document = DeathCertificate(pages=pages_read)
            else:
                raise ValueError(f"Could not determine document type {document_type}")

            self.formatter.format_document(document)
            documents.append(document)
        return documents

    def process_job(self, job):
        print("Processing job....")
        self.socketio.start_background_task(
            self.socketio.emit,
            "job_in_progress",
            {"id": job.job_id, "status": "processing"}
        )

        feature = job.selected_feature
        print(feature)
        uploaded_files = job.files

        documents = self._standardize_document(uploaded_files)

        if feature.lower() == "general":
            feature_results = self.general_audit.audit(documents[0])
        elif feature.lower() == "comparison":
            feature_results = self.comparer.compare(
                document1=documents[0], document2=documents[1]
            )
        else:
            raise ValueError(f"Unknown feature: {feature}")

        result = {
            "id": job.job_id,
            "status": "completed",
            "accuracy": feature_results.get("accuracy"),
            "issues": feature_results.get("issues"),
            "completed_at": datetime.now().isoformat()
        }

        self.socketio.start_background_task(
            self.socketio.emit,
            "job_update",
            result
        )

        return result
