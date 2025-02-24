import requests
import os
import re
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw
from requests.exceptions import RequestException
from scraping.screenshot import capture_screenshot

# Definir el proxy de Tor
TOR_PROXY = "socks5h://127.0.0.1:9050"

# User-Agent para simular un navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

# Lista de palabras clave prohibidas en meta keywords
FORBIDDEN_KEYWORDS = [
    "porn", "porno", "girls", "boys", "moms", "dads", "daddy", "hardcore", "rape", "brutal", "cp", "teens", "hot", "sex"
]

# Palabras que contengan "pedo"
PEDO_PATTERN = re.compile(r".*pedo.*", re.IGNORECASE)

def extract_real_url(possible_redirect):
    """
    Extrae la URL real desde un enlace de redirección.
    """
    parsed_url = urlparse(possible_redirect)
    
    if "redirect_url" in parse_qs(parsed_url.query):
        real_url = parse_qs(parsed_url.query).get("redirect_url", [""])[0]
        return real_url if real_url.endswith(".onion") else None

    return possible_redirect if possible_redirect.endswith(".onion") else None

def extract_title_description(html_text):
    """
    Extrae el título, la descripción y las meta keywords del HTML usando expresiones regulares.
    """
    title_match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE)
    meta_desc_match = re.search(r'<meta name="description" content="(.*?)"', html_text, re.IGNORECASE)
    meta_keywords_match = re.search(r'<meta name="keywords" content="(.*?)"', html_text, re.IGNORECASE)
    
    title = title_match.group(1) if title_match else "No title"
    description = meta_desc_match.group(1) if meta_desc_match else "No description"
    meta_keywords = meta_keywords_match.group(1) if meta_keywords_match else ""
    
    return title.strip(), description.strip(), meta_keywords.strip()

def contains_forbidden_keywords(meta_keywords):
    """
    Verifica si las meta keywords contienen palabras prohibidas.
    """
    keywords_lower = meta_keywords.lower()
    if any(word in keywords_lower for word in FORBIDDEN_KEYWORDS) or PEDO_PATTERN.search(keywords_lower):
        return True
    return False

def scrape_deep(domains, tematicas):
    """
    Realiza scraping en sitios de la Deep Web.
    """
    results = []
    proxies = {"http": TOR_PROXY, "https": TOR_PROXY}

    for domain in domains:
        domain = extract_real_url(domain)  # Extraer URL .onion real

        # Si no se obtiene una URL .onion válida, saltar
        if not domain:
            print(f"Saltando {domain}: No es un dominio .onion válido")
            continue

        try:
            response = requests.get(domain, proxies=proxies, timeout=15, headers=HEADERS)
            response.raise_for_status()

            title, description, meta_keywords = extract_title_description(response.text)

            # Filtrar dominios que contengan palabras prohibidas en meta keywords
            if contains_forbidden_keywords(meta_keywords):
                print(f"Saltando {domain}: Contiene palabras prohibidas en meta keywords")
                continue

            for tema in tematicas:
                if tema.lower() in title.lower() or tema.lower() in description.lower():
                    screenshot_path = capture_screenshot(domain, output_folder="screenshots", is_deepweb=True)

                    results.append({
                        "domain": domain,
                        "title": title,
                        "description": description,
                        "screenshot": screenshot_path
                    })
                    break  # Detener la búsqueda si encontramos una coincidencia

        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP en {domain}: {e}")
        except requests.exceptions.ConnectionError:
            print(f"Error de conexión en {domain}: No se pudo conectar.")
        except requests.exceptions.Timeout:
            print(f"Timeout en {domain}: La solicitud tomó demasiado tiempo.")
        except Exception as e:
            print(f"Error general en {domain}: {e}")

    print(f"Scraping Deep Web completado: {len(results)} resultados encontrados.")
    return results