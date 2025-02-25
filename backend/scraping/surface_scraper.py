import requests
from bs4 import BeautifulSoup
from utils.detect_technologies import detect_technologies

def ensure_http(url):
    """
    Asegura que la URL tenga 'http://' o 'https://'.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url  # Suponemos HTTPS por defecto
    return url

def scrape_surface(domains, tematicas):
    """
    Realiza scraping en sitios de la Surface Web.
    """
    results = []
    session = requests.Session()  # Usamos una sesión para simular navegación

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Referer": "https://www.google.com",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }

    for domain in domains:
        domain = ensure_http(domain)  # Agregar esquema si falta
        try:
            response = session.get(domain, timeout=10, headers=headers)
            response.raise_for_status()  # Verifica si hay errores en la respuesta

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No title"
            description_tag = soup.find("meta", attrs={"name": "description"})
            description = description_tag["content"] if description_tag else "No description"

            for tema in tematicas:
                if tema.lower() in title.lower() or tema.lower() in description.lower():
                    results.append({
                        "domain": domain,
                        "title": title,
                        "description": description
                    })
                    break

        except requests.exceptions.HTTPError as e:
            print(f"Error en {domain}: {e}")
        except Exception as e:
            print(f"Error general en {domain}: {e}")

    print(f"Scraping completado: {len(results)} resultados encontrados.")
    return results