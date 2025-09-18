from src.Documents.Page import Page
from src.OCR.ITextRecognition import ITextRecognition
from paddleocr import PaddleOCR

from src.OCR.ITextRecognition import ITextRecognition
from paddleocr import PaddleOCR
from numpy.typing import NDArray
from typing_extensions import Tuple
  # accurate, multi-lang
class PaddleOCRTextRecognition(ITextRecognition):
    def __init__(self, lang: str = 'en', use_textline_orientation: bool = True, text_detection_model_name="PP-OCRv5_server_det", 
    text_recognition_model_name="PP-OCRv5_server_rec"):
        
        self._model = PaddleOCR(use_textline_orientation=use_textline_orientation, lang=lang, text_detection_model_name=text_detection_model_name, text_recognition_model_name=text_recognition_model_name) 

    def __str__(self):
        return "PaddleOCRTextRecognition"

    def get_recognized_texts(self, page: NDArray) -> list[Tuple]:
        result = self._model.predict(page)
        if result:
            return list(zip(result[0]["rec_texts"], result[0]["rec_scores"]))
        raise ValueError("No recognized texts generated.")

    
    def set_model(self, **kwargs) -> None:
        # change or add model instance specifications e.g. lang=en -> ch
        self._model = PaddleOCR(**kwargs)
