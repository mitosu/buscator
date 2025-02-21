import os
import requests
from PIL import Image
from io import BytesIO

def ensure_http(url):
    """
    Asegura que la URL tenga 'http://' o 'https://'.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url  # Asumimos HTTPS por defecto
    return url

def capture_screenshot(url, output_folder="screenshots"):
    """
    Captura una imagen de la página principal del sitio web usando Thum.io.
    """
    url = ensure_http(url)  # Asegurar que la URL es válida
    os.makedirs(output_folder, exist_ok=True)

    # API de Thum.io para capturas de pantalla
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