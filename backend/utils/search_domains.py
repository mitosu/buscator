import requests
from bs4 import BeautifulSoup
import random

def get_surface_domains(tematicas):
    """
    Busca automáticamente entre 10 y 15 dominios en la Surface Web basándose en las temáticas.
    Utiliza Bing o Google para obtener dominios relacionados.
    """
    search_engine_url = "https://www.bing.com/search?q="
    user_agent = {"User-Agent": "Mozilla/5.0"}

    all_domains = []

    for tema in tematicas:
        query = f"{tema} site:.com OR site:.net OR site:.org"
        response = requests.get(search_engine_url + query, headers=user_agent)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = [a["href"] for a in soup.find_all("a", href=True) if "http" in a["href"]]

            # Filtrar y limpiar resultados
            filtered_domains = list(set([link.split("/")[2] for link in links if "bing" not in link]))

            all_domains.extend(filtered_domains)

    return random.sample(all_domains, min(len(all_domains), 15))  # Retorna 10-15 dominios


def get_deepweb_domains(tematicas):
    """
    Busca automáticamente entre 10 y 15 dominios en la Deep Web usando Ahmia con base en las temáticas.
    """
    base_url = "https://ahmia.fi/search/?q="
    user_agent = {"User-Agent": "Mozilla/5.0"}

    all_domains = []

    for tema in tematicas:
        query_url = f"{base_url}{tema}"
        try:
            response = requests.get(query_url, headers=user_agent)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                links = [a["href"] for a in soup.find_all("a", href=True) if ".onion" in a["href"]]
                
                # Filtrar duplicados y agregar a la lista general
                all_domains.extend(list(set(links)))

        except Exception as e:
            print(f"Error obteniendo dominios .onion para {tema}: {e}")

    return random.sample(all_domains, min(len(all_domains), 15))  # Retorna 10-15 dominios