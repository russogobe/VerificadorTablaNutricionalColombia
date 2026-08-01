import os

import pytesseract
from pytesseract import Output

from core.constants import MICROS, NUTRIENTS, PER_PORTION_ALIASES, PORTION_ALIASES, SERVINGS_CONTAINER_ALIASES, TITLE_ALIASES
from core.image_ops import ImageProcessor
from core.models import LineBox, OCRCandidate, WordBox
from core.utils import norm

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD', 'tesseract')


class OCRExtractor:
    def __init__(self, lang: str = 'spa+eng'):
        self.lang = lang

    def image_to_lines(self, img, psm=6, image_id=None, region_name=None):
        cfg = f'--oem 1 --psm {psm}'
        data = pytesseract.image_to_data(img, lang=self.lang, config=cfg, output_type=Output.DICT)
        words = []
        for i, txt in enumerate(data.get('text', [])):
            txt = (txt or '').strip()
            try:
                conf = float(data.get('conf', ['-1'])[i])
            except Exception:
                conf = -1
            if not txt:
                continue
            x, y = int(data['left'][i]), int(data['top'][i])
            w, h = int(data['width'][i]), int(data['height'][i])
            words.append(WordBox(txt, x, y, x + w, y + h, conf))
        return self.group_lines(words, image_id=image_id, region_name=region_name)

    def group_lines(self, words, image_id=None, region_name=None):
        lines = []
        for p in words:
            cy = (p.y0 + p.y1) / 2
            alt = max(1, p.y1 - p.y0)
            sel = None
            for l in lines:
                lcy = (l.y0 + l.y1) / 2
                if abs(lcy - cy) <= max(8, alt * 0.75):
                    sel = l
                    break
            if sel is None:
                lines.append(LineBox('', p.x0, p.y0, p.x1, p.y1, [p], image_id=image_id, region_name=region_name))
            else:
                sel.words.append(p)
        for l in lines:
            l.words.sort(key=lambda z: z.x0)
            l.text = ' '.join(w.text for w in l.words)
            l.x0 = min(w.x0 for w in l.words)
            l.y0 = min(w.y0 for w in l.words)
            l.x1 = max(w.x1 for w in l.words)
            l.y1 = max(w.y1 for w in l.words)
            l.ocr_conf = sum(max(w.conf, 0) for w in l.words) / max(len(l.words), 1)
        lines.sort(key=lambda z: (z.y0 + z.y1) / 2)
        return lines

    def score_text(self, text: str) -> float:
        t = norm(text)
        score = 0.0
        score += 3 if any(a in t for a in TITLE_ALIASES) else 0
        score += 2 if any(a in t for a in PORTION_ALIASES) else 0
        score += 2 if any(a in t for a in SERVINGS_CONTAINER_ALIASES) else 0
        score += 1 if any(a in t for a in PER_PORTION_ALIASES) else 0
        score += sum(1 for n in NUTRIENTS if any(a in t for a in n['alias']))
        score += sum(1 for m in MICROS if any(a in t for a in m['alias'])) * 0.5
        return score

    def extract_region_candidates(self, img_bgr, image_id='img', region_name='unknown'):
        variants = ImageProcessor.preprocess_variants(img_bgr)
        candidates = []
        for variant_name, var in variants.items():
            for psm in [4, 6, 11]:
                lines = self.image_to_lines(var, psm=psm, image_id=image_id, region_name=region_name)
                text = '\n'.join(l.text for l in lines)
                score = self.score_text(text) + min(len(lines) / 10, 3)
                candidates.append(OCRCandidate(variant_name, psm, lines, text, score, region_name))
        return sorted(candidates, key=lambda x: x.score, reverse=True)
