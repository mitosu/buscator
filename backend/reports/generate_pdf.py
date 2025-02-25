import os
from fpdf import FPDF
import unicodedata

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, "Reporte de Scraping", ln=True, align="C")
        self.ln(10)  # Espaciado después del título

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, self.clean_text(title), ln=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 8, self.clean_text(body))  # `multi_cell` maneja texto largo sin que se salga
        self.ln()

    def clean_text(self, text):
        """
        Convierte el texto a ASCII eliminando caracteres no soportados por FPDF.
        """
        if not text:
            return "Texto no disponible"
        
        # Normalizar el texto eliminando caracteres Unicode que no son compatibles con Latin-1
        return ''.join(
            c for c in unicodedata.normalize("NFKD", text) if ord(c) < 128
        )

def generate_pdf(data):
    output_folder = "reports/generated/"
    os.makedirs(output_folder, exist_ok=True)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)  # Evitar que el contenido se salga del folio
    pdf.add_page()

    for item in data:
        pdf.chapter_title(item.get("domain", "Dominio Desconocido"))
        
        if item.get("description"):
            pdf.chapter_body(f"Descripción: {item['description']}")

        if item.get("screenshot"):
            screenshot_path = item["screenshot"]
            if os.path.exists(screenshot_path):
                pdf.image(screenshot_path, x=15, w=180)  
                pdf.ln(10)  # Espaciado después de la imagen
        
        if item.get("technologies"):
            pdf.chapter_body(f"Tecnologías usadas: {', '.join(item['technologies'])}")

    pdf_path = os.path.join(output_folder, "scraping_report.pdf")
    pdf.output(pdf_path)

    return pdf_path