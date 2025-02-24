import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, "Reporte de Scraping", ln=True, align="C")
        self.ln(10)  # Espaciado después del título

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 8, body)  # multi_cell permite manejar texto largo sin que se salga
        self.ln()

def generate_pdf(data):
    output_folder = "reports/generated/"
    os.makedirs(output_folder, exist_ok=True)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)  # Evitar que el contenido se salga del folio
    pdf.add_page()

    for item in data:
        pdf.chapter_title(f"Dominio: {item['domain']}")
        
        if item.get("description"):
            pdf.chapter_body(f"Descripción: {item['description']}")

        if item.get("screenshot"):
            screenshot_path = item["screenshot"]
            if os.path.exists(screenshot_path):
                # Ajustar la imagen para que no sea demasiado grande
                pdf.image(screenshot_path, x=15, w=180)  
                pdf.ln(10)  # Espaciado después de la imagen

    pdf_path = os.path.join(output_folder, "scraping_report.pdf")
    pdf.output(pdf_path)
    
    return pdf_path