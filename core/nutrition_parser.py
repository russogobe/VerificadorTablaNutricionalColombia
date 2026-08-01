import pandas as pd

from core.constants import MICROS, NUTRIENTS, PER_100_ALIASES, PER_PORTION_ALIASES, PORTION_ALIASES, SERVINGS_CONTAINER_ALIASES, SWEETENER_TERMS, TITLE_ALIASES
from core.utils import confidence_for_line, norm


class NutritionParser:
    def __init__(self, rows, primary_lines):
        self.rows = rows
        self.lines = primary_lines
        self.records = []
        self.evidence = []
        self.fields = {}
        self.used_row_ids = set()

    def reg(self, articulo, descripcion, estado, obs):
        self.records.append({'articulo': articulo, 'descripcion': descripcion, 'estado': estado, 'observacion': obs})

    def add_evidence(self, campo, row, valor=None, unidad=None):
        self.evidence.append({
            'campo': campo,
            'linea': row.raw_text,
            'confianza': row.confidence,
            'valor_100': row.value_100,
            'unidad_100': row.unit_100,
            'valor_porcion': row.value_portion,
            'unidad_porcion': row.unit_portion,
            'image_id': row.image_id,
            'region_name': row.region_name,
            'valor': valor,
            'unidad': unidad,
        })

    def parse_basic(self):
        text = ' '.join(norm(l.text) for l in self.lines)
        self.reg('Art. 28.1 Res. 810/2021', 'Título de la tabla', 'CUMPLE' if any(a in text for a in TITLE_ALIASES) else 'REVISAR', 'Validación global del bloque principal.')
        self.reg('Art. 12.4 Res. 810/2021', 'Tamaño de porción declarado', 'CUMPLE' if any(a in text for a in PORTION_ALIASES) else 'REVISAR', 'Validación global del bloque principal.')
        self.reg('Art. 10.4 Res. 810/2021', 'Porciones por envase', 'CUMPLE' if any(a in text for a in SERVINGS_CONTAINER_ALIASES) else 'REVISAR', 'Validación global del bloque principal.')
        self.reg('Art. 10.1 Res. 810/2021', 'Declaración por 100 g / 100 mL', 'CUMPLE' if any(a in text for a in PER_100_ALIASES) else 'REVISAR', 'Validación global del bloque principal.')
        self.reg('Art. 10.1 Res. 810/2021', 'Declaración por porción', 'CUMPLE' if any(a in text for a in PER_PORTION_ALIASES) else 'REVISAR', 'Validación global del bloque principal.')

    def assign_best_row(self, aliases, expected_unit):
        candidates = []
        for row in self.rows:
            if row.row_id in self.used_row_ids:
                continue
            score = confidence_for_line(row.normalized_name, aliases)
            if score < 55:
                continue
            unit_bonus = 15 if expected_unit in {row.unit_100, row.unit_portion} else -10
            value_bonus = 5 if row.value_100 is not None or row.value_portion is not None else 0
            total = score + unit_bonus + value_bonus + min(int(row.confidence / 10), 8)
            candidates.append((total, row))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_row = candidates[0]
        if best_score < 65:
            return None
        self.used_row_ids.add(best_row.row_id)
        return best_row

    def parse_nutrients(self):
        for n in NUTRIENTS:
            row = self.assign_best_row(n['alias'], n['unidad'])
            if not row:
                self.fields[n['k']] = None
                self.reg('Art. 28.4 Res. 810/2021', f"Declara {n['nombre']}", 'REVISAR', 'No asignado con confianza suficiente.')
                self.reg('Art. 28.4 Res. 810/2021', f"Unidad de {n['nombre']}", 'REVISAR', 'No asignado con confianza suficiente.')
                continue
            unidad = row.unit_100 or row.unit_portion
            valor = row.value_100 if row.value_100 is not None else row.value_portion
            self.fields[n['k']] = row
            self.add_evidence(n['k'], row, valor=valor, unidad=unidad)
            self.reg('Art. 28.4 Res. 810/2021', f"Declara {n['nombre']}", 'CUMPLE', row.raw_text)
            self.reg('Art. 28.4 Res. 810/2021', f"Unidad de {n['nombre']}", 'CUMPLE' if unidad else 'REVISAR', f'Valor={valor} Unidad={unidad}')

    def parse_micros(self):
        for m in MICROS:
            row = self.assign_best_row(m['alias'], m['unidad'])
            if not row:
                self.reg('Art. 28.3 Res. 810/2021', f"Micronutriente {m['nombre']}", 'REVISAR', 'No encontrado explícitamente.')
                continue
            unidad = row.unit_100 or row.unit_portion
            valor = row.value_100 if row.value_100 is not None else row.value_portion
            self.add_evidence(m['k'], row, valor=valor, unidad=unidad)
            self.reg('Art. 28.3 Res. 810/2021', f"Micronutriente {m['nombre']}", 'CUMPLE' if unidad else 'REVISAR', row.raw_text)

    def validate_order(self):
        present = [n['k'] for n in NUTRIENTS if self.fields.get(n['k'])]
        self.reg('Art. 28.4 Res. 810/2021', 'Orden de nutrientes', 'CUMPLE' if len(present) >= 4 else 'REVISAR', ', '.join(present) if present else 'Muy pocos nutrientes detectados.')

    def validate_consistency(self):
        azt = self.fields.get('aztot')
        aza = self.fields.get('azadd')
        v1 = azt.value_100 if azt and azt.value_100 is not None else None
        v2 = aza.value_100 if aza and aza.value_100 is not None else None
        if v1 is None or v2 is None:
            self.reg('Coherencia interna', 'Azúcares añadidos <= azúcares totales', 'NO APLICA', 'No fue posible comparar.')
        else:
            self.reg('Coherencia interna', 'Azúcares añadidos <= azúcares totales', 'CUMPLE' if v2 <= v1 else 'REVISAR', f'Añadidos={v2}; Totales={v1}')

    def detect_sweeteners(self):
        text = ' '.join(norm(l.text) for l in self.lines)
        self.fields['sweeteners'] = [t for t in SWEETENER_TERMS if t in text]

    def run(self):
        self.parse_basic()
        self.parse_nutrients()
        self.parse_micros()
        self.validate_order()
        self.validate_consistency()
        self.detect_sweeteners()
        return pd.DataFrame(self.records), pd.DataFrame(self.evidence), self.fields
