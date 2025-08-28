from paddleocr import PaddleOCR

img = r"D:\Web App Data Audit\Frontend\output\1756212551_9310_preprocessed_img.png"

ocr = PaddleOCR(
    use_doc_orientation_classify=True,      # deskew/rotate whole page if needed
    use_doc_unwarping=False,                # enable if you scan curved docs
    use_textline_orientation=True,          # rotate individual lines
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec"  # accurate, multi-lang
)
result = ocr.predict(img)
for res in result:
    res.print()                  # inspect
    res.save_to_img("output")    # visualize boxes + texts
    res.save_to_json("output")   # structured output
