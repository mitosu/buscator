import os
import requests
from PIL import Image, ImageDraw
from io import BytesIO

# Definir el proxy de Tor para capturas en la Deep Web
TOR_PROXY = "socks5h://127.0.0.1:9050"

def ensure_http(url, is_deepweb=False):
    """
    Asegura que la URL tenga 'http://' o 'https://'.
    Para la Deep Web, se mantiene solo 'http://'.
    """
    if is_deepweb:
        return "http://" + url.lstrip("http://").lstrip("https://")
    
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url  # Asumimos HTTPS por defecto para Surface Web
    
    return url

def capture_screenshot(url, output_folder="screenshots", is_deepweb=False):
    """
    Captura una imagen de la página principal del sitio web.
    Para la Surface Web, usa Thum.io.
    Para la Deep Web, usa requests con proxy Tor y Pillow.
    """
    url = ensure_http(url, is_deepweb)  # Asegurar que la URL es válida
    os.makedirs(output_folder, exist_ok=True)

    if is_deepweb:
        # Captura de pantalla simulada para la Deep Web
        screenshot_filename = url.replace("http://", "").replace("/", "_") + ".png"
        screenshot_path = os.path.join(output_folder, screenshot_filename)

        try:
            response = requests.get(url, proxies={"http": TOR_PROXY, "https": TOR_PROXY}, timeout=15)
            if response.status_code == 200:
                img = Image.new("RGB", (800, 400), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                draw.text((50, 150), url, fill=(0, 0, 0))
                img.save(screenshot_path)
                print(f"Captura simulada guardada: {screenshot_path}")
                return screenshot_path
        except Exception as e:
            print(f"Error capturando {url} en la Deep Web: {e}")
        return None
    
    # API de Thum.io para capturas de pantalla en Surface Web
    screenshot_url = f"https://image.thum.io/get/fullpage/{url}"
    try:
        response = requests.get(screenshot_url, timeout=15)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            screenshot_filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".png"
            screenshot_path = os.path.join(output_folder, screenshot_filename)
            img.save(screenshot_path)

            print(f"Captura guardada: {screenshot_path}")
            return screenshot_path
        else:
            print(f"No se pudo capturar la imagen de {url}. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error capturando {url}: {e}")

    return None