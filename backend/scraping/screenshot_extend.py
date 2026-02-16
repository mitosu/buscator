import subprocess
import os
import logging
import shutil
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Preferencias de Firefox para usar el proxy Tor SOCKS y modo automatizado
_FIREFOX_PREFS = """\
// Proxy Tor SOCKS
user_pref("network.proxy.type", 1);
user_pref("network.proxy.socks", "127.0.0.1");
user_pref("network.proxy.socks_port", 9050);
user_pref("network.proxy.socks_remote_dns", true);
user_pref("network.proxy.no_proxies_on", "");
// Anti-fingerprinting (simula comportamiento de Tor Browser)
user_pref("privacy.resistFingerprinting", true);
user_pref("privacy.trackingprotection.enabled", true);
user_pref("webgl.disabled", true);
user_pref("media.peerconnection.enabled", false);
user_pref("geo.enabled", false);
user_pref("intl.accept_languages", "en-US, en");
user_pref("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0");
user_pref("javascript.enabled", false);
// Modo automatizado
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("toolkit.startup.max_resumed_crashes", -1);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
"""

# Timeout en segundos para que Firefox renderice la página
_SCREENSHOT_TIMEOUT = 90


def _find_firefox():
    """
    Busca el ejecutable de Firefox en el sistema.
    Prioridad: variable de entorno > firefox-esr > firefox
    """
    env_path = os.environ.get("FIREFOX_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    for name in ["firefox-esr", "firefox"]:
        result = subprocess.run(
            ["which", name], capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()

    return None


def _capture_once(firefox_path, url, output_path):
    """
    Ejecuta Firefox en modo headless para capturar un screenshot.
    Crea un perfil temporal con las preferencias de proxy Tor.

    Returns:
        True si el screenshot se guardó correctamente, False en caso contrario
    """
    profile_dir = tempfile.mkdtemp(prefix="buscator_ff_")
    try:
        # Escribir preferencias de proxy en el perfil temporal
        with open(os.path.join(profile_dir, "user.js"), "w") as f:
            f.write(_FIREFOX_PREFS)

        cmd = [
            firefox_path,
            "--headless",
            "--screenshot", output_path,
            "--window-size=1280,960",
            "-profile", profile_dir,
            url,
        ]

        env = os.environ.copy()
        env["MOZ_CRASHREPORTER_DISABLE"] = "1"
        env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

        logger.info(f"Capturando screenshot de {url}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=_SCREENSHOT_TIMEOUT,
            env=env,
        )

        if result.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Screenshot guardado: {output_path}")
            return True

        stderr = result.stderr.decode(errors="replace")[:300]
        logger.warning(f"Firefox retornó código {result.returncode}: {stderr}")
        return False

    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout ({_SCREENSHOT_TIMEOUT}s) capturando {url}")
        return False
    except Exception as e:
        logger.error(f"Error capturando {url}: {e}")
        return False
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def capture_screenshot_with_tor_browser(url, output_path=None, max_retries=2):
    """
    Captura screenshot de un sitio .onion usando Firefox headless
    con el proxy SOCKS del daemon Tor (127.0.0.1:9050).

    Args:
        url: URL del sitio .onion
        output_path: Ruta donde guardar la captura (opcional)
        max_retries: Número máximo de intentos

    Returns:
        str: Ruta al screenshot si fue exitoso, None si falló
    """
    firefox_path = _find_firefox()
    if not firefox_path:
        logger.error(
            "No se encontró Firefox. Instala firefox-esr: sudo apt install -y firefox-esr"
        )
        return None

    if not output_path:
        domain = url.replace("http://", "").replace("https://", "").split("/")[0]
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        output_path = os.path.join(screenshots_dir, f"{domain}.png")

    for attempt in range(1, max_retries + 1):
        logger.info(f"Intento {attempt}/{max_retries} para {url}")
        if _capture_once(firefox_path, url, output_path):
            return output_path
        logger.warning(f"Intento {attempt} fallido para {url}")

    logger.error(f"Todos los intentos fallaron para {url}")
    return None
