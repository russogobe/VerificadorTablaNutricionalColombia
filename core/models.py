from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WordBox:
    text: str
    x0: int
    y0: int
    x1: int
    y1: int
    conf: float = 0.0


@dataclass
class LineBox:
    text: str
    x0: int
    y0: int
    x1: int
    y1: int
    words: List[WordBox] = field(default_factory=list)
    image_id: Optional[str] = None
    region_name: Optional[str] = None
    ocr_conf: float = 0.0


@dataclass
class OCRCandidate:
    variant: str
    psm: int
    lines: List[LineBox]
    text: str
    score: float
    region_name: str


@dataclass
class DetectedBlock:
    block_type: str
    title: Optional[str]
    lines: List[LineBox]
    confidence: float = 0.0


@dataclass
class StructuredRow:
    row_id: str
    raw_text: str
    normalized_name: str
    image_id: str
    region_name: str
    y_center: float
    value_100: Optional[float] = None
    unit_100: Optional[str] = None
    value_portion: Optional[float] = None
    unit_portion: Optional[str] = None
    confidence: float = 0.0
    source_line: Optional[LineBox] = None
    meta: Dict = field(default_factory=dict)
