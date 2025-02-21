from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraping.surface_scraper import scrape_surface
from scraping.deep_scraper import scrape_deep
from scraping.screenshot import capture_screenshot
from reports.generate_pdf import generate_pdf
from reports.generate_html import generate_html
from utils.search_domains import get_surface_domains, get_deepweb_domains
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes (puedes restringirlo a ['http://127.0.0.1:5173'] si prefieres)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")
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
    if network == "surface":
        results = scrape_surface(domains, tematicas)
    elif network == "deep":
        results = scrape_deep(domains, tematicas)

    # Capturar capturas de pantalla (sin dependencias del SO)
    for result in results:
        result["screenshot"] = capture_screenshot(result["domain"])

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