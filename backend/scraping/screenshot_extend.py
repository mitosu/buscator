import subprocess
import time
import os
import logging
import sys
import tempfile
import pyautogui
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TorBrowserScreenshotter:
    def __init__(self, tor_browser_path=None):
        """
        Inicializa el capturador de screenshots para Tor Browser.
        """
        if tor_browser_path:
            self.tor_browser_path = tor_browser_path
        else:
            if sys.platform.startswith('linux'):
                possible_paths = [
                    "/usr/bin/torbrowser-launcher",
                    "/usr/sbin/tor",
                    "/usr/bin/tor",
                    "/usr/local/bin/tor",
                    "/opt/tor-browser/Browser/start-tor-browser",
                    str(Path.home()) + "/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/start-tor-browser"
                ]
            else:
                raise OSError(f"Sistema operativo no soportado: {sys.platform}")

            # Buscar el ejecutable en las rutas posibles
            self.tor_browser_path = next((path for path in possible_paths if os.path.exists(path)), None)
            
            if not self.tor_browser_path:
                raise FileNotFoundError("No se pudo encontrar la ruta a Tor Browser automáticamente.")
        
        logger.info(f"Usando Tor Browser en: {self.tor_browser_path}")
        self.temp_dir = tempfile.gettempdir()

    def _kill_process(self, process_name):
        """Mata un proceso específico, **excepto el navegador frontend**."""
        try:
            # Evitar cerrar el navegador del frontend (Firefox o Chrome)
            if process_name in ["firefox", "chrome", "chromium"]:
                logger.info(f"🛑 No se cierra el proceso {process_name} para evitar afectar el frontend.")
                return
            
            subprocess.run(["pkill", "-f", process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"🔪 Proceso {process_name} terminado.")
        except Exception as e:
            logger.error(f"⚠ Error al matar proceso {process_name}: {str(e)}")

    def _get_display(self):
        """Obtiene el DISPLAY en el que está corriendo Xvfb correctamente."""
        try:
            output = subprocess.run(["pgrep", "-a", "Xvfb"], capture_output=True, text=True).stdout
            for line in output.splitlines():
                if "Xvfb" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith(":"):
                            return part  # Devuelve el DISPLAY correcto (ejemplo: ":99")
        except Exception:
            pass
        return ":99"  # Valor por defecto si no se encuentra otro

    def capture_onion_site(self, onion_url, output_path, wait_time=60):
        """
        Captura screenshot de un sitio .onion usando Tor Browser.
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 🔹 Obtener el DISPLAY correcto
            display = self._get_display()
            os.environ["DISPLAY"] = display
            logger.info(f"📺 Usando DISPLAY: {display}")

            # 🔹 Eliminar solo procesos específicos de **Tor Browser**, NO del frontend
            self._kill_process("torbrowser-launcher")
            self._kill_process("start-tor-browser")

            # 🔹 Iniciar Xvfb si no está en ejecución
            if subprocess.run(["pgrep", "-x", "Xvfb"], capture_output=True).returncode != 0:
                logger.info(f"🖥 Iniciando Xvfb en {display}...")
                subprocess.Popen(["Xvfb", display, "-screen", "0", "1280x1024x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)

            # 🔹 Iniciar Tor Browser en el DISPLAY correcto
            browser_args = [
                self.tor_browser_path,
                "--connect",  
                "--new-instance",
                "--wait-for-browser",
                "-width", "1280",
                "-height", "960",
                "-no-remote",
                onion_url
            ]
            logger.info(f"🌍 Iniciando Tor Browser en {display} con: {' '.join(browser_args)}")
            tor_process = subprocess.Popen(browser_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())

            # 🔹 Esperar a que el navegador abra
            logger.info("⌛ Esperando 10 segundos para que Tor Browser se abra...")
            time.sleep(10)

            # 🔹 Simular entrada del usuario con `pyautogui`
            try:
                logger.info("⌨ Simulando entrada de URL en Tor Browser con pyautogui...")
                os.environ["DISPLAY"] = display  # Asegurar que `pyautogui` usa el DISPLAY correcto

                # Enviar CTRL+L para enfocar la barra de direcciones
                pyautogui.hotkey("ctrl", "l")
                time.sleep(2)

                # Escribir la URL del sitio .onion
                pyautogui.typewrite(onion_url)
                time.sleep(2)

                # Presionar ENTER para navegar al sitio
                pyautogui.press("enter")
                time.sleep(60)  # Esperar 60 segundos para que el sitio cargue

            except Exception as e:
                logger.error(f"❌ Error en simulación de entrada con pyautogui: {str(e)}")

            # 🔹 Esperar a que el sitio cargue
            logger.info(f"⌛ Esperando {wait_time} segundos para que el sitio cargue...")
            time.sleep(wait_time)

            # 🔹 Verificar en qué DISPLAY se ejecuta realmente Tor Browser
            tor_display = os.environ.get("DISPLAY")  
            #system_display = subprocess.run(["printenv", "DISPLAY"], capture_output=True, text=True, shell=True).stdout.strip()
            #logger.info(f"🔍 DISPLAY detectado en terminal (printenv): {system_display}")
            
            logger.info("⚠️ DISPLAY real vacío, forzando a :99")
            system_display = ":99"
            # Si el DISPLAY real sigue vacío, forzamos el DISPLAY correcto
            #if not system_display:
            #    logger.info("⚠️ DISPLAY real vacío, forzando a :99")
            #    system_display = ":99"

            os.environ["DISPLAY"] = system_display

            # 🔹 Si `Tor Browser` está en otro DISPLAY, actualizar antes de capturar
            if system_display and system_display != tor_display:
                logger.info(f"⚠ Corrigiendo DISPLAY para captura: {system_display}")
                os.environ["DISPLAY"] = system_display

            # 🔹 Tomar screenshot asegurando que `scrot` use el mismo DISPLAY
            screenshot_cmd = ["env", f"DISPLAY={os.environ['DISPLAY']}", "scrot", "-z", output_path]
            logger.info(f"📸 Capturando con: {' '.join(screenshot_cmd)}")
            result = subprocess.run(screenshot_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                logger.error(f"❌ Error al capturar screenshot: {result.stderr.decode()}")
                return False

            logger.info(f"✅ Screenshot guardado en: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error durante captura: {str(e)}")
            return False

    def capture_with_retries(self, onion_url, output_path, max_retries=3, base_wait_time=45):
        """
        Intenta capturar el sitio con múltiples reintentos y espera exponencial.
        """
        wait_time = base_wait_time
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Intento {attempt}/{max_retries} para {onion_url}")

            if self.capture_onion_site(onion_url, output_path, wait_time):
                logger.info(f"✅ Captura exitosa en intento {attempt}")
                return output_path

            wait_time += 15
            logger.info(f"⏳ Aumentando tiempo de espera a {wait_time} segundos para el próximo intento")
            time.sleep(5)

        logger.error(f"❌ Todos los intentos fallaron para {onion_url}")
        return None
    
    # Función adaptada para ser compatible con tu implementación actual
def capture_screenshot_with_tor_browser(url, output_path=None, max_retries=2):
    """
    Función compatible que captura screenshots usando Tor Browser
    
    Args:
        url: URL del sitio .onion
        output_path: Ruta donde guardar la captura (opcional)
        max_retries: Número máximo de intentos
        
    Returns:
        str: Ruta al screenshot si fue exitoso, None si falló
    """
    try:
        # Generar nombre de archivo basado en la URL si no se proporciona
        if not output_path:
            # Extraer dominio para el nombre del archivo
            domain = url.replace("http://", "").replace("https://", "").split("/")[0]
            screenshots_dir = os.path.join("static", "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            output_path = os.path.join(screenshots_dir, f"{domain}.png")
        
        # Inicializar el screenshotter
        screenshotter = TorBrowserScreenshotter()
        
        # Capturar con reintentos
        result_path = screenshotter.capture_with_retries(
            onion_url=url,
            output_path=output_path,
            max_retries=max_retries,
            base_wait_time=30
        )
        
        return result_path
    
    except Exception as e:
        logger.error(f"Error al capturar screenshot de {url}: {str(e)}")
        return None