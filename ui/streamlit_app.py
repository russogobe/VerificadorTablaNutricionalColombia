from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.constants import MAX_FOTOS
from core.image_ops import ImageProcessor
from core.nutrition_parser import NutritionParser
from core.ocr_engine import OCRExtractor
from core.reporting import generate_pdf
from core.seal_rules import SealComparator
from core.table_model import build_structured_rows, deduplicate_rows, split_primary_secondary
from core.utils import norm

FRONT_TERMS = ['EXCESO EN SODIO', 'EXCESO EN AZUCARES', 'EXCESO EN GRASAS SATURADAS', 'CONTIENE EDULCORANTES']


def main():
    st.set_page_config(page_title='Verificador nutricional final', page_icon='📋', layout='wide')
    st.title('📋 Verificador nutricional final')
    st.caption('Evalúa la tabla principal, separa bloque secundario y compara sellos esperados vs observados.')
    st.info('Se aceptan hasta 8 fotos. Debe incluirse al menos una foto de la tabla nutricional y, cuando aplique, una de los sellos frontales. Esta herramienta es de tamizaje y no constituye concepto oficial.')

    with st.sidebar:
        matrix = st.selectbox('Matriz', ['solido', 'liquido'], format_func=lambda x: 'Sólido por 100 g' if x == 'solido' else 'Líquido por 100 mL')
        debug = st.checkbox('Mostrar depuración OCR', value=True)

    uploads = st.file_uploader('Sube hasta 8 fotos', type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

    if st.button('Analizar', type='primary'):
        if not uploads:
            st.warning('Debes subir al menos una imagen.')
            st.stop()

        uploads = uploads[:MAX_FOTOS]
        extractor = OCRExtractor()
        all_lines = []
        debug_rows = []
        front_texts = []

        progress = st.progress(0, text='Iniciando análisis...')
        for i, file in enumerate(uploads, start=1):
            progress.progress((i - 1) / len(uploads), text=f'Procesando imagen {i}/{len(uploads)}...')
            img = ImageProcessor.from_bytes(file.read())
            regions = ImageProcessor.crop_table_regions(img)
            region_candidates = []

            for region_name, region_img in regions.items():
                cands = extractor.extract_region_candidates(region_img, image_id=file.name, region_name=region_name)
                if cands:
                    region_candidates.append(cands[0])

            if not region_candidates:
                debug_rows.append({'archivo': file.name, 'region': 'N/A', 'variante': 'N/A', 'psm': 'N/A', 'lineas_totales': 0, 'lineas_principales': 0, 'lineas_secundarias': 0, 'score': 0.0})
                continue

            best = sorted(region_candidates, key=lambda x: x.score, reverse=True)[0]
            lines = best.lines
            primary_block, secondary_block = split_primary_secondary(lines)
            all_lines.extend(primary_block.lines)
            all_lines.extend(secondary_block.lines)

            txt = '\n'.join(l.text for l in lines)
            if any(a in norm(txt) for a in FRONT_TERMS):
                front_texts.append(txt)

            debug_rows.append({
                'archivo': file.name,
                'region': best.region_name,
                'variante': best.variant,
                'psm': best.psm,
                'lineas_totales': len(lines),
                'lineas_principales': len(primary_block.lines),
                'lineas_secundarias': len(secondary_block.lines),
                'score': round(best.score, 2),
            })

        progress.progress(1.0, text='Análisis completado.')

        if not all_lines:
            st.error('No fue posible extraer líneas útiles desde las imágenes cargadas.')
            if debug_rows:
                st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)
            st.stop()

        primary_rows = deduplicate_rows(build_structured_rows(all_lines))
        parser = NutritionParser(primary_rows, all_lines)
        df, evidence_df, fields = parser.run()
        comparator = SealComparator(matrix, fields, front_texts)
        seals = comparator.compare()
        secondary_present = any('PERFIL NUTRICIONAL COMPLEMENTARIO' in norm(l.text) for l in all_lines)
        secondary_title = next((l.text for l in all_lines if 'PERFIL NUTRICIONAL COMPLEMENTARIO' in norm(l.text)), None)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader('Sellos / comparación')
            for s in seals:
                st.write(f'- {s}')
            st.write(f"Bloque secundario detectado: {secondary_title if secondary_present and secondary_title else 'NO'}")
        with c2:
            st.subheader('Resumen OCR por imagen')
            st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)

        st.subheader('Evaluación normativa preliminar de tabla principal')
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader('Evidencia por campo')
        st.dataframe(evidence_df, use_container_width=True, hide_index=True)

        pdf_data = generate_pdf(df, evidence_df, seals, secondary_present, secondary_title)
        st.download_button('Descargar informe PDF', data=pdf_data, file_name='informe_nutricional_final.pdf', mime='application/pdf')

        if debug:
            st.subheader('Depuración OCR')
            st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)

        st.markdown('---')
        st.markdown('La aplicación realiza cotejo preliminar con criterios parametrizados. No constituye concepto oficial.')


if __name__ == '__main__':
    main()
