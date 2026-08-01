import io

import cv2
import numpy as np
from PIL import Image


class ImageProcessor:
    @staticmethod
    def from_bytes(data: bytes) -> np.ndarray:
        img = Image.open(io.BytesIO(data)).convert('RGB')
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    @staticmethod
    def resize_up(img: np.ndarray, scale: float = 2.5) -> np.ndarray:
        return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    @staticmethod
    def preprocess_variants(img_bgr: np.ndarray):
        up = ImageProcessor.resize_up(img_bgr, 2.5)
        gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        sharp = cv2.filter2D(clahe, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
        adapt = cv2.adaptiveThreshold(clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
        otsu = cv2.threshold(sharp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return {'sharp': sharp, 'adapt': adapt, 'clahe': clahe, 'otsu': otsu}

    @staticmethod
    def crop_table_regions(img_bgr: np.ndarray):
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]
        th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        rows = cv2.morphologyEx(th, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5)), iterations=2)
        cols = cv2.morphologyEx(th, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 25)), iterations=2)
        combined = cv2.bitwise_or(rows, cols)
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            if cw * ch >= 0.015 * h * w:
                boxes.append((x, y, cw, ch))
        boxes = sorted(boxes, key=lambda b: b[1])
        regions = {'full': img_bgr}
        pad = 10
        if boxes:
            x, y, cw, ch = boxes[0]
            regions['primary'] = img_bgr[max(0, y - pad): min(h, y + ch + pad), max(0, x - pad): min(w, x + cw + pad)]
            if len(boxes) > 1:
                x2, y2, cw2, ch2 = boxes[1]
                if y2 > y + ch * 0.8:
                    regions['secondary'] = img_bgr[max(0, y2 - pad): min(h, y2 + ch2 + pad), max(0, x2 - pad): min(w, x2 + cw2 + pad)]
        return regions
