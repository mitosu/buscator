import requests
from bs4 import BeautifulSoup
import random

TOR_SEARCH_ENGINES = [
    "juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=",
    "tornetupfu7gcgidt33ftnungxzyfq2pygui5qdoyss34xbgx2qruzid.onion/search?q=",
    "2fd6cemt4gmccflhm6imvdfvli3nf7zn6rfrwpsy7uhxrgbypvwf5fad.onion/search?query=",
    "darkhuntxyxutk3cda4eogyvbcdcmsijv4i2dwtkfoeb6ggwzz7ke3qd.onion/search?q=",
    "3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search?q=",
    "venusosejno7oie4c73vsvrdw5k5gyhrhmq3apovwvy3qihub2dfppad.onion/Search?Query=",
    "thedude75pphneo4auknyvspskdmcj4xicbsnkvqgwhb4sfnmubkl5qd.onion/?query=",
    "ondexh46xin5wsjsz44b3jqucd4ytzz5l7pbcfpmzm5ejamfnol7mpyd.onion/search.htm?query=",
    "matesea7myfqb62sbjtpx3dfchalnpf2b4ppw52lzuxwvlbtj2kb3nqd.onion/?s=",
    "searchgf7gdtauh7bhnbyed4ivxqmuoat3nm6zfrg3ymkq6mtnpye3ad.onion/search?q="
]

TOR_PROXY = "socks5h://127.0.0.1:9050"


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
    Busca automáticamente entre 10 y 15 dominios en la Deep Web usando múltiples buscadores Tor.
    """
    user_agent = {"User-Agent": "Mozilla/5.0"}
    all_domains = set()

    for tema in tematicas:
        for search_engine in TOR_SEARCH_ENGINES:
            query_url = f"http://{search_engine}{tema}"
            print(f"Query URL ejecutada: {query_url}")
            try:
                response = requests.get(query_url, headers=user_agent, proxies={"http": TOR_PROXY}, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    links = {a["href"] for a in soup.find_all("a", href=True) if ".onion" in a["href"]}
                    
                    all_domains.update(links)
                    
                    if len(all_domains) >= 10:
                        break  # Si ya tenemos 10 o más dominios, paramos la búsqueda

            except Exception as e:
                print(f"Error obteniendo dominios .onion desde {search_engine}: {e}")
                continue  # Pasar al siguiente buscador si falla
        
        if len(all_domains) >= 10:
            break  # Si ya tenemos 10 dominios, no seguimos buscando

    print(f"Total de dominios obtenidos: {len(all_domains)}")
    return random.sample(all_domains, min(len(all_domains), 15))  # Retorna 10-15 dominios