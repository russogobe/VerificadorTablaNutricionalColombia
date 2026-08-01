import re
import unicodedata
from typing import List

try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


def norm(texto: str) -> str:
    if not texto:
        return ''
    t = unicodedata.normalize('NFD', str(texto))
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = t.upper()
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def parse_number(token: str):
    if token is None:
        return None
    t = str(token).replace(',', '.')
    t = re.sub(r'[^0-9\.]', '', t)
    if not t:
        return None
    if t.count('.') > 1:
        p = t.find('.')
        t = t[: p + 1] + t[p + 1 :].replace('.', '')
    return safe_float(t)


def confidence_for_line(line: str, aliases: List[str]) -> int:
    t = norm(line)
    normalized_aliases = [norm(a) for a in aliases]
    exact = max((100 if a in t else 0) for a in normalized_aliases) if normalized_aliases else 0
    if exact:
        return exact
    if fuzz is None:
        return 0
    return max(fuzz.partial_ratio(t, a) for a in normalized_aliases) if normalized_aliases else 0


def parse_values_from_text(line: str):
    t = norm(line)
    t = t.replace('M9', 'MG').replace('OG', '0 G').replace('O G', '0 G')
    t = re.sub(r'00G', '0.0 G', t)
    t = re.sub(r'009', '0.0 G', t)
    t = re.sub(r'00MG', '0.0 MG', t)
    vals = re.findall(r'([0-9]+(?:[\.,][0-9]+)?)\s*(KCAL|MG|G)', t)
    return [(parse_number(v), u) for v, u in vals]
