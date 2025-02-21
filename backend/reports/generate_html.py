import os  # ← ¡Esta línea soluciona el error!
from jinja2 import Environment, FileSystemLoader

def generate_html(data):
    """
    Genera un reporte en HTML con los datos de scraping.
    """
    output_folder = "reports/generated/"
    os.makedirs(output_folder, exist_ok=True)  # ← Ahora `os` está correctamente definido

    env = Environment(loader=FileSystemLoader("reports/templates"))
    template = env.get_template("report_template.html")

    # Convertir las rutas de imágenes para que sean accesibles
    for item in data:
        if item.get("screenshot"):
            filename = os.path.basename(item["screenshot"])
            item["screenshot"] = f"http://127.0.0.1:8000/screenshots/{filename}"  # Opción con FastAPI

    html_content = template.render(data=data)
    
    html_path = os.path.join(output_folder, "scraping_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_path