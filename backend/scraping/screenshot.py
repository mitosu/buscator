import os
import requests
import asyncio
from PIL import Image
from io import BytesIO
from html2image import Html2Image

# Definir el proxy de Tor para Pyppeteer
TOR_PROXY = "socks5h://127.0.0.1:9050"

def ensure_http(url, is_deepweb=False):
    """
    Asegura que la URL tenga 'http://'.
    - Para la Deep Web, solo se usa 'http://'.
    - Para la Surface Web, se usa 'https://' por defecto.
    """
    if is_deepweb:
        return "http://" + url.lstrip("http://").lstrip("https://")  # Solo HTTP para .onion
    
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url  # Surface Web usa HTTPS por defecto
    
    return url

def capture_screenshot(url, output_folder="screenshots"):
    """
    Genera una vista HTML del contenido del sitio web y la convierte en una imagen.
    """
    os.makedirs(output_folder, exist_ok=True)
    screenshot_filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".png"
    screenshot_path = os.path.join(output_folder, screenshot_filename)

    try:
        # Obtener el HTML de la página
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        page_html = response.text[:5000]  # Limitar a 5000 caracteres para evitar problemas de memoria
        
        # Verifica que el HTML no esté vacío
        if not page_html.strip():
            print(f"⚠️ Advertencia: {url} no devolvió contenido HTML. Se omite la captura.")
            return None

        # Construir HTML para renderizar
        html_content = f"""
        <html>
        <head><meta charset='utf-8'><style>body {{ font-family: Arial, sans-serif; }}</style></head>
        <body><h2>Vista previa de {url}</h2><hr>{page_html}</body>
        </html>
        """

        # Convertir el HTML en imagen
        hti = Html2Image()
        hti.screenshot(html_str=html_content, save_as=screenshot_filename, size=(800, 600))

        final_path = os.path.join(output_folder, screenshot_filename)
        os.rename(screenshot_filename, final_path)
        print(f"✅ Captura guardada: {final_path}")
        return final_path
    except Exception as e:
        print(f"❌ Error capturando {url}: {e}")
        return None