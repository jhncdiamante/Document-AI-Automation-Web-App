from pdf2image import convert_from_path
import numpy as np
from datetime import datetime

from src.Models import Job as JobModel, AuditResult, Upload, db
from src.Documents.Page import Page
from src.OCR.PaddleTextRecognition import PaddleOCRTextRecognition
from src.Features.Classification import DocumentClassification
from src.LLM.Models.ChatGPT import ChatGPTAI
from src.Documents.DocumentFormatting.DeathCertificate import DeathCertificate
from src.Documents.DocumentFormatting.DRW import DeathRegistrationWorksheet
from src.Features.Formatter import DocumentFormatter
from src.Features.Comparison import DocumentComparison
from src.Features.General import GeneralAudit


class Worker:
    def __init__(self, ai_model=None, socketio=None, poppler_path=None):
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

            for page in pages[:1]:  # only first page for now
                image_np = np.array(page)
                recognized_texts = self.ocr.get_recognized_texts(image_np)
                pages_read.append(Page(content=recognized_texts))

            document_type = (self.classifier.classify(pages_read) or "").strip().lower()

            if document_type == "death registration worksheet":
                document = DeathRegistrationWorksheet(pages=pages_read)
            elif document_type == "certificate of death":
                document = DeathCertificate(pages=pages_read)
            else:
                raise ValueError(f"Could not determine document type {document_type}")

            self.formatter.format_document(document)
            documents.append(document)
        return documents

    def process_job(self, job_record: JobModel):
        """
        Takes a JobModel record directly from DB.
        Fetches related uploads for processing.
        """
        job_record.status = "processing"
        db.session.add(job_record)
        db.session.commit()
        # tell frontend job started
        self._emit_to_frontend("job_progress", {
            "id": job_record.id,
            "status": "processing",
            "user_id": job_record.user_id
        })

        print("Processing job")
        
        try:
            uploaded_files = [u.file_path for u in job_record.uploads]
            documents = self._standardize_document(uploaded_files)

            # run feature logic
            if job_record.feature.lower() == "general":
                feature_results = self.general_audit.audit(documents[0])
            elif job_record.feature.lower() == "cross-check":
                feature_results = self.comparer.compare(
                    document1=documents[0], document2=documents[1]
                )
            else:
                raise ValueError(f"Unknown feature: {job_record.feature}")

            # job canceled mid-way?
            if job_record.status == "canceled":
                return

            job_record.status = "completed"

            audit = AuditResult(
                job_id=job_record.id,
                accuracy=feature_results.get("accuracy"),
                issues=feature_results.get("issues"),
            )
            db.session.add(job_record)  

            db.session.add(audit)
            db.session.commit()

            result = {
                "id": job_record.id,
                "status": "completed",
                "accuracy": audit.accuracy,
                "issues": audit.issues,
                "completed_at": audit.completed_at.isoformat(),
                "user_id": job_record.user_id

            }
            self._emit_to_frontend("job_update", result)


        except Exception as e:
            db.session.rollback()

            job_record.status = "failed"
            job_record.error = str(e)

            db.session.add(job_record)  
            audit = AuditResult(job_id=job_record.id)

            db.session.add(audit)
            db.session.commit()


            result = {
                "id": job_record.id,
                "status": job_record.status,
                "error": job_record.error,
                "completed_at": audit.completed_at.isoformat(),
                "user_id": job_record.user_id
            }
            self._emit_to_frontend("job_failed", result)


    def _emit_to_frontend(self, name: str, data: dict, namespace="/"):
        """Send socketio events only to the owning user"""
        room = f"user_{data.get('user_id')}"
        self.socketio.start_background_task(
            self.socketio.emit,
            name,
            data,
            namespace=namespace,
            room=room
        )
