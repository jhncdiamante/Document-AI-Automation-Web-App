from pdf2image import convert_from_path
import numpy as np
from backend.src.Documents.Document import Document
from backend.src.Documents.Page import Page
from backend.src.OCR.PaddleTextRecognition import PaddleOCRTextRecognition
from backend.src.Features.Classification import DocumentClassification
from backend.src.LLM.Models.Gemini import GeminiAI


pdf_path = r"D:\Whitmore_death_certificate_info_20250728-181158.pdf"

pages = convert_from_path(
    pdf_path=pdf_path,
    poppler_path=r"D:\libraries_and_such\poppler\poppler-25.07.0\Library\bin"
)

ocr = PaddleOCRTextRecognition()


gemini = GeminiAI()
document_classifier = DocumentClassification(model=gemini)

pages_read = []

#for page in []:
image_np = np.array(pages[3])
recognized_texts = ocr.get_recognized_texts(image_np)
page = Page(content=recognized_texts)
pages_read.append(page)

document = Document(pages=pages_read)


document_type = document_classifier.classify(document)

document.type = document_type
print(f"DOCUMENT TYPE -->>> {document.type}")


