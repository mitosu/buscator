import subprocess
import time
import os
import signal
import logging
import sys
import tempfile
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TorBrowserScreenshotter:
    def __init__(self, tor_browser_path=None):
        """
        Inicializa el capturador de screenshots para Tor Browser
        
        Args:
            tor_browser_path: Ruta al ejecutable de Tor Browser
        """
        if tor_browser_path:
            self.tor_browser_path = tor_browser_path
        else:
            # Rutas predeterminadas comunes de Tor Browser según OS
            if sys.platform.startswith('linux'):
                home = str(Path.home())
                possible_paths = [
                    f"{home}/tor-browser/Browser/start-tor-browser",
                    f"{home}/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/start-tor-browser",
                    "/opt/tor-browser/Browser/start-tor-browser"
                ]
            elif sys.platform.startswith('darwin'):  # macOS
                possible_paths = [
                    "/Applications/Tor Browser.app/Contents/MacOS/firefox",
                    f"{str(Path.home())}/Applications/Tor Browser.app/Contents/MacOS/firefox"
                ]
            elif sys.platform.startswith('win'):  # Windows
                possible_paths = [
                    r"C:\Program Files\Tor Browser\Browser\firefox.exe",
                    rf"{os.environ.get('USERPROFILE', '')}\Desktop\Tor Browser\Browser\firefox.exe"
                ]
            else:
                raise OSError(f"Sistema operativo no soportado: {sys.platform}")
            
            # Buscar el ejecutable en las rutas posibles
            self.tor_browser_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.tor_browser_path = path
                    break
            
            if not self.tor_browser_path:
                raise FileNotFoundError("No se pudo encontrar la ruta a Tor Browser automáticamente.")
        
        logger.info(f"Usando Tor Browser en: {self.tor_browser_path}")
        
        # Directorio para guardar capturas temporales
        self.temp_dir = tempfile.gettempdir()
    
    def _kill_process(self, process):
        """Mata un proceso y espera a que termine"""
        try:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        except Exception as e:
            logger.error(f"Error al terminar proceso: {str(e)}")
    
    def capture_onion_site(self, onion_url, output_path, wait_time=45, display_num=99):
        """
        Captura screenshot de un sitio .onion usando Tor Browser
        
        Args:
            onion_url: URL del sitio .onion
            output_path: Ruta donde guardar la captura
            wait_time: Tiempo de espera para carga del sitio (segundos)
            display_num: Número de display para Xvfb
        
        Returns:
            bool: True si la captura fue exitosa, False en caso contrario
        """
        xvfb_process = None
        tor_process = None
        
        try:
            # Crear directorio para la captura si no existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Iniciar Xvfb (servidor X virtual)
            display = f":{display_num}"
            xvfb_cmd = ["Xvfb", display, "-screen", "0", "1280x1024x24"]
            logger.info(f"Iniciando Xvfb: {' '.join(xvfb_cmd)}")
            xvfb_process = subprocess.Popen(xvfb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)  # Dar tiempo a Xvfb para iniciar
            
            # Configurar variable de entorno DISPLAY
            os.environ["DISPLAY"] = display
            
            # Argumentos para Tor Browser
            browser_args = [
                self.tor_browser_path,
                "--new-instance",
                "--wait-for-browser",
                "-width", "1280",
                "-height", "960",
                "-no-remote",
                "-url", onion_url
            ]
            
            # Si es Linux, verificar si es start-tor-browser o firefox directamente
            if sys.platform.startswith('linux') and self.tor_browser_path.endswith('start-tor-browser'):
                logger.info(f"Iniciando Tor Browser con script: {self.tor_browser_path}")
                tor_process = subprocess.Popen(browser_args, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE,
                                            env=os.environ.copy())
            else:
                # Para macOS, Windows o si apunta directamente a firefox
                logger.info(f"Iniciando Tor Browser con ejecutable: {self.tor_browser_path}")
                tor_env = os.environ.copy()
                tor_env["TOR_SKIP_LAUNCH"] = "1"  # Usar Tor existente si está en ejecución
                tor_env["TOR_BROWSER_SKIP_LAUNCH"] = "1"
                tor_process = subprocess.Popen(browser_args, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE,
                                            env=tor_env)
            
            # Tiempo de espera para que Tor Browser se inicie y cargue el sitio
            logger.info(f"Esperando {wait_time} segundos para carga del sitio {onion_url}...")
            time.sleep(wait_time)
            
            # Tomar screenshot usando scrot
            screenshot_cmd = ["scrot", "-z", output_path]
            logger.info(f"Tomando screenshot: {' '.join(screenshot_cmd)}")
            result = subprocess.run(screenshot_cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                logger.error(f"Error al capturar screenshot: {result.stderr.decode()}")
                return False
            
            logger.info(f"Screenshot guardado en: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error durante captura: {str(e)}")
            return False
            
        finally:
            # Limpiar procesos
            self._kill_process(tor_process)
            self._kill_process(xvfb_process)

    def capture_with_retries(self, onion_url, output_path, max_retries=3, 
                            base_wait_time=45, backoff_factor=1.5):
        """
        Intenta capturar el sitio con múltiples reintentos y espera exponencial
        
        Args:
            onion_url: URL del sitio .onion
            output_path: Ruta donde guardar la captura
            max_retries: Número máximo de intentos
            base_wait_time: Tiempo base de espera (segundos)
            backoff_factor: Factor de incremento para tiempos de espera
        
        Returns:
            str: Ruta al screenshot si fue exitoso, None si falló
        """
        wait_time = base_wait_time
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Intento {attempt}/{max_retries} para {onion_url}")
            
            success = self.capture_onion_site(
                onion_url=onion_url,
                output_path=output_path,
                wait_time=wait_time,
                display_num=99 + attempt  # Usar diferentes displays para cada intento
            )
            
            if success:
                logger.info(f"Captura exitosa en intento {attempt}")
                return output_path
            
            # Aumentar tiempo de espera para el próximo intento
            wait_time = int(wait_time * backoff_factor)
            logger.info(f"Aumentando tiempo de espera a {wait_time} segundos para próximo intento")
            
            # Esperar entre intentos
            time.sleep(5)
        
        logger.error(f"Todos los intentos fallaron para {onion_url}")
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