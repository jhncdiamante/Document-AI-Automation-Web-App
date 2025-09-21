import eventlet
from pdf2image import convert_from_path
import numpy as np
import traceback
from sqlalchemy.orm import sessionmaker, joinedload
import concurrent.futures
import time
import threading
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


class Worker:
    def __init__(self, app, ai_model=None, socketio=None, poppler_path=None, max_workers=2):
        self.ai = ai_model or ChatGPTAI()
        self.formatter = DocumentFormatter(self.ai)
        self.comparer = DocumentComparison(self.ai)
        self.classifier = DocumentClassification(self.ai)
        self.general_audit = GeneralAudit(self.ai)
        self.ocr = PaddleOCRTextRecognition()
        self.socketio = socketio
        self.poppler_path = poppler_path
        self.app = app
        
        # Use a thread pool executor for CPU-intensive tasks
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        with app.app_context():
            self.SessionLocal = sessionmaker(bind=db.engine)

    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _convert_pdf_pages_to_images(self, pdf_path):
        return convert_from_path(
            pdf_path=pdf_path,
            poppler_path=self.poppler_path
        )

    def _standardize_document(self, uploaded_files):
        print(f"Standardizing document pages for files: {uploaded_files}")
        documents = []
        for file in uploaded_files:
            pages = self._convert_pdf_pages_to_images(file)
            pages_read = []

            for page in pages[:1]:  # only first page for now
                image_np = np.array(page)
                recognized_texts = self.ocr.get_recognized_texts(image_np)
                pages_read.append(Page(content=recognized_texts))

            document_type = (self.classifier.classify(pages_read) or "").strip().lower()
            print(f"Detected document type: {document_type}")

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
        Submit job to thread pool executor - completely non-blocking
        """
        print(f"[Worker] Submitting job {job_record.id} to thread pool")
        
        # Submit to thread pool and don't wait for result
        future = self.executor.submit(self._process_job_in_executor, job_record.id)
        
        # Optional: Add callback for when job completes (but don't block)
        future.add_done_callback(lambda f: self._job_completion_callback(f, job_record.id))

    def _job_completion_callback(self, future, job_id):
        """Called when job completes (success or failure)"""
        try:
            result = future.result()  # This will raise exception if job failed
            print(f"[Worker] Job {job_id} completed successfully in thread pool")
        except Exception as e:
            print(f"[Worker] Job {job_id} failed in thread pool: {e}")

    def _process_job_in_executor(self, job_id):
        """
        The actual job processing that runs in the thread pool executor
        This is completely isolated from the main Flask/eventlet thread
        """
        print(f"[Worker] Starting job {job_id} in thread pool executor")
        
        try:
            # Get job data (with fresh app context)
            with self.app.app_context():
                with self.get_db_session() as session:
                    job = (
                        session.query(JobModel)
                        .options(joinedload(JobModel.uploads))
                        .get(job_id)
                    )
                    
                    if not job:
                        print(f"[Worker] Job {job_id} not found in DB.")
                        return

                    if job.status == "canceled":
                        print(f"[Worker] Job {job_id} was canceled, skipping.")
                        return

                    # Update status to processing
                    job.status = "processing"
                    session.commit()
                    
                    # Get job data for processing
                    uploaded_files = [u.file_path for u in job.uploads]
                    feature = job.feature
                    user_id = job.user_id
                    
                    print(f"[Worker] Processing job {job_id}, feature={feature}, uploads={len(job.uploads)}")

            # Emit progress update (schedule on main thread)
            self._schedule_emit("job_progress", {
                "id": job_id,
                "status": "processing",
                "user_id": user_id
            })

            # Process documents (this is the CPU-intensive part)
            documents = self._standardize_document(uploaded_files)

            # Check if job was canceled during processing
            with self.app.app_context():
                with self.get_db_session() as session:
                    job_check = session.get(JobModel, job_id)
                    if job_check and job_check.status == "canceled":
                        print(f"[Worker] Job {job_id} was canceled during processing")
                        return

            # Run feature analysis
            if feature.lower() == "general":
                feature_results = self.general_audit.audit(documents[0])
            elif feature.lower() == "cross-check":
                feature_results = self.comparer.compare(
                    document1=documents[0], document2=documents[1]
                )
            else:
                raise ValueError(f"Unknown feature: {feature}")

            # Save results
            with self.app.app_context():
                with self.get_db_session() as session:
                    job_db = session.get(JobModel, job_id)
                    if job_db and job_db.status != "canceled":
                        job_db.status = "completed"
                        audit = AuditResult(
                            job_id=job_db.id,
                            accuracy=feature_results.get("accuracy"),
                            issues=feature_results.get("issues"),
                        )
                        session.add(audit)
                        session.commit()

                        result = {
                            "id": job_db.id,
                            "status": "completed",
                            "accuracy": audit.accuracy,
                            "issues": audit.issues,
                            "completed_at": audit.completed_at.isoformat(),
                            "user_id": job_db.user_id,
                        }
                        
                        print(f"[Worker] Job {job_id} completed successfully.")
                        self._schedule_emit("job_update", result)
                        
        except Exception as e:
            print(f"[Worker] Job {job_id} failed with error: {e}")
            traceback.print_exc()

            # Update job status to failed
            try:
                with self.app.app_context():
                    with self.get_db_session() as session:
                        job_db = session.get(JobModel, job_id)
                        if job_db:
                            job_db.status = "failed"
                            job_db.error = str(e)
                            audit = AuditResult(job_id=job_db.id, error=str(e))
                            session.add(audit)
                            session.commit()

                            result = {
                                "id": job_db.id,
                                "status": job_db.status,
                                "error": job_db.error,
                                "completed_at": audit.completed_at.isoformat(),
                                "user_id": job_db.user_id,
                            }
                            self._schedule_emit("job_failed", result)
            except Exception as save_error:
                print(f"[Worker] Error saving failure state for job {job_id}: {save_error}")

    def _schedule_emit(self, event_name: str, data: dict):
        """
        Schedule socket emission to run on the main eventlet thread
        This ensures socket operations don't interfere with the executor thread
        """
        def emit_task():
            try:
                room = f"user_{data.get('user_id')}"
                self.socketio.emit(event_name, data, room=room)
                print(f"[Worker] Emitted {event_name} for user {data.get('user_id')}")
            except Exception as e:
                print(f"[Worker] Error emitting {event_name}: {e}")
        
        # Schedule the emit to run on the main eventlet thread
        eventlet.spawn_n(emit_task)

    def shutdown(self):
        """Clean shutdown of the worker"""
        print("[Worker] Shutting down thread pool executor...")
        self.executor.shutdown(wait=True)
        print("[Worker] Thread pool executor shut down complete.")

    def _emit_to_frontend(self, name: str, data: dict, namespace="/"):
        """Legacy method - kept for compatibility"""
        self._schedule_emit(name, data)