import subprocess
import time
import os
import signal
import logging
import sys
import glob
import tempfile
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Preferencias para suprimir diálogos en modo automatizado
_TOR_BROWSER_PREFS = {
    # Desactivar restauración de sesión tras cierre forzoso
    "browser.sessionstore.resume_from_crash": "false",
    "toolkit.startup.max_resumed_crashes": "-1",
    # Desactivar prompts de idioma/localización
    "intl.locale.requested": '"en-US"',
    "privacy.spoof_english": "2",
    # Desactivar otros diálogos
    "browser.shell.checkDefaultBrowser": "false",
    "browser.startup.homepage_override.mstone": '"ignore"',
    "browser.rights.3.shown": "true",
    "browser.download.panel.shown": "true",
    "extensions.torlauncher.prompt_at_startup": "false",
    "app.update.enabled": "false",
}

class TorBrowserScreenshotter:
    def __init__(self, tor_browser_path=None):
        """
        Inicializa el capturador de screenshots para Tor Browser

        Args:
            tor_browser_path: Ruta al ejecutable de Tor Browser
        """
        # Prioridad: argumento > variable de entorno > detección automática
        env_path = os.environ.get("TOR_BROWSER_PATH")
        if tor_browser_path:
            self.tor_browser_path = tor_browser_path
        elif env_path:
            if not os.path.exists(env_path):
                raise FileNotFoundError(f"TOR_BROWSER_PATH apunta a una ruta inexistente: {env_path}")
            self.tor_browser_path = env_path
        else:
            # Rutas predeterminadas comunes de Tor Browser según OS
            if sys.platform.startswith('linux'):
                home = str(Path.home())
                possible_paths = [
                    f"{home}/.local/share/torbrowser/tbb/x86_64/tor-browser/Browser/start-tor-browser",
                    f"{home}/tor-browser/Browser/start-tor-browser",
                    f"{home}/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/start-tor-browser",
                    "/opt/tor-browser/Browser/start-tor-browser",
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
                raise FileNotFoundError(
                    "No se pudo encontrar Tor Browser automáticamente. "
                    "Configura la variable de entorno TOR_BROWSER_PATH con la ruta al ejecutable."
                )

        logger.info(f"Usando Tor Browser en: {self.tor_browser_path}")

        # Detectar directorio del perfil de Tor Browser
        self.profile_dir = self._find_profile_dir()

        # Directorio para guardar capturas temporales
        self.temp_dir = tempfile.gettempdir()

    def _find_profile_dir(self):
        """Localiza el directorio del perfil default de Tor Browser"""
        browser_dir = os.path.dirname(self.tor_browser_path)
        profile_dir = os.path.join(browser_dir, "TorBrowser", "Data", "Browser", "profile.default")
        if os.path.isdir(profile_dir):
            logger.info(f"Perfil de Tor Browser encontrado: {profile_dir}")
            return profile_dir
        logger.warning(f"No se encontró el perfil en: {profile_dir}")
        return None

    def _prepare_profile(self):
        """
        Prepara el perfil de Tor Browser para uso automatizado:
        - Elimina archivos de sesión para evitar el diálogo de recuperación
        - Escribe preferencias en user.js para suprimir prompts
        """
        if not self.profile_dir:
            return

        # Eliminar archivos de sesión que provocan el diálogo de recuperación
        session_files = [
            os.path.join(self.profile_dir, "sessionstore.jsonlz4"),
            os.path.join(self.profile_dir, "sessionstore.json"),
            os.path.join(self.profile_dir, ".parentlock"),
            os.path.join(self.profile_dir, "lock"),
        ]
        session_backup_dir = os.path.join(self.profile_dir, "sessionstore-backups")

        for f in session_files:
            if os.path.exists(f):
                os.remove(f)
                logger.info(f"Eliminado archivo de sesión: {f}")

        if os.path.isdir(session_backup_dir):
            for f in glob.glob(os.path.join(session_backup_dir, "*")):
                os.remove(f)
            logger.info("Limpiados backups de sesión")

        # Escribir preferencias en user.js
        user_js_path = os.path.join(self.profile_dir, "user.js")
        lines = []
        for key, value in _TOR_BROWSER_PREFS.items():
            lines.append(f'user_pref("{key}", {value});')

        with open(user_js_path, "w") as f:
            f.write("\n".join(lines) + "\n")
        logger.info("Preferencias escritas en user.js")
    
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

    @staticmethod
    def _kill_residual_tor_processes():
        """Mata procesos residuales de Tor Browser de ejecuciones anteriores"""
        try:
            subprocess.run(
                ["pkill", "-f", "firefox.real.*-no-remote"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            subprocess.run(
                ["pkill", "-f", "start-tor-browser"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            time.sleep(2)  # Esperar a que los procesos terminen y liberen archivos
        except Exception as e:
            logger.warning(f"Error limpiando procesos residuales: {e}")

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
            # Matar procesos residuales y preparar perfil limpio
            self._kill_residual_tor_processes()
            self._prepare_profile()

            # Crear directorio para la captura si no existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Iniciar Xvfb (servidor X virtual)
            display = f":{display_num}"
            xvfb_cmd = ["Xvfb", display, "-screen", "0", "1280x1024x24"]
            logger.info(f"Iniciando Xvfb en display {display}")
            xvfb_process = subprocess.Popen(xvfb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)

            # Entorno con display virtual y crash reporter desactivado
            env = os.environ.copy()
            env["DISPLAY"] = display
            env["MOZ_CRASHREPORTER_DISABLE"] = "1"
            env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

            # Argumentos para Tor Browser
            browser_args = [
                self.tor_browser_path,
                "--connect",
                "--new-instance",
                "--wait-for-browser",
                "-width", "1280",
                "-height", "960",
                "-no-remote",
                "-url", onion_url
            ]

            if sys.platform.startswith('linux') and self.tor_browser_path.endswith('start-tor-browser'):
                logger.info(f"Iniciando Tor Browser: {onion_url}")
                tor_process = subprocess.Popen(
                    browser_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
            else:
                logger.info(f"Iniciando Tor Browser con ejecutable: {self.tor_browser_path}")
                env["TOR_SKIP_LAUNCH"] = "1"
                env["TOR_BROWSER_SKIP_LAUNCH"] = "1"
                tor_process = subprocess.Popen(
                    browser_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )

            # Esperar a que Tor Browser cargue el sitio
            logger.info(f"Esperando {wait_time}s para carga de {onion_url}...")
            time.sleep(wait_time)

            # Tomar screenshot en el display virtual (mismo env que Tor Browser)
            screenshot_cmd = ["scrot", "-z", output_path]
            logger.info(f"Tomando screenshot en display {display}")
            result = subprocess.run(
                screenshot_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

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
            time.sleep(1)  # Esperar a que los archivos de sesión se liberen

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
            screenshots_dir = "screenshots"
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