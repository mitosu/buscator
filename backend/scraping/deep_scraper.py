import requests
import os
import re
import asyncio
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw
from requests.exceptions import RequestException
from scraping.screenshot import capture_screenshot, ensure_http
from urllib.parse import urlparse, parse_qs
from utils.detect_technologies import detect_technologies
from bs4 import BeautifulSoup

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
    Extrae la URL real desde un enlace de redirección y la limpia para obtener solo el dominio principal .onion.
    """
    print(f"Procesando URL: {possible_redirect}")  # DEBUG

    parsed_url = urlparse(possible_redirect)
    
    # Verifica si la URL contiene un parámetro "redirect_url="
    if "redirect_url" in parse_qs(parsed_url.query):
        real_url = parse_qs(parsed_url.query).get("redirect_url", [""])[0]
    else:
        real_url = possible_redirect
    
    # Extraer solo la parte base del dominio .onion (sin rutas o parámetros)
    if ".onion" in real_url:
        onion_index = real_url.find(".onion") + 6  # 6 es la longitud de ".onion"
        clean_url = real_url[:onion_index]  # Obtener solo hasta ".onion"
        print(f"URL extraída y limpiada: {clean_url}")  # DEBUG
        return clean_url
    
    return None

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

async def scrape_deep(domains, tematicas):
    """
    Realiza scraping en sitios de la Deep Web utilizando el proxy Tor y filtra según las temáticas.
    """
    results = []
    proxies = {"http": "socks5h://127.0.0.1:9050"}  # Solo HTTP para la Deep Web

    for domain in domains:
        domain = extract_real_url(domain)  # Extraer URL real de redirecciones

        if not domain:
            print(f"Saltando {domain}: No es un dominio .onion válido")
            continue

        # ✅ Asegurar que la URL tenga "http://"
        domain = ensure_http(domain, is_deepweb=True)

        try:
            response = requests.get(domain, proxies=proxies, timeout=20)
            response.raise_for_status()

            title, description, meta_keywords = extract_title_description(response.text)

            # Detectar tecnologías en el HTML
            technologies = detect_technologies(response.text)

            # **Filtrar por palabras prohibidas en meta keywords**
            if contains_forbidden_keywords(meta_keywords):
                print(f"❌ Dominio bloqueado por contenido prohibido: {domain}")
                continue

            # ✅ Filtrar solo si el título o la descripción coinciden con las temáticas
            if any(tema.lower() in title.lower() or tema.lower() in description.lower() for tema in tematicas):
                try:
                    screenshot_path = capture_screenshot(domain)
                except Exception as e:
                    print(f"⚠️ Error al capturar screenshot de {domain}: {e}")
                    screenshot_path = None  # Permitir que el proceso continúe

                results.append({
                    "domain": domain,
                    "title": title,
                    "description": description,
                    "products": meta_keywords,
                    "technologies": technologies,
                    "screenshot": screenshot_path
                })

        except Exception as e:
            print(f"❌ Error general en {domain}: {e}")

    print(f"✅ Scraping Deep Web completado: {len(results)} resultados encontrados.")
    return results