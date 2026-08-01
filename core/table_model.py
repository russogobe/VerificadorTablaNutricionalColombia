from typing import Dict, List

from core.constants import SECONDARY_HEADER_ALIASES, SECONDARY_ROW_MARKERS
from core.models import DetectedBlock, LineBox, StructuredRow
from core.utils import norm, parse_values_from_text


def split_primary_secondary(lines: List[LineBox]):
    if not lines:
        return DetectedBlock('primary', None, [], 0.0), DetectedBlock('secondary', None, [], 0.0)
    sorted_lines = sorted(lines, key=lambda z: (z.y0 + z.y1) / 2)
    title_idx = None
    for i, l in enumerate(sorted_lines):
        t = norm(l.text)
        if any(a in t for a in SECONDARY_HEADER_ALIASES):
            title_idx = i
            break
    if title_idx is None:
        marker_hits = [i for i, l in enumerate(sorted_lines) if any(m in norm(l.text) for m in SECONDARY_ROW_MARKERS)]
        if len(marker_hits) >= 2:
            title_idx = marker_hits[0]
    if title_idx is None:
        return DetectedBlock('primary', None, sorted_lines, 0.9 if sorted_lines else 0.0), DetectedBlock('secondary', None, [], 0.0)
    primary = sorted_lines[:title_idx]
    secondary = sorted_lines[title_idx:]
    title = sorted_lines[title_idx].text
    return DetectedBlock('primary', None, primary, 0.9 if primary else 0.0), DetectedBlock('secondary', title, secondary, 0.9 if secondary else 0.0)


def build_structured_rows(lines: List[LineBox]) -> List[StructuredRow]:
    rows = []
    for idx, line in enumerate(lines):
        vals = parse_values_from_text(line.text)
        row = StructuredRow(
            row_id=f'row_{idx}',
            raw_text=line.text,
            normalized_name=norm(line.text),
            image_id=line.image_id or 'unknown',
            region_name=line.region_name or 'unknown',
            y_center=(line.y0 + line.y1) / 2,
            confidence=line.ocr_conf,
            source_line=line,
        )
        if len(vals) >= 1:
            row.value_100, row.unit_100 = vals[0]
        if len(vals) >= 2:
            row.value_portion, row.unit_portion = vals[1]
        rows.append(row)
    return rows


def deduplicate_rows(rows: List[StructuredRow]) -> List[StructuredRow]:
    best: Dict[str, StructuredRow] = {}
    for r in rows:
        key = norm(r.raw_text)
        if key not in best or r.confidence > best[key].confidence:
            best[key] = r
    return list(best.values())
