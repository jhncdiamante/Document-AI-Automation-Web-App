from pdf2image import convert_from_path
import numpy as np
import traceback
from sqlalchemy.orm import sessionmaker, joinedload
from contextlib import contextmanager
from src.Models import Job as JobModel, AuditResult, db
from src.Documents.Page import Page
from src.OCR.PaddleTextRecognition import PaddleOCRTextRecognition
from src.Features.Classification import DocumentClassification
from src.LLM.Models.ChatGPT import ChatGPTAI
from src.Documents.DocumentFormatting.DeathCertificate import DeathCertificate
from src.Documents.DocumentFormatting.DRW import DeathRegistrationWorksheet
from src.Features.Formatter import DocumentFormatter
from src.Features.Comparison import DocumentComparison
from src.Features.General import GeneralAudit

from src.flask_config import app
from src.Socket import socketio

class Worker:
    def __init__(self, ai_model=None, poppler_path=None):
        self.app = app
        self.ai = ai_model or ChatGPTAI()
        self.formatter = DocumentFormatter(self.ai)
        self.comparer = DocumentComparison(self.ai)
        self.classifier = DocumentClassification(self.ai)
        self.general_audit = GeneralAudit(self.ai)
        self.ocr = PaddleOCRTextRecognition()
        self.socketio = socketio
        self.poppler_path = poppler_path

        with app.app_context():
            self.SessionLocal = sessionmaker(bind=db.engine)

    @contextmanager
    def get_db_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _convert_pdf_pages_to_images(self, pdf_path):
        return convert_from_path(pdf_path=pdf_path, poppler_path=self.poppler_path)

    def _standardize_document(self, uploaded_files):
        documents = []
        print(f"Standardizing documents...")
        for file in uploaded_files[:1]:
            pages = self._convert_pdf_pages_to_images(file)
            pages_read = []
            for page in pages:
                image_np = np.array(page)
                recognized_texts = self.ocr.get_recognized_texts(image_np)
                pages_read.append(Page(content=recognized_texts))

            doc_type = (self.classifier.classify(pages_read) or "").strip().lower()
            if doc_type == "death registration worksheet":
                document = DeathRegistrationWorksheet(pages=pages_read)
            elif doc_type == "certificate of death":
                document = DeathCertificate(pages=pages_read)
            else:
                raise ValueError(f"Unknown document type {doc_type}")

            self.formatter.format_document(document)
            documents.append(document)
        return documents

    def process_job(self, job_id):
        try:
            print("Processing job...")
            with self.app.app_context():
                with self.get_db_session() as session:
                    job = session.query(JobModel).options(joinedload(JobModel.uploads)).get(job_id)
                    if not job or job.status == "canceled":
                        return
                    job.status = "processing"
                    session.commit()
                    uploaded_files = [u.file_path for u in job.uploads]
                    feature = job.feature
                    user_id = job.user_id
            print(f"Emitting job progress to frontend: Processing")
            self._emit_job_progress(job_id, user_id)

            documents = self._standardize_document(uploaded_files)

            with self.app.app_context():
                with self.get_db_session() as session:
                    job_check = session.get(JobModel, job_id)
                    if job_check and job_check.status == "canceled":
                        return

            if feature.lower() == "general":
                results = self.general_audit.audit(documents[0])
            elif feature.lower() == "cross-check":
                results = self.comparer.compare(documents[0], documents[1])
            else:
                raise ValueError(f"Unknown feature {feature}")

            with self.app.app_context():
                with self.get_db_session() as session:
                    job_db = session.get(JobModel, job_id)
                    if job_db.status != "canceled":
                        job_db.status = "completed"
                        audit = AuditResult(job_id=job_db.id, accuracy=results.get("accuracy"),
                                            issues=results.get("issues"))
                        session.add(audit)
                        session.commit()
                        self._emit_job_update({
                            "id": job_db.id,
                            "status": "completed",
                            "accuracy": audit.accuracy,
                            "issues": audit.issues,
                            "completed_at": audit.completed_at.isoformat(),
                            "user_id": job_db.user_id
                        })

        except Exception as e:
            traceback.print_exc()
            with self.app.app_context():
                with self.get_db_session() as session:
                    job_db = session.get(JobModel, job_id)
                    if job_db:
                        job_db.status = "failed"
                        job_db.error = str(e)
                        audit = AuditResult(job_id=job_db.id, error=str(e))
                        session.add(audit)
                        session.commit()
                        self._emit_job_failed({
                            "id": job_db.id,
                            "status": "failed",
                            "error": job_db.error,
                            "completed_at": audit.completed_at.isoformat(),
                            "user_id": job_db.user_id
                        })

    def _emit_job_progress(self, job_id, user_id):
        self.socketio.emit("job_progress", {"id": job_id, "status": "processing", "user_id": user_id},
                           room=f"user_{user_id}")

    def _emit_job_update(self, data):
        self.socketio.emit("job_update", data, room=f"user_{data.get('user_id')}")

    def _emit_job_failed(self, data):
        self.socketio.emit("job_failed", data, room=f"user_{data.get('user_id')}")



