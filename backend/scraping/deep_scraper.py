import requests

def ensure_http(url):
    """
    Asegura que la URL tenga 'http://'.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        return "http://" + url  # Para Deep Web, aseguramos HTTP (Tor no usa HTTPS)
    return url

def scrape_deep(domains, tematicas):
    """
    Realiza scraping en sitios de la Deep Web.
    """
    results = []
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Referer": "https://ahmia.fi",  # Usamos Ahmia como referencia porque es el buscador de la Deep Web
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }

    for domain in domains:
        domain = ensure_http(domain)  # Agregar esquema si falta
        try:
            response = requests.get(domain, proxies=proxies, timeout=15, headers=headers)
            response.raise_for_status()

            title = "No title"
            description = "No description"

            if "<title>" in response.text:
                title = response.text.split("<title>")[1].split("</title>")[0]

            if 'name="description"' in response.text:
                description = response.text.split('name="description" content="')[1].split('"')[0]

            for tema in tematicas:
                if tema.lower() in title.lower() or tema.lower() in description.lower():
                    results.append({
                        "domain": domain,
                        "title": title,
                        "description": description
                    })
                    break

        except requests.exceptions.HTTPError as e:
            print(f"Error en {domain}: {e}")
        except Exception as e:
            print(f"Error general en {domain}: {e}")

    print(f"Scraping Deep Web completado: {len(results)} resultados encontrados.")
    return results