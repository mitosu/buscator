import os
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

# Definir el proxy de Tor
TOR_PROXY = {"http": "socks5h://127.0.0.1:9050"}
# Fuente por defecto para dibujar el texto
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

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

def capture_screenshot(url, output_folder="screenshots", max_retries=3):
    """
    Descarga el HTML de una página Onion, extrae su contenido y lo renderiza como imagen.
    Incluye reintentos en caso de fallo.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    screenshot_filename = url.replace("http://", "").replace("/", "_") + ".png"
    screenshot_path = os.path.join(output_folder, screenshot_filename)

    attempt = 1
    while attempt <= max_retries:
        try:
            print(f"🔄 Intento {attempt}/{max_retries} para obtener HTML de {url}...")
            response = requests.get(url, proxies=TOR_PROXY, timeout=60)  # Aumentamos el timeout a 60s
            response.raise_for_status()

            # Extraer contenido relevante
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "Sin título"
            paragraphs = [p.text.strip() for p in soup.find_all("p")[:5]]  # Extraemos los primeros 5 párrafos
            text_content = f"{title}\n\n" + "\n".join(paragraphs)

            # Configurar imagen
            img_width, img_height = 800, 600
            img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Cargar fuente si está disponible
            try:
                font = ImageFont.truetype(FONT_PATH, 18)
            except IOError:
                font = ImageFont.load_default()

            # Dibujar texto en la imagen
            margin, y_offset = 20, 20
            for line in text_content.split("\n"):
                draw.text((margin, y_offset), line, fill=(0, 0, 0), font=font)
                y_offset += 25  # Espaciado entre líneas

            # Guardar imagen generada
            img.save(screenshot_path)
            print(f"✅ Imagen generada a partir del HTML: {screenshot_path}")
            return screenshot_path

        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout al intentar conectar con {url}. Reintentando...")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con {url}: {e}")
            break  # Si es un error crítico, no reintentamos

        attempt += 1
        time.sleep(5)  # Esperamos 5 segundos antes de reintentar

    print(f"❌ Fallo en la captura de {url} después de {max_retries} intentos.")
    return None  # No bloquea el reporte si falla