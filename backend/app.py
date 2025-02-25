from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from scraping.surface_scraper import scrape_surface
from scraping.deep_scraper import scrape_deep
from reports.generate_pdf import generate_pdf
from reports.generate_html import generate_html
from utils.search_domains import get_surface_domains, get_deepweb_domains
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes (puedes restringirlo a ['http://127.0.0.1:5173'] si prefieres)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.get("/download-report/")
async def download_report(report_type: str = Query(...)):
    """
    Permite descargar reportes PDF o HTML.
    """
    report_folder = "reports/generated/"
    file_name = f"scraping_report.{report_type}"
    file_path = os.path.join(report_folder, file_name)

    # Verificar si el archivo existe antes de devolverlo
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "El reporte solicitado no existe"}, status_code=404)

    return FileResponse(file_path, filename=file_name, media_type="application/octet-stream")

@app.post("/start-scraping/")
async def start_scraping(data: dict):
    """
    Recibe datos de la UI y ejecuta el scraping.
    """
    tematicas = data.get("tematicas", [])
    network = data.get("network", "")
    domains = data.get("domains", [])

    if not tematicas or not network:
        return {"error": "Faltan datos obligatorios"}

    if not domains:
        if network == "surface":
            domains = get_surface_domains(tematicas)
        elif network == "deep":
            domains = get_deepweb_domains(tematicas)

    if not domains:
        return {"error": "No se encontraron dominios para la búsqueda"}

    results = []
    print(f"Dominios obtenidos: {domains}")
    if network == "surface":
        results = scrape_surface(domains, tematicas)
    elif network == "deep":
        results = await scrape_deep(domains, tematicas)

    print("Capturas de pantalla generadas:")
    for r in results:
        print(r.get("screenshot", "No captura"))

    pdf_path = generate_pdf(results)
    html_path = generate_html(results)

    return {
        "message": "Scraping finalizado",
        "pdf_report": pdf_path,
        "html_report": html_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)