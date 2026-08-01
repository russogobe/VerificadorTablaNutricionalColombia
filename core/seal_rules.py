from core.constants import FRONT_SEAL_TERMS
from core.utils import norm


class SealComparator:
    def __init__(self, matrix, fields, front_texts):
        self.matrix = matrix
        self.fields = fields
        self.front_texts = front_texts

    def get_value(self, key):
        obj = self.fields.get(key)
        if obj is None:
            return None
        return obj.value_100 if getattr(obj, 'value_100', None) is not None else getattr(obj, 'value_portion', None)

    def expected(self):
        exp = []
        sodio = self.get_value('sodio')
        azucar = self.get_value('azadd') or self.get_value('aztot')
        sat = self.get_value('saturada')
        if sodio is not None and sodio >= (300 if self.matrix == 'solido' else 100):
            exp.append('sodio')
        if azucar is not None and azucar >= (10 if self.matrix == 'solido' else 5):
            exp.append('azucar')
        if sat is not None and sat >= (4 if self.matrix == 'solido' else 3):
            exp.append('grasa')
        if self.fields.get('sweeteners'):
            exp.append('edulcorante')
        return exp

    def observed(self):
        t = norm(' '.join(self.front_texts))
        obs = []
        for key, aliases in FRONT_SEAL_TERMS.items():
            if any(a in t for a in aliases):
                obs.append(key)
        return obs

    def compare(self):
        exp = self.expected()
        obs = self.observed()
        out = []
        if not exp and not obs:
            return ['NO CORRESPONDEN SELLOS FRONTALES SEGUN LA TABLA PRINCIPAL.']
        for s in exp:
            out.append(f'CORRESPONDE Y SE OBSERVA: {s.upper()}' if s in obs else f'CORRESPONDE PERO NO SE OBSERVA: {s.upper()}')
        for s in obs:
            if s not in exp:
                out.append(f'SE OBSERVA PERO NO CORRESPONDE SEGUN TABLA PRINCIPAL: {s.upper()}')
        return out
