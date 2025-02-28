import os
import subprocess
import time
from bs4 import BeautifulSoup
import requests
from io import BytesIO
from PIL import Image
import logging
from scraping.screenshot_extend import capture_screenshot_with_tor_browser

# Definir proxy Tor
TOR_PROXY = "socks5h://127.0.0.1:9050"
TOR_CURL_CMD = "curl --socks5-hostname 127.0.0.1:9050 -L"

# Directorios
OUTPUT_FOLDER = "screenshots"
HTML_FOLDER = "temp_html"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(HTML_FOLDER, exist_ok=True)

def ensure_http(url, is_deepweb=False):
    """Asegura que la URL comience con http:// o https://"""
    if not url.startswith(('http://', 'https://')):
        # Para sitios .onion, siempre usar HTTP ya que no suelen tener HTTPS
        if is_deepweb and '.onion' in url:
            return f"http://{url}"
        else:
            return f"http://{url}"
    return url

def download_html(url):
    """
    Usa curl a través de Tor para obtener el HTML completo de una página Onion.
    """
    filename = os.path.join(HTML_FOLDER, url.replace("http://", "").replace("/", "_") + ".html")
    
    try:
        print(f"🔄 Descargando HTML de {url}...")
        subprocess.run(f"{TOR_CURL_CMD} {url} -o {filename}", shell=True, check=True)
        
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al descargar HTML: {e}")
        return None

def download_images(soup, url):
    """
    Descarga imágenes del HTML y actualiza las referencias en el HTML local.
    """
    domain = url.replace("http://", "").split("/")[0]
    local_images = {}
    
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if img_url and not img_url.startswith("data:image"):  # Evitar imágenes en base64
            try:
                if not img_url.startswith("http"):
                    img_url = f"http://{domain}{img_url}"  # Manejar rutas relativas
                
                response = requests.get(img_url, proxies={"http": TOR_PROXY, "https": TOR_PROXY}, timeout=10)
                response.raise_for_status()
                
                img_filename = os.path.join(OUTPUT_FOLDER, os.path.basename(img_url))
                with open(img_filename, "wb") as img_file:
                    img_file.write(response.content)
                
                local_images[img_url] = img_filename
                print(f"✅ Imagen descargada: {img_filename}")
            except Exception as e:
                print(f"⚠️ No se pudo descargar {img_url}: {e}")
    
    # Reemplazar URLs en el HTML
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if img_url in local_images:
            img["src"] = local_images[img_url]
    
    return soup

def render_html_to_image(html_content, output_path):
    """
    Usa wkhtmltoimage para convertir HTML en una imagen PNG.
    """
    temp_html_path = os.path.join(HTML_FOLDER, "temp.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    try:
        print(f"📸 Generando imagen desde HTML...")
        subprocess.run(f"wkhtmltoimage {temp_html_path} {output_path}", shell=True, check=True)
        print(f"✅ Screenshot guardado en {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la conversión de HTML a imagen: {e}")
        return None
    
def capture_screenshot(url, output_folder="screenshots"):
    """
    Captura una screenshot de una URL.
    
    Args:
        url: URL a capturar
        output_folder: Carpeta donde guardar la captura
        
    Returns:
        str: Ruta al archivo de screenshot
    """
    # Crear directorio si no existe
    os.makedirs(output_folder, exist_ok=True)
    
    # Procesar URL para obtener un nombre de archivo válido
    domain = url.replace('http://', '').replace('https://', '').split('/')[0]
    output_path = os.path.join(OUTPUT_FOLDER, f"{domain}.png")
    
    # Verificar si es un sitio .onion
    if '.onion' in url:
        # Usar implementación Tor Browser para sitios .onion
        return capture_screenshot_with_tor_browser(url, output_path)
    else:
        # Aquí podrías mantener tu implementación actual para sitios normales
        # O implementar otro método para capturar sitios no .onion
        pass
    
    return output_path

#def capture_screenshot(url):
#    """
#    Captura un "screenshot" de una página Onion renderizando su HTML.
#    """
#    html_content = download_html(url)
#    if not html_content:
#        return None
#    
#    soup = BeautifulSoup(html_content, "html.parser")
#    soup = download_images(soup, url)  # Descargar e incrustar imágenes
#    
#    output_path = os.path.join(OUTPUT_FOLDER, url.replace("http://", "").replace("/", "_") + ".png")
#    return render_html_to_image(str(soup), output_path)