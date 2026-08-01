from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _df_to_table_data(df, max_rows=50):
    if df is None or df.empty:
        return [['Sin datos']]
    headers = list(df.columns)
    rows = df.head(max_rows).fillna('').astype(str).values.tolist()
    return [headers] + rows


def generate_pdf(df_eval, evidence_df, seals, secondary_present, secondary_title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('Informe nutricional preliminar', styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f'Sellos: {" | ".join(seals) if seals else "Sin hallazgos"}', styles['BodyText']))
    story.append(Paragraph(f'Bloque secundario detectado: {"Sí" if secondary_present else "No"}', styles['BodyText']))
    if secondary_title:
        story.append(Paragraph(f'Título bloque secundario: {secondary_title}', styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('Evaluación normativa preliminar', styles['Heading2']))
    t1 = Table(_df_to_table_data(df_eval), repeatRows=1)
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9edf7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 12))

    story.append(Paragraph('Evidencia por campo', styles['Heading2']))
    t2 = Table(_df_to_table_data(evidence_df), repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fcf8e3')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]))
    story.append(t2)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
