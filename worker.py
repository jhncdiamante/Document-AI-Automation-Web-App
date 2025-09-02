from pdf2image import convert_from_path
import numpy as np
from backend.src.Documents.Page import Page
from backend.src.OCR.PaddleTextRecognition import PaddleOCRTextRecognition
from backend.src.Features.Classification import DocumentClassification
from backend.src.LLM.Models.Gemini import GeminiAI
from backend.src.Documents.DocumentFormatting.DeathCertificate import DeathCertificate
from backend.src.Documents.DocumentFormatting.DRW import DeathRegistrationWorksheet
from backend.src.Features.Formatter import DocumentFormatter
from backend.src.Features.Comparison import DocumentComparison
from backend.src.Features.General import GeneralAudit
import json
from datetime import datetime

from backend.src.Data.Redis import redis_conn

gemini = GeminiAI()

formatter = DocumentFormatter(gemini)
comparer = DocumentComparison(gemini)
classifier = DocumentClassification(gemini)
general_audit = GeneralAudit(gemini)

ocr = '''PaddleOCRTextRecognition()'''


def _convert_pdf_pages_to_images(pdf_path):
    return convert_from_path(
            pdf_path=pdf_path,
            poppler_path=r"D:\libraries_and_such\poppler\poppler-25.07.0\Library\bin"
        )

def _standardize_document(uploaded_files):
    documents = []

    for file in uploaded_files:
        pages = _convert_pdf_pages_to_images(file)

        pages_read = []

        for page in pages:
            image_np = np.array(page)
            recognized_texts = ocr.get_recognized_texts(image_np)
            page = Page(content=recognized_texts)
            pages_read.append(page)

        document_type = classifier.classify(pages_read).strip().lower()

        if document_type == "death registration worksheet":
            document = DeathRegistrationWorksheet(pages=pages_read)
        elif document_type == "certificate of death":
            document = DeathCertificate(pages=pages_read)
        else:
            raise ValueError(f"Could not determine document type {document_type}")

        formatter.format_document(document)
        documents.append(document)
    return documents


def process_job(job_id: str, job_data: dict):
    feature = job_data.get("feature")
    uploaded_files = job_data.get("saved_files")

    documents = _standardize_document(uploaded_files)

    if feature == "General":
        feature_results = general_audit.audit(documents[0])
    elif feature == "Comparison":
        feature_results = comparer.compare(document1=documents[0], document2=documents[1])

    # publish to Redis so Flask sees it
    result = {
        "id": job_id,
        "status": "completed",
        "accuracy": feature_results.get("accuracy"),
        "issues": feature_results.get("issues"),
        "completed_at": datetime.now()
    }
    redis_conn.publish("job_updates", json.dumps(result))

    return result



    




