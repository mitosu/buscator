import requests
import os
import re
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw
from requests.exceptions import RequestException

# Definir el proxy de Tor
TOR_PROXY = "socks5h://127.0.0.1:9050"

# User-Agent para simular un navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

def extract_real_url(possible_redirect):
    """
    Extrae la URL real desde un enlace de redirección.
    """
    print(f"Procesando URL: {possible_redirect}")  # DEBUG: Ver qué URLs estamos recibiendo

    parsed_url = urlparse(possible_redirect)
    
    if "redirect_url" in parse_qs(parsed_url.query):
        real_url = parse_qs(parsed_url.query).get("redirect_url", [""])[0]
        print(f"URL extraída: {real_url}")  # DEBUG: Ver la URL extraída
        return real_url if real_url.endswith(".onion") else None

    return possible_redirect if possible_redirect.endswith(".onion") else None

def capture_screenshot(url, title, output_folder="screenshots"):
    """
    Genera una imagen con el título de la página como vista previa.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((50, 150), title, fill=(0, 0, 0))
    
    screenshot_filename = url.replace("http://", "").replace("/", "_") + ".png"
    screenshot_path = os.path.join(output_folder, screenshot_filename)
    img.save(screenshot_path)

    return screenshot_path

def extract_title_description(html_text):
    """
    Extrae el título y la descripción del HTML usando expresiones regulares.
    """
    title_match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE)
    meta_match = re.search(r'<meta name="description" content="(.*?)"', html_text, re.IGNORECASE)
    
    title = title_match.group(1) if title_match else "No title"
    description = meta_match.group(1) if meta_match else "No description"
    
    return title.strip(), description.strip()

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

            title, description = extract_title_description(response.text)

            for tema in tematicas:
                if tema.lower() in title.lower() or tema.lower() in description.lower():
                    screenshot_path = capture_screenshot(domain, title)

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