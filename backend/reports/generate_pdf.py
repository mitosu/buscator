import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, "Reporte de Scraping", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 8, body)
        self.ln()

def clean_text(text):
    """Reemplaza caracteres problemáticos con alternativas compatibles con FPDF"""
    if text:
        return text.replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    return text

def generate_pdf(data):
    output_folder = "reports/generated/"
    os.makedirs(output_folder, exist_ok=True)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for item in data:
        pdf.chapter_title(clean_text(f"Dominio: {item['domain']}"))

        if item.get("description"):
            pdf.chapter_body(clean_text(f"Descripción: {item['description']}"))

        if item.get("screenshot") and os.path.exists(item["screenshot"]):
            pdf.image(item["screenshot"], x=15, w=180)
            pdf.ln(10)  
        else:
            pdf.chapter_body(clean_text("ADVERTENCIA: No hay captura disponible para este dominio."))

    pdf_path = os.path.join(output_folder, "scraping_report.pdf")
    pdf.output(pdf_path)

    return pdf_path