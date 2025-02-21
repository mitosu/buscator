from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_pdf(data):
    """
    Genera un reporte en PDF con los datos de scraping.
    """
    output_folder = "reports/generated/"
    os.makedirs(output_folder, exist_ok=True)

    pdf_path = os.path.join(output_folder, "scraping_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Reporte de Scraping")

    y = 730  # Posición inicial en la página

    for item in data:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Dominio: {item['domain']}")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Title: {item['title']}")
        y -= 15
        c.drawString(50, y, f"Description: {item['description']}")
        y -= 15

        if "screenshot" in item and item["screenshot"]:
            screenshot_path = item["screenshot"]
            try:
                c.drawImage(screenshot_path, 50, y - 100, width=200, height=150)
                y -= 170
            except Exception as e:
                print(f"Error al agregar imagen {screenshot_path}: {e}")

        y -= 20  # Espaciado entre registros

        if y < 100:  # Si no hay más espacio, agregar una nueva página
            c.showPage()
            y = 750

    c.save()
    return pdf_path