from pdf2image import convert_from_bytes
from PIL import Image


def convert_pdf_to_images(pdf: bytes) -> list[Image.Image]:
    return convert_from_bytes(pdf)
