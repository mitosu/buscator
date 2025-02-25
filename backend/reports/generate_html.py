import os
from jinja2 import Environment, FileSystemLoader

def generate_html(data):
    """
    Genera un reporte en HTML con los datos de scraping.
    """
    output_folder = "reports/generated/"
    os.makedirs(output_folder, exist_ok=True)

    env = Environment(loader=FileSystemLoader("reports/templates"))
    template = env.get_template("report_template.html")

    for item in data:
        if item.get("screenshot") and os.path.exists(item["screenshot"]):
            filename = os.path.basename(item["screenshot"])
            item["screenshot"] = f"http://127.0.0.1:8000/screenshots/{filename}"  
        else:
            item["screenshot"] = None  # ❌ Indicar que no hay imagen disponible

    html_content = template.render(data=data)

    html_path = os.path.join(output_folder, "scraping_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_path